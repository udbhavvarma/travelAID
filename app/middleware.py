from flask import Flask, request, jsonify
from app.nlp_query_parser import extract_parameters_with_llm, handle_out_of_scope_query
from app.utils.query_operations import decompose_query, execute_subqueries, aggregate_results, log_query
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)

@app.route('/federated_search', methods=['POST'])
def federated_search():
    """
    Unified search endpoint that processes both natural language queries (via LLM)
    and hardcoded integrated queries.
    """
    start_time = time.time()
    user_query = request.json.get("query", "")
    hardcoded_query = request.json.get("hardcoded_query")

    if user_query:
        unified_query = extract_parameters_with_llm(user_query)

        if unified_query == "OUT OF SCOPE":
            print("Query is out of scope. Handling gracefully.")
            return handle_out_of_scope_query(user_query)

            
        elif not unified_query:
            log_query(user_query, "unknown", "failure", 0)
            return jsonify({"error": "Failed to parse query"}), 500
        
        else:
            subqueries = decompose_query(unified_query)
            results = execute_subqueries(subqueries)

            results = aggregate_results(results)

            return jsonify(results)

    elif hardcoded_query:
        subqueries = decompose_query(hardcoded_query)

        results = execute_subqueries(subqueries)

        results = aggregate_results(results)

        response_data = {"query": hardcoded_query, "status": "success"}
        query_type = response_data["type"]
        status = response_data["status"]

        response_time = int((time.time() - start_time) * 1000)

        # Log the query
        log_query(user_query, query_type, status, response_time)

        return jsonify(results)


    else:
        return jsonify({"error": "No query or hardcoded_query provided"}), 400




if __name__ == '__main__':
    app.run(port=8000)

