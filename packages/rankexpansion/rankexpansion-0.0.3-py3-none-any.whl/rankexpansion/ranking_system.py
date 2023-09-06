from sentence_transformers import SentenceTransformer
from typing import List, Optional
from dataclasses import dataclass
# from libs.ai.search.search_classes import Candidate
from searchdatamodels import Candidate

import spacy

import os
import re
import openai

from geopy.geocoders import Nominatim
from geopy.distance import geodesic

import numpy as np 

import math 

# Initialize the geocoder
geolocator = Nominatim(user_agent="location_expansion")

# OpenAI API Key
os.environ["OPENAI_API_KEY"] = "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"

# Openai API key 
openai.api_key = "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"

# Load the Sentence Transformers model for text embedding
model = SentenceTransformer('paraphrase-MiniLM-L3-v2')

# Load spaCy's English language model
nlp_spacy = spacy.load("en_core_web_sm")


# Keep track of the number of times a candiate is recommended
# Key: Candidate Name (str) OR Candidate ID/UUID (str)
# Value: Recommendation Count (int)
recommendation_count = {}

# Keep track of the candidate scores
# Key: Candidate Name (str) OR Candidate ID/UUID (str)
# Value: Candidate Score (int)
score_tracker = {}

# Defunct since rank_score is not a field in Candidate
def rank_candidates(query: str, candidates: List[Candidate]) -> List[Candidate]:
    query_embedding = model.encode([query], convert_to_tensor=True)

    for candidate in candidates:
        # Use the Summary embedding for comparison
        candidate_embedding = candidate.Summary.Embedding  
        if candidate_embedding is not None:
            # similarity_score = util.pytorch_cos_sim(query_embedding, candidate_embedding)[0].item()
            # rank_score attribute should be addded to the candidate model
            similarity_score = util.cos_sim(query_embedding, candidate_embedding)[0].item()
            candidate.rank_score = similarity_score
        else:
            # Set a default score for candidates without embeddings
            candidate.rank_score = 0.0  

    ranked_candidates = sorted(candidates, key=lambda c: c.rank_score, reverse=True)
    return ranked_candidates

# Get the top ranked candidates
def get_top_candidates(query: str, candidates: List[Candidate], k: int) -> List[Candidate]:
    
    # Calculate total scores for each candidate
    scored_candidates = [(candidate, calculate_total_score(query, candidate)) for candidate in candidates]

    # Sort the candidates based on their scores in descending order
    scored_candidates.sort(key=lambda x: x[1], reverse=True)
    
    # Return the top k candidates
    return [candidate[0] for candidate in scored_candidates[:k]]


# Define helper functions for the weighting algorithm


# Location extraction to extract locations from the query
# spaCy has GPE tags
# However spacy cannot resolve location names in case of typos
def extract_location_mentions_spacy(query: str) -> List[str]:
    locations = []
    doc = nlp_spacy(query)
    for entity in doc.ents:
        # "GPE" represents geopolitical entities (locations)
        if entity.label_ == "GPE":  
            locations.append(entity.text)

    return locations


# Location extraction using openai
# This function can take care of typos
def extract_location_mentions_llm(query: str) -> List[str]:

    # prompt should be passed in as a parameter to this function
    prompt = (
        "You are a language model that can extract location mentions from queries. Please provide the list of locations mentioned in the following queries. Take care of typos\n\n" 
        "Examples:\n"
        "1. Query: \"Find me 3 candidates in New York City and Los Angles who are Software Engineers\"\n"
        "   Locations: [\"New York City\", \"Los Angeles\"]\n\n"
        "2. Query: \"I'm looking for candidates from London with programming skills\"\n"
        "   Locations: [\"London\"]\n\n"
        "3. Query: \"Search for profiles in San Francsco with marketing experience\"\n"
        "   Locations: [\"San Francisco\"]\n\n"
        f"Query: \"{query}\""
    )
    
    # Use the appropriate LLM model - the cheapest
    # Set the desired max tokens
    # Don't set any stop sequence
    response = openai.Completion.create(
        engine="text-davinci-003",  
        prompt=prompt,
        max_tokens=100,  
        stop=None  
    )

    # Extract the list of locations mentioned from the model's response
    output_lines = response.choices[0].text.strip().split("\n")
    extracted_locations = []
    for line in output_lines:
        if line.startswith("Locations: ["):
            locations_str = line.split(":")[1].strip()
            locations_list = [loc.strip('" ') for loc in locations_str.strip("[]").split(",")]
            extracted_locations.extend(locations_list)

    return extracted_locations


# Location expansion using geopy
def expand_locations(query_locations: List[str], max_distance_km: float = 100.0) -> List[str]:
    expanded_locations = []

    # Iterate through the query locations and find their coordinates
    for query_location in query_locations:
        location = geolocator.geocode(query_location)
        if location:
            query_coords = (location.latitude, location.longitude)

            # Find nearby locations within the specified distance
            nearby_locations = geolocator.reverse(query_coords, exactly_one=False)

            # Add the nearby locations within the specified distance to the expanded list
            for nearby_loc in nearby_locations:
                nearby_coords = (nearby_loc.latitude, nearby_loc.longitude)
                distance_km = geodesic(query_coords, nearby_coords).kilometers
                if distance_km <= max_distance_km:
                    expanded_locations.append(nearby_loc.address)

    return expanded_locations

# Location expansion using llm
def generate_expanded_locations(query_locations: List[str], max_distance_km: float = 100.0, max_limit: int = 5, include_state: bool = False) -> List[str]:
    expanded_locations = []

    # Generate expanded locations for each query location
    for query_location in query_locations:
        # Keep it simple so that we remain at city level granularity
        prompt = f"Given the query location '{query_location}', provide a list of major cities within {max_distance_km} km radius.\n\nList:"

        # Generate the expanded locations using the OpenAI API
        response = openai.Completion.create(
            engine="text-davinci-003",  
            prompt=prompt,
            max_tokens=50,  
            stop=None  
        )

        # Parse the generated response to extract the expanded locations
        expanded_locations_query = response.choices[0].text.strip().split("\n")[:max_limit]
        
        # Remove numbering from the generated locations
        expanded_locations_query = [re.sub(r'^\d+\.\s*', '', location) for location in expanded_locations_query]
        
        # Extract only the city name before the first comma
        if not include_state:
          expanded_locations_query = [location.split(',')[0].strip() for location in expanded_locations_query]

        expanded_locations.extend(expanded_locations_query)

    return expanded_locations


# Extract skills from the query
def extract_skills(query: str) -> List[str]:
    prompt = (
        f"You are a language model that can extract skills from queries. Please provide the list of skills mentioned in the following queries.\n\n"
        "Examples:\n"
        "1. Query: \"Looking for candidates with programming and data analysis skills\"\n"
        "   Skills: [\"programming\", \"data analysis\"]\n\n"
        "2. Query: \"Searching for profiles with communication and leadership abilities\"\n"
        "   Skills: [\"communication\", \"leadership\"]\n\n"
        "3. Query: \"Find candidates experienced in project management and teamwork\"\n"
        "   Skills: [\"project management\", \"teamwork\"]\n\n"
        f"Query: \"{query}\""
    )

    # Use the appropriate engine - cheapest preferred
    # max_tokens can be adjusted as needed
    response = openai.Completion.create(
        engine="text-davinci-003",  
        prompt=prompt,
        max_tokens=50,  
        stop=None  
    )

    extracted_text = response.choices[0].text
    start_index = extracted_text.find("[\"")
    end_index = extracted_text.find("\"]")
    extracted_skills = extracted_text[start_index + 2:end_index].split("\", \"")
    
    return extracted_skills
    

# Calculate the skill match score between the required skills and candidate skills
def calculate_skill_match_score(extracted_skills: List[str], candidate_skills: List[str]) -> float:

    # Calculate direct match score
    direct_match_score = len(set(extracted_skills).intersection(candidate_skills)) / len(extracted_skills)

    # Encode the skill lists into embeddings
    # model = SentenceTransformer('paraphrase-MiniLM-L3-v2')
    extracted_skills_embeddings = model.encode(extracted_skills, convert_to_tensor=True)
    candidate_skills_embeddings = model.encode(candidate_skills, convert_to_tensor=True)

    # Calculate cosine similarity between the skill embeddings
    expanded_match_scores = util.cos_sim(extracted_skills_embeddings, candidate_skills_embeddings)
   
    # Calculate the average cosine similarity
    avg_expanded_match_score = np.mean(expanded_match_scores.numpy())

    # Calculate total match score as a weighted sum of direct and expanded match scores
    # Weights can be modified
    total_match_score = 0.6 * direct_match_score + 0.4 * avg_expanded_match_score

    return total_match_score

    
# Calculate the location match score
def calculate_location_match_score(query_location: List[str], expanded_locations: List[str], candidate_location: str) -> float:

    # Initialize the geolocator
    geolocator = Nominatim(user_agent="location_match_score")
    
    # Get the coordinates of the candidate's location
    candidate_coords = geolocator.geocode(candidate_location) if candidate_location else None
    
    # Calculate direct match score
    direct_match_score = 1.0 if candidate_location in query_location else 0.0
    
    # Initialize closest_distance with a high value
    closest_distance = float("inf")
    
    # Calculate the closest distance between candidate location to expanded locations
    for expanded_loc in expanded_locations:
        expanded_coords = geolocator.geocode(expanded_loc)
        if expanded_coords and candidate_coords:
            distance = geodesic(candidate_coords.point, expanded_coords.point).kilometers
            closest_distance = min(closest_distance, distance)
    
    # Initialize expanded location score
    expanded_location_score = 0.0
    
    # Calculate expanded location score if candidate_coords is available and distance is within 300 km
    # the score decreases exponentially as we move away from the exact location,
    # and drops down to 0 after 300 km
    if candidate_coords and closest_distance <= 300.0:
        expanded_location_score = math.exp(-0.01 * closest_distance)
    
    # Calculate total score using a weighted combination of direct and expanded scores
    total_score = 0.7 * expanded_location_score + 0.3 * direct_match_score
    return total_score
    

# Calculate the extent of relevance between the query and a candidate's profile
def calculate_similarity_score(query: str, candidate: Candidate) -> float:
    if candidate.Summary.Embedding is None:
        # Encode the candidate's summary
        candidate_embedding = model.encode([candidate.Summary.Text], convert_to_tensor=True)[0]
        candidate.Summary.Embedding = candidate_embedding
    
    # Encode the query
    query_embedding = model.encode([query], convert_to_tensor=True)
    
    # Calculate the cosine similarity score between query and candidate embeddings
    similarity_score = util.cos_sim(query_embedding, candidate.Summary.Embedding).item()
    
    return similarity_score



# Final score calculation
def calculate_total_score(query: str, candidate: Candidate) -> float:
    # Calculate similarity score
    similarity_score = calculate_similarity_score(query, candidate)
    
    # Extract query locations and expanded locations
    # Include query_locations within query_expanded_locations as well
    query_locations = extract_location_mentions_spacy(query)
    query_expanded_locations = generate_expanded_locations(query_locations)
    
    # Calculate location match score
    location_match_score = calculate_location_match_score(query_locations, query_expanded_locations, candidate.Location)
    
    # Extract query skills
    query_skills = extract_skills(query)
    
    # Calculate skill match score
    skill_match_score = calculate_skill_match_score(query_skills, candidate.Skills)
    
    # Define weights for each component
    similarity_weight = 0.4
    location_weight = 0.3
    skill_weight = 0.3
    
    # Calculate total score
    # Weights can be adjusted
    # Include recommendation_count factor as well
    total_score = similarity_weight * similarity_score + location_weight * location_match_score + skill_weight * skill_match_score

    
    return total_score

