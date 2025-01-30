from flask import Flask, jsonify, request
import pymysql
from datetime import timedelta
import os
from groq import Groq
from dotenv import load_dotenv
import re
from app.schema import mediated_schema
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)


def query_mediated_schema(query, table_name):
    """
    Queries the mediated schema and returns unified results.
    """
    if table_name not in mediated_schema:
        raise ValueError(f"Table '{table_name}' not found in mediated schema.")

    table = mediated_schema[table_name]
    combined_results = []

    FLIGHTS_COLUMN_MAPPINGS = {
        "flight_date": 0,
        "airline": 1,
        "flight_num": 2,
        "class": 3,
        "dep_city": 4,
        "dep_time": 5,
        "arr_city": 6,
        "arr_time": 7,
        "duration": 8,
        "price": 9,
        "stops": 10,
        "flight_id": 11,
        "sitename": 12
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
            combined_results = sort_combined_results(combined_results, order_by_columns, FLIGHTS_COLUMN_MAPPINGS)

        # Apply LIMIT if specified
        if limit_value is not None:
            combined_results = combined_results[:limit_value]

        return combined_results

    except Exception as e:
        print(f"Error querying mediated schema: {e}")
        return []

def format_time(value):
    """
    Format a time-like object (datetime.time or datetime.timedelta) to 'HH:MM'.
    """
    if isinstance(value, timedelta):
        total_seconds = int(value.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours:02}:{minutes:02}"
    elif hasattr(value, "strftime"):
        return value.strftime("%H:%M")
    return value



client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
    )

def clean_query(query):
    """
    Cleans and validates an SQL query to avoid common syntax errors.

    Parameters:
        query (str): The raw SQL query.

    Returns:
        str: The cleaned SQL query.
    """
    try:
        # Remove leading and trailing spaces
        query = query.strip()

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



def generate_flights_query_with_llm(filters):
    """
    Generate a SQL query using an LLM for the Hotels table based on user-provided filters.
    """
    prompt = f"""
    You are an assistant designed to generate MySQL queries for a table named flights.
    You are only supposed to generate a single query for the table

    GIVE SYNATACTICALLY CORRECT QUERY THAT CAN BE EXECUTED. DO NOT INCLUDE UNNECESSARY WHITESPACES AND NEWLINES.
    NEVER USE ILIKE OR RLIEK IN THE QUERY. USE LIKE ONLY.

    PLEASE USE PARAMETERS EXPLICITLY MENTIONED IN THE QUERY. DO NOT USE COMPLICATED CLAUSES UNNECESSARILY.

    USE LIMIT WHEN THE USER ASKS FOR TOP-N RESULTS!!!!!!!!!! eg. top 5 flights -> LIMIT 5

 
    Table: flights
    Columns (including that have some definite discrete values): flight_date, airline, flight_num, class (economy, business discrete values), dep_city, dep_time, arr_city, arr_time, duration, price, stops (non-stop, 1-stop, 2+-stop discrete values), flight_id, sitename (USE WHEN MENTIONED 'source' IS MENTIONED EXPLICITLY : LIKE '%booking.com%' or LIKE '%goibibo.com%' or LIKE '%makemytrip.com%')

    Rules:
    Most Imp: Use standard Mysql syntax. Do not use things such as ILIKE that are not supported in MySQL.
    Take care of ordering of the results.
    If the query has 1-stop, do "LIKE '%1-stop%'" in the query as the name of stop might be included in data which is not there in query.
    1. You have to generate a simple query that fetches all columns from the table. Do not use complicated clauses unnecessarily.
    2. Reflect all filters provided in the input in the WHERE clause and handle the ORDER BY clause if necessary (eg. cheapest hotels in bangalore with 4 star rating -> ORDER BY price ASC).
    3. Give a single query that can be executed straight away.
    4. Handle semantic similarity by handling difference in uppercase and lowercase entities. For example, 'Delhi' and 'delhi', 'Economy' and 'economy' should be treated as the same city.
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


@app.route('/flights', methods=['GET'])
def get_flights():

    filters = request.args.to_dict(flat=False)
    llm_query_response = generate_flights_query_with_llm(filters)
    if not llm_query_response:
        return jsonify({"error": "Failed to generate query"}), 500

    query = llm_query_response

    try:

        rows = query_mediated_schema(query, "flights")
        flights_data = [
            {
                "flight_date": row[0],
                "airline": row[1],
                "flight_num": row[2],
                "class": row[3],
                "departure": row[4],
                "dep_time": format_time(row[5]),
                "arrival": row[6],
                "arr_time": format_time(row[7]),
                "duration": row[8],
                "price": row[9],
                "stops": row[10],
                "flight_id": row[11],
                "sitename": row[12]
            }
            for row in rows
        ]

        print(f"Number of Flights: {len(flights_data)}")
        return jsonify(flights_data)
        
        
    except Exception as e:
        print("Error executing query:", e)
        return jsonify({"error": "Query execution failed"}), 5

if __name__ == '__main__':
    app.run(port=5001)
