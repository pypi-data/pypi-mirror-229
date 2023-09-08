import os
import sys
sys.path.append(os.getcwd())
from query_expansion import *
import unittest

class QueryTest(unittest.TestCase):
    def test_generate_expanded_queries(self):
        user_query="fashion designer in paris"
        expanded_queries=generate_expanded_queries(user_query,5)
        print(expanded_queries)
        self.assertEqual(6, len(expanded_queries))

    def test_generate_expanded_queries_original(self):
        user_query = "data scientist in london"
        expanded_queries = generate_expanded_queries(user_query, 3)
        self.assertIn(user_query, expanded_queries)

    def test_generate_expanded_queries_unique(self):
        user_query = "civil engineer in berlin"
        expanded_queries = generate_expanded_queries(user_query, 4)
        self.assertEqual(len(expanded_queries), len(set(expanded_queries)))


if __name__ =='__main__':
    unittest.main()
