import requests
import json
import logging

BACKEND_APIS = {
    "flights": "http://localhost:5001/flights",
    "hotels": "http://localhost:5002/hotels",
    "tourist_spots": "http://localhost:5003/tourist_spots"
}

def is_query_in_scope(query):
    """
    Check if the query is within the scope of the federated search.
    """
    allowed_keywords = ["flights", "hotels", "tourist_spots"]
    return any(keyword in query for keyword in allowed_keywords)
        

def decompose_query(unified_query):
    """
    Decompose the unified query into subqueries for each data source.
    """
    subqueries = {}

    print("Unified Query:", unified_query)

    if "flights" in unified_query:
        subqueries["flights"] = unified_query["flights"]
        print("Flights Subquery:", subqueries["flights"])

    if "hotels" in unified_query:
        subqueries["hotels"] = unified_query["hotels"]

    if "tourist_spots" in unified_query:
        subqueries["tourist_spots"] = unified_query["tourist_spots"]

    return subqueries

def execute_subqueries(subqueries):
    """
    Execute subqueries for each data source and return results.
    """
    results = {}

    if "flights" in subqueries and subqueries["flights"]:
        flights_url = f"{BACKEND_APIS['flights']}?{subqueries['flights']}"
        try:
            results["flights"] = requests.get(
                BACKEND_APIS["flights"], params=subqueries["flights"]
            ).json()
        except Exception as e:
            print("Error executing Flights Subquery:", e)
            results["flights"] = []


    if "hotels" in subqueries and subqueries["hotels"]:
        print("Executing Hotels Subquery:", subqueries["hotels"])
        try:
            results["hotels"] = requests.get(
                BACKEND_APIS["hotels"], params=subqueries["hotels"]
            ).json()
        except Exception as e:
            print("Error executing Hotels Subquery:", e)
            results["hotels"] = []

    if "tourist_spots" in subqueries and subqueries["tourist_spots"]:
        print("Executing Tourist Spots Subquery:", subqueries["tourist_spots"])
        try:
            results["tourist_spots"] = requests.get(
                BACKEND_APIS["tourist_spots"], params=subqueries["tourist_spots"]
            ).json()
        except Exception as e:
            print("Error executing Tourist Spots Subquery:", e)
            results["tourist_spots"] = []

    return results



def aggregate_results(results):
    """
    Aggregate results from all data sources into a unified response.
    """
    unified_response = {
        "flights": results.get("flights", []),
        "hotels": results.get("hotels", []),
        "tourist_spots": results.get("tourist_spots", [])
    }
    return unified_response

logging.basicConfig(
    filename="query.log", 
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Log query function
def log_query(query, query_type, status, response_time):
    logging.info(
        f"Query: {query}, Type: {query_type}, Status: {status}, Response Time: {response_time} ms"
    )