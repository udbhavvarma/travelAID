from flask import Flask, jsonify, request
import pymysql
import os
from groq import Groq
import re
from app.schema import mediated_schema
from dotenv import load_dotenv

load_dotenv()


app = Flask(__name__)


import pymysql

def query_mediated_schema(query, table_name):
    """
    Queries the mediated schema and returns unified results.
    """
    if table_name not in mediated_schema:
        raise ValueError(f"Table '{table_name}' not found in mediated schema.")

    table = mediated_schema[table_name]
    combined_results = []

    HOTELS_COLUMN_MAPPING = {

        "address": 0,
        "city": 1,
        "hotel_description": 2,
        "hotel_facilities": 3,
        "hotel_star_rating": 4,
        "property_id": 5,
        "property_name": 6,
        "room_count": 7,
        "room_type": 8,
        "site_review_rating": 9,
        "sitename": 10,
        "price": 11

    }


    def extract_order_by_and_limit(query):
        """
        Extracts the ORDER BY and LIMIT clauses from a query and removes them from the query.

        Returns:
            query_without_order_and_limit (str): The query without ORDER BY or LIMIT clauses.
            order_by_columns (list): List of tuples (column, direction) for sorting.
            limit_value (int or None): The LIMIT value if present.
        """
        # Initialize default values
        order_by_columns = []
        limit_value = None

        # Handle LIMIT first
        limit_match = re.search(r"LIMIT\s+(\d+)", query, re.IGNORECASE)
        if limit_match:
            limit_value = int(limit_match.group(1))
            query = query[:limit_match.start()].strip()  # Remove LIMIT from the query

        # Handle ORDER BY
        order_by_match = re.search(r"ORDER BY (.+)$", query, re.IGNORECASE)
        if order_by_match:
            order_by_clause = order_by_match.group(1).strip()
            query = query[:order_by_match.start()].strip()  # Remove ORDER BY from the query

            # Parse ORDER BY columns
            order_by_columns = [
                (col.strip().split()[0], col.strip().split()[1].upper() if len(col.strip().split()) > 1 else "ASC")
                for col in order_by_clause.split(",")
            ]

        # Debugging Logs
        print(f"Extracted Base Query: {query}")
        print(f"Extracted ORDER BY Columns: {order_by_columns}")
        print(f"Extracted LIMIT Value: {limit_value}")

        return query, order_by_columns, limit_value

    def sort_combined_results(results, order_by_columns, column_mapping):
        """
        Sorts the combined results based on the extracted ORDER BY columns.
        """
        for col, direction in reversed(order_by_columns):
            index = column_mapping.get(col)
            if index is None:
                raise ValueError(f"Invalid column '{col}' for sorting.")
            results.sort(key=lambda x: x[index], reverse=(direction == "DESC"))
        return results

    try:
        # Extract ORDER BY and LIMIT clauses
        query, order_by_columns, limit_value = extract_order_by_and_limit(query)
        print(query, order_by_columns, limit_value)

        for source in table["sources"]:
            host_name = source["host"]
            user_name = source["user"]
            password = source["password"]
            db_name = source["database"]
            table_name = source["table"]

            try:
                # Connect to the respective database
                connection = pymysql.connect(
                    host=host_name,
                    user=user_name,
                    password=password,
                    database=db_name
                )
                cursor = connection.cursor()
                cursor.execute(query)
                results = cursor.fetchall()
                combined_results.extend(results)
                cursor.close()
                connection.close()
                print(f"Queried {db_name}.{table_name} successfully.")
            except Exception as e:
                print(f"Error querying {db_name}.{table_name}: {e}")

        # Apply ORDER BY if specified
        if order_by_columns:
            combined_results = sort_combined_results(combined_results, order_by_columns, HOTELS_COLUMN_MAPPING)

        # Apply LIMIT if specified
        if limit_value is not None:
            combined_results = combined_results[:limit_value]

        return combined_results

    except Exception as e:
        print(f"Error querying mediated schema: {e}")
        return []


    
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
    )

def clean_query(query):
    """
    Cleans and validates an SQL query to avoid common syntax errors.
    Ensures anything before SELECT is removed.

    Parameters:
        query (str): The raw SQL query.

    Returns:
        str: The cleaned SQL query.
    """
    try:
        # Remove leading and trailing spaces
        query = query.strip()

        # Remove anything before the first occurrence of SELECT (case-insensitive)
        select_index = query.lower().find("select")
        if select_index != -1:
            query = query[select_index:]

        # Ensure single quotes for SQL string literals
        query = query.replace('“', "").replace('”', "").replace('"', "")

        # Remove enclosing quotes if the query is wrapped in extra quotes
        if query.startswith("'") and query.endswith("'"):
            query = query[1:-1]

        # Strip redundant whitespace
        query = " ".join(query.split())

        return query
    except Exception as e:
        raise ValueError(f"Error cleaning query: {e}")





def generate_hotels_query_with_llm(filters):
    """
    Generate a SQL query using an LLM for the Hotels table based on user-provided filters.
    """
    prompt = f"""
    You are an assistant designed to generate MySQL queries for a table of hotels in Indian cities named hotels.
    You are only supposed to generate a single query for a table

    PLEASE USE PARAMETERS EXPLICITLY MENTIONED IN THE QUERY. DO NOT USE COMPLICATED CLAUSES UNNECESSARILY.


    USE LIMIT WHEN THE USER ASKS FOR TOP-N RESULTS!!!!!!!!!! eg. top 5 hotels -> LIMIT 5


    address text (the address of the hotel)
    city text (the city where the hotel is located)
    country text (the country where the hotel is located)
    hotel_description text (a description of the hotel)
    hotel_facilities text (the facilities provided by the hotel)
    hotel_star_rating int (the star rating of the hotel)
    property_id int (the ID of the hotel)
    property_name text (the name of the hotel)
    room_count int (the number of rooms in the hotel)
    room_type text (the type of rooms available in the hotel)
    site_review_rating double (the rating of the hotel on the site)
    sitename text (the name of the site data was scraped from)
    state text (the state where the hotel is located)
    price int (the price of the hotel)

    Rules:
    1. You have to generate a simple query that fetches all columns from the table. Do not use complicated clauses unnecessarily.
    2. Reflect all filters provided in the input in the WHERE clause.
    3. Give a single queryt that can be executed straight away.
    4. Handle semantic similarity by handling difference in uppercase and lowercase entities and use LIKE operator with them. For example, 'Delhi' and 'delhi' should be treated as the same city. Booking.com and bookingcom should be treated as the same site.
    5. Make sure the query is syntactically correct and can be executed. Do not include unnecessary whitespaces and newlines.
    6. GIVE NOTHING OTHER THAN THE QUERY INSIDE THE DOUBLE QUOTES. JUST THE QUERY. NOTHING ELSE.

    Input Filters: {filters}

    """
    try:
        response = client.chat.completions.create(
            messages=[{"role": "system", "content": prompt}],
            model="llama3-8b-8192",
        )

        # Parse the LLM output
        output = response.choices[0].message.content.strip()
        query = clean_query(output)
        print(query)
        return query
    
    except Exception as e:
        print("Error generating query with LLM:", e)
        return None


@app.route('/hotels', methods=['GET'])
def get_hotels():
    filters = request.args.to_dict(flat=False)
    llm_query_response = generate_hotels_query_with_llm(filters)
    if not llm_query_response:
        return jsonify({"error": "Failed to generate queries"}), 500

    query = llm_query_response

    try:

        results = query_mediated_schema(query, "hotels")
        hotels_data = [
            {
                "address": row[0],
                "city": row[1],
                "hotel_description": row[2],
                "hotel_facilities": row[3],
                "hotel_star_rating": row[4],
                "property_name": row[6],
                "site_review_rating": row[9],
                "sitename": row[10],
                "price": row[11]

            } for row in results
        ]
        
        if filters.get("source"):
            site = filters["source"][0]
            filtered_data = [hotel for hotel in hotels_data if hotel["sitename"].lower() == site.lower()]
            return jsonify(filtered_data)
        
        else:
            return jsonify(hotels_data)


    except Exception as e:
        print("Error executing query:", e)
        return jsonify({"error": "Query execution failed"}), 500


if __name__ == '__main__':
    app.run(port=5002)
