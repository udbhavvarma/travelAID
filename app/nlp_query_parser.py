
import groq
import os
from dotenv import load_dotenv
from groq import Groq
import json
import re
from flask import jsonify


# Load environment variables
load_dotenv()

# Set the OpenAI API key
groq.api_key = os.getenv("GROQ_API_KEY")

def create_prompt(query):
    """
    Generates a prompt for the LLM with examples for query parsing.
    """
    return f"""
You are a helpful assistant that diverts search parameters from natural language queries.

We have 3 different types of entities: hotels, flights, and restaurants. You need to divert information regarding each of them to their specific handlers.


IMPORTANT NOTES:
1. MAKE SURE YOU EXTRACT THE ATTRIBUTES CORRECTLY IN JSON SERIALIZABLE FORMAT!! ALWAYS COMPLETE THE CURLY BRACES!
2. USE DOUBLE QUOTES!!!
3. NEVER GIVE ANY THING OUTSIDE CURLY BRACES! JUST RETURN THE JSON! THAT'S IT! NO HELPING WORDS!
4. WE ONLY SERVE INDIAN MAJOR CITIES FROM {{Chennai Delhi Hyderabad Kolkata Mumbai Bangalore Ahmedabad Jaipur Pune Bhubaneswar Goa Chandigarh}}. OTHER CITIES/PLACES ARE OUT OF SCOPE.
5. IF THERE IS A SPECIFIC SOURCE MENTIONED, ONLY THEN INCLUDE IT IN THE QUERY. OTHERWISE, IGNORE IT.


Here are some examples:
Construct them correctly.

1. Query: "Find hotels in Delhi near Connaught Place with 4-star rating with parking facility", pass the query verbatim ->
   {{"hotels":{{"query":"Find hotels in Delhi near Connaught Place with 4-star rating with parking facility"}}}}

2. Query: "Find top 20 hotels in Bangalore", pass the query verbatim:
   {{"hotels":{{"query": "Find top 20 hotels in Bangalore"}}}}   

   Query: "Show Air India flights from Delhi to Mumbai on 29th November using Goibibo" ->
    {{"flights": {{"query": "Show Air India flights from Delhi to Mumbai on 29th November", "source": "Goibibo"}}}}

Flights:
3. Query: "Show Air India flights from Delhi to Mumbai on 29th November" ->
   {{"flights": {{"query": "Show Air India flights from Delhi to Mumbai on 29th November"}}}}

   Query: "Show Air India flights from Delhi to Mumbai on 29th November using Goibibo" ->
    {{"flights": {{"query": "Show Air India flights from Delhi to Mumbai on 29th November", "source": "goibibodata"}}}}

   Query: "Show Air India flights from Delhi to Mumbai on 29th November using makemytrip" ->
    {{"flights": {{"query": "Show Air India flights from Delhi to Mumbai on 29th November", "source": "makemytripdata"}}}}

   Query: "Show Air India flights from Delhi to Mumbai on 29th November using booking.com" ->
    {{"flights": {{"query": "Show Air India flights from Delhi to Mumbai on 29th November", "source": "booking.com"}}}}

    Only include the source if it is mentioned in the query. Otherwise, dont mentio it.

Tourist spots have attributes such as type (restaurant, tourist_attraction), categories (like Italian, Mexican, Historical, Cultural), amenities (like parking, live music, etc.), and accessibility (like wheelchair_accessible, braille_menu, etc.)

4. Query: "Get restaurants in Mumbai around Bandra offering Italian and Mexican cuisines and have parking" ->
   {{"tourist_spots": {{"query": "Restaurants in Mumbai around Bandra locality having category Italian or Mexican cuisines and have parking facility"}}}}

   Query: "Give tourist attractions in Bangalore with wheelchair accessibility" ->
   {{"tourist_spots": {{"query": "Give tourist attractions in Bangalore with wheelchair accessibility and braille menu"}}}}


You can also be asked to handle an integrated query with multiple entities like:
Query: "Give flights from Delhi to Bangalore on 30 Dec 2024 (economy) and hotels in Bangalore for with a Doorman. Also give restaurants in Bangalore with Italian food"
Parameters: {{"flights": {{"query": "Flights from Delhi to Bangalore on 30 Dec 2024 economy class"}}, "hotels": {{"query": "Hotels in Bangalore that have Doorman facility}}, "tourist_spots": {{"query": "Restaurants in Bangalore with Italian category"}}}}
Note: Restaurants are a type WITHIN tourist_spots, not the top-level entity.


DO NOT RETURN ANY TEXT OUTSIDE THE CURLY BRACES.

IMP: CITIES OUTSIDE INDIA ARE OUT OF SCOPE.
IF YOU SEE THAT A QUERY IS OUT OF SCOPE (NOT SOMETHING WE CAN PROCESS), SIMPLY RETURN THE STRING "OUT OF SCOPE".

Now process this query:
Query: "{query}"
Parameters:
"""

def extract_parameters_with_llm(query):
    """
    Calls OpenAI's API to extract parameters from a natural language query.
    """
    prompt = create_prompt(query)
    
    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY"),
    )

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": prompt,
                }
            ],
            model="llama3-8b-8192",
        )

        print(chat_completion.choices[0].message.content)

        full_response = chat_completion.choices[0].message.content.strip()

        if "OUT OF SCOPE" in full_response:
            return "OUT OF SCOPE"
        else:
            match = re.search(r"\{.*\}", full_response, re.DOTALL)
            if match:
                structured_response = match.group(0)
                open_brackets = structured_response.count("{")
                close_brackets = structured_response.count("}")

                if open_brackets > close_brackets:
                    structured_response += "}" * (open_brackets - close_brackets)
                elif close_brackets > open_brackets:
                    structured_response = structured_response.rstrip("}")[:-(close_brackets - open_brackets)]

                try:
                    return json.loads(structured_response)
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON: {e}")
                    return None
            else:
                print("No JSON object found in response.")
                return None

            # return eval(structured_response)

    except Exception as e:
        print("Error with Llama LLM:", e)
        return
    
import json
import re

def fix_and_parse_response(full_response):
    """
    Extracts and parses JSON objects from a response. Ensures balanced brackets for valid JSON.

    Parameters:
        full_response (str): The raw response containing a potential JSON object.

    Returns:
        dict or None: Parsed JSON object if valid, None otherwise.
    """
    # Search for the first JSON-like object using regex
    match = re.search(r"\{.*\}", full_response, re.DOTALL)
    if not match:
        print("No JSON object found in response.")
        return None

    structured_response = match.group(0)

    # Count opening and closing brackets
    open_brackets = structured_response.count("{")
    close_brackets = structured_response.count("}")

    # Fix imbalance if necessary
    if open_brackets > close_brackets:
        # Add missing closing brackets
        structured_response += "}" * (open_brackets - close_brackets)
    elif close_brackets > open_brackets:
        # Remove excess closing brackets (from the end)
        structured_response = structured_response.rstrip("}")[:-(close_brackets - open_brackets)]

    # Try parsing the fixed JSON object
    try:
        return json.loads(structured_response)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return None


def handle_out_of_scope_query(query):

    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY"),
    )

    """
    Use LLM to handle out-of-scope queries.
    """
    prompt = f"""
    You are a helpful travel assistant. Answer the following query in a concise and user-friendly manner:
    Query: {query}
    """
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": prompt,
                }
            ],
            model="llama3-8b-8192",
        )

        response = chat_completion.choices[0].message.content.strip()
        return jsonify({"out_of_scope_response": response})
    
    except Exception as e:
        print("Error with Handler LLM:", e)
        return "I'm sorry, I couldn't process your query at this time."
