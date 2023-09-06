import os
import openai
from typing import List

# Openai API key
os.environ["OPENAI_API_KEY"] = "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"

# Openai API key 
openai.api_key = "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"

# generate a set of queries similar to the original
def generate_expanded_queries(query: str, num_queries: int = 5) -> List[str]:
    prompt = (
        f"Given a user's search query, generate a list of {num_queries} similar queries that are relevant to the original context [similar job title, nearby location, similar skills].\n\n"
        "Examples:\n"
        "1. Input Query: \"Software engineer in New York\"\n"
        "   [\"Software Development Engineer in New York\", \"Software developer in New York\", \"SDE in Jersey City\" ]\n\n"
        "2. Input Query: \"Remote Data Scientist\"\n"
        "   [\"Remote Data Science Engineer\", \"Work from home Data Scientist\"]\n\n"
        "3. Input Query: \"Entry-level software developer\"\n"
        "   [\"Software engineering intern\", \"Junior software engineer\"]\n\n"
        "4. Input Query: \"Experienced software engineer\"\n"
        "   [\"Senior software engineer\", \"Software Architect\"]\n\n"
        "5. Input Query: \"Software development careers\"\n"
        "   [\"Software engineering job paths\", \"Career options in software development\"]\n\n"
        f"Input Query: \"{query}\"\n"
    )

    
    response = openai.Completion.create(
        engine="text-davinci-003",  
        prompt=prompt,
        max_tokens=100,
        stop=None,
        temperature=0.7,
        n=num_queries,
        frequency_penalty=0.5,
        presence_penalty=0.5
    )

    expanded_text = response.choices[0]['text']

    # Find the start index of the list
    result_list_start = expanded_text.index("[")  

    # Find the end index of the list
    result_list_end = expanded_text.index("]")  

    # extract the result
    result_list_str = expanded_text[result_list_start:result_list_end+1] 
    result_list = eval(result_list_str) 

    # add original query as well
    result_list.append(query)

    return result_list
