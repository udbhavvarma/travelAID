from flask import Flask, jsonify, request
import pymysql
import re
from groq import Groq
from app.schema import mediated_schema


app = Flask(__name__)




def query_mediated_schema(query, table_name):
    """
    Queries the mediated schema and returns unified results.
    """
    if table_name not in mediated_schema:
        raise ValueError(f"Table '{table_name}' not found in mediated schema.")

    table = mediated_schema[table_name]
    combined_results = []

    TOURIST_SPOTS_COLUMN_MAPPINGS = {
        "spot_id": 0,
        "name_spot": 1,
        "type_spot": 2,
        "description_spot": 3,
        "location_address": 4,
        "location_locality": 5,
        "location_city": 6,
        "contact_phone": 7,
        "contact_email": 8,
        "contact_website": 9,
        "category": 10,
        "rating_average": 11,
        "pricing_currency": 12,
        "pricing_price_level": 13,
        "accessibility_wheelchair_accessible": 14,
        "accessibility_braille_menu": 15,
        "accessibility_service_animals_allowed": 16,
        "accessibility_elevator_available": 17,
        "accessibility_accessible_restrooms": 18,
        "amenities_wifi": 19,
        "amenities_parking_available": 20,
        "amenities_outdoor_seating": 21,
        "amenities_live_music": 22,
        "sitename": 23
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
            combined_results = sort_combined_results(combined_results, order_by_columns, TOURIST_SPOTS_COLUMN_MAPPINGS)

        # Apply LIMIT if specified
        if limit_value is not None:
            combined_results = combined_results[:limit_value]

        return combined_results

    except Exception as e:
        print(f"Error querying mediated schema: {e}")
        return []

    
client = Groq(
    api_key="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"
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

def generate_ts_query_with_llm(filters):
    """
    Generate a SQL query using an LLM for the Hotels table based on user-provided filters.
    """
    prompt = f"""
    You are an assistant designed to generate MySQL queries for a table of hotels in Indian cities named tourist_spots.
    You are only supposed to generate a single query for a table

    PLEASE USE PARAMETERS EXPLICITLY MENTIONED IN THE QUERY. If accessibility_wheelchair_accessible or braille_menu is not mentioned, do not include it in the query.

    USE LIMIT WHEN THE USER ASKS FOR TOP-N RESULTS!!!!!!!!! eg. top 5 restaurants -> LIMIT 5, top 5 tourist_attractions -> LIMIT 5

    

    spot_id varchar(50) PK (Primary Key)
    name_spot varchar(255) (Name of the spot)
    type_spot varchar(50) (Type of the spot, 2 Discrete values: 'restaurant', 'tourist_attraction')
    description_spot text (Description of the spot)
    location_address varchar(255) (Address of the spot)
    location_locality varchar(50) (Locality of the spot)
    location_city varchar(50) (City of the spot)
    contact_phone varchar(15) (Contact phone number)
    contact_email varchar(50) (Contact email)
    contact_website varchar(50) (Contact website)
    category varchar(50) (Category of the spot ONLY USE IF EXPLICITLY MENTIONED: Italian, Indian, etc Cuisines or Historical, Natural, etc Attractions)
    rating_average float (Average rating of the spot)
    pricing_currency varchar(5) (Currency of pricing)
    pricing_price_level int (Price level of the spot)

    accessibility_wheelchair_accessible boolean (Is wheelchair accessible? 2 Discrete values: 0 or 1)
    accessibility_braille_menu boolean (Is braille menu available? 2 Discrete values: 0 or 1)
    accessibility_service_animals_allowed boolean (Are service animals allowed? 2 Discrete values: 0 or 1)
    accessibility_elevator_available boolean (Is elevator available? 2 Discrete values: 0 or 1)
    accessibility_accessible_restrooms boolean (Are restrooms accessible? 2 Discrete values: 0 or 1)

    amenities_wifi boolean (Is wifi available? 2 Discrete values: 0 or 1)
    amenities_parking_available boolean (Is parking available? 2 Discrete values: 0 or 1)
    amenities_outdoor_seating boolean (Is outdoor seating available? 2 Discrete values: 0 or 1)
    amenities_live_music boolean (Is live music available? 2 Discrete values: 0 or 1)

    sitename varchar(50) (Name of the site)

    Rules:
    1. You have to generate a simple query that fetches all columns from the table. Do not use complicated clauses unnecessarily.
    2. Reflect all filters provided in the input in the WHERE clause.
    3. Give a single queryt that can be executed straight away.
    4. Handle semantic similarity by handling difference in uppercase and lowercase cities and localities. For example, 'Delhi' and 'delhi' should be treated as the same city. Use LIKE operator for locality and city columns.
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



@app.route('/tourist_spots', methods=['GET'])
def get_tourist_spots():
    filters = request.args.to_dict(flat=False)

    llm_query_response = generate_ts_query_with_llm(filters)
    if not llm_query_response:
        return jsonify({"error": "Failed to generate query"}), 500

    query = llm_query_response

    try:
        rows = query_mediated_schema(query, "tourist_spots")
        tourist_spots_data = [
            {
                "name": row[1],
                "type": row[2],
                "description": row[3],
                "location": {
                    "address": row[4],
                    "locality": row[5],
                    "city": row[6]
                },
                "contact": {
                    "phone": row[7],
                    "email": row[8],
                    "website": row[9]
                },
                "category": row[10],
                "rating": row[11],
                "pricing": {
                    "currency": row[12],
                    "price_level": row[13]
                },
                "accessibility": {
                    "wheelchair_accessible": bool(row[14]),
                    "braille_menu": bool(row[15]),
                    "service_animals_allowed": bool(row[16]),
                    "elevator_available": bool(row[17]),
                    "accessible_restrooms": bool(row[18])
                },
                "amenities": {
                    "wifi": bool(row[19]),
                    "parking_available": bool(row[20]),
                    "outdoor_seating": bool(row[21]),
                    "live_music": bool(row[22])
                },
                "site": row[23]
            }
            for row in rows
            
        ]

        print(tourist_spots_data[0])

        print(f"Number of Tourist Spots: {len(tourist_spots_data)}")
        return jsonify(tourist_spots_data)
        
        
    except Exception as e:
        print("Error executing query:", e)
        return jsonify({"error": "Query execution failed"}), 5


if __name__ == '__main__':
    app.run(port=5003)
