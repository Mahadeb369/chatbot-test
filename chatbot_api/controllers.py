import os
import json
from flask import request, jsonify, render_template, send_from_directory, abort
from app import app, db
from sqlalchemy import text
from .gpt_visual import generate_graphs, detect_graph_request, only_detect_graph_request
from application.file_utility import data_to_csv
from .langchain.langchain_openai import sql_chain, heading_chain, fallback_heading_chain, get_memory
from .utility import omit_data
from .langchain.langchain_utility import get_most_recent_history_data, analyze_user_prompt, get_previous_messages
import time
from chatbot_api.langchain.langchain_pg_memory import PostgresChatMessageHistory
from langchain.schema import AIMessage, HumanMessage

now = time.time()

CSV_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'saved_csv'))
UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'uploads'))

# Route to serve the CSV file for download
@app.route('/download/<filename>')
def download_file(filename):
    print("\n---download-hit----\n")
    print("filename: ", filename)
    # Check in saved_csv folder
    saved_csv_path = os.path.join(CSV_FOLDER, filename)
    if os.path.exists(saved_csv_path):
        return send_from_directory(CSV_FOLDER, filename, as_attachment=True)
    
    # Check in uploads folder
    uploads_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(uploads_path):
        return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)
    
    # If file not found, return 404
    abort(404, description="File not found")


@app.route('/clear_memory', methods=['POST'])
def clear_memory():
    # memory.clear()
    return jsonify({"message": "Memory cleared successfully"}), 200


@app.route('/messages/<session_id>', methods=['GET'])
def get_messages(session_id):
    print("\n---get-messages-hit----\n")
    print("session_id: ", session_id)
    messages = get_previous_messages(session_id, omit=False)
    return jsonify(messages), 200


def handle_new_columns():
    try:
        status_columns = ""
        report_columns = ""

        with db.engine.connect() as connection:
            result = connection.execute(
                text("""SELECT table_name, column_name FROM public.new_columns""")
            )

            # Get column names once from the result object before fetchall
            new_columns_table_columns = result.keys()
            new_columns_table_rows = result.fetchall()

            # Convert rows to list of dicts
            data = [dict(zip(new_columns_table_columns, row)) for row in new_columns_table_rows]

            for item in data:
                table = item.get("table_name")
                columns = item.get("column_name")

                if table == "media_property_occupancy_report":
                    report_columns = columns
                elif table == "media_property_occupancy_status":
                    status_columns = columns

        # You can return or use these values later if needed
        return {
            "report_columns": report_columns,
            "status_columns": status_columns
        }

    except Exception as e:
        print(f"Error in getting new columns: {e}")
        return jsonify({"error": "Failed to get new columns"}), 400


@app.route('/chat', methods=['POST', 'GET'])
def chat():
    if request.method == 'POST':
        print("\n--------------get-hit--------------\n")
        now = time.time()
        user_prompt = request.form['user_prompt']
        session_id = request.form['session_id']
        print("session_id: ", session_id)
        print("user_prompt: ", user_prompt)

        if not user_prompt:
            return jsonify({"error": "No prompt provided"}), 400

        #! Save data in chat history table
        chat_history = PostgresChatMessageHistory(session_id=session_id)
        
        #! setp-1: Check if the user only wants visuals
        if only_detect_graph_request(user_prompt):
            try:
                most_recent_data = get_most_recent_history_data(session_id)

                if most_recent_data is None:
                    return jsonify({"error": "There is no data in the previous response."}), 400
                
                print("length of most_recent_memory: ", len(most_recent_data))
                
                visuals = []
                for item in most_recent_data:
                    csv_file_path = item.get("csv_filename")
                    prompt_from_memory = item.get("prompt")

                    if csv_file_path and prompt_from_memory:
                        image = generate_graphs(csv_path=f"/app/saved_csv/{csv_file_path}", user_query=prompt_from_memory)
                        if image:
                            visuals.append(image)

                chat_history.add_message(HumanMessage(content=user_prompt))
                chat_history.add_message(AIMessage(content=[{
                    "heading": "",
                    "csv_filename": None,
                    "data": [],
                    "images": visuals
                }]))

                return jsonify({
                    "heading": "Visuals based on your request:",
                    "csv_filename": None,
                    "data": [],
                    "images": visuals
                }), 200

            except Exception as e:
                print(f"Error in getting most recent memory: {e}")
                return jsonify({"error": "Failed to get most recent memory"}), 400

        #! step-2: user prompt analysis
        prompts = analyze_user_prompt(user_prompt)

        responses = []

        for index, prompt in enumerate(prompts):
            print(f"\n-----loop start for index: {index}-------\n")
            response_dict = {}

            #! step-2: get new columns from new_columns table
            table_new_columns = handle_new_columns()

            #! step-3: Generate SQL query
            try:
                print("prompt: ", prompt)
                memory = get_memory(session_id)  # ✅ session-specific memory
                memory_variables = memory.load_memory_variables({})  # manually load memory
                sql_query = sql_chain.run({
                    "history": memory_variables.get("history") if index == 0 else omit_data(responses),
                    "query": prompt,
                    "new_status_columns": table_new_columns.get("status_columns"),
                    "new_report_columns": table_new_columns.get("report_columns"),
                })
            except Exception as e:
                print(f"Error in sql generation: {e}")
                print("user_prompt: ", prompt)
                # memory.clear()
                # print("Memory cleared successfully")
                return jsonify({"error": "Cache memory exceeded the token limit.\n We have cleared the cache memory now.\n Please run the prompt again."}), 400

            try:
                sql_block = sql_query.split("```sql")[1].split("```")[0]
                sql_query_block = sql_block.strip()
                response_dict["sql_query"] = str(sql_query_block)
                response_dict["prompt"] = prompt
            except Exception as e:
                print(f"Error in sql extraction: {e}")
                return jsonify({"error": "Failed to extract SQL query from response"}), 400

            #! step-4: Execute the SQL query
            with db.engine.connect() as connection:
                print("Executing SQL:\n", sql_query_block)
                try:
                    result = connection.execute(text(sql_query_block))
                    rows = result.fetchall()
                    columns = result.keys()
                    data = [dict(zip(columns, row)) for row in rows]
                    response_dict["data"] = data
                except Exception as e:
                    print(f"Error in sql execution: {e}")
                    if str(e).find("DivisionByZero"):
                        return jsonify({"error": "There are currently no data found for your request."}), 400
                    return jsonify({"error": "Failed to execute SQL query"}), 400
                finally:
                    connection.close()

            #! step-5: save data to csv
            csv_path = None
            file_name = None
            if len(data) > 0:
                csv_path = data_to_csv(data)
                file_name = os.path.basename(csv_path)

            response_dict["csv_filename"] = str(file_name) if file_name else None

            #! step-6: Generate heading
            try:
                heading = heading_chain.run({
                    "user_query": prompt,
                    "data": data,
                    "length": len(data)
                })
            except Exception as e:
                print(f"Error in heading generation: {e}")
                # heading = "Please find below the response based on your query."
                heading = fallback_heading_chain.run({
                    "user_query": prompt
                })
            response_dict["heading"] = heading

            #! step-7: generate visuals
            if detect_graph_request(prompt):
                visuals = generate_graphs(csv_path=csv_path if csv_path else None, user_query=prompt)
            else:
                visuals = []
            response_dict["images"] = visuals

            #! step-8: Save user query, SQL query, and data response in memory
            # if index < len(prompts) - 1 :
            #     try:
            #         memory.save_context(
            #             {"input": prompt},
            #             {"output": json.dumps(omit_data(response_dict), default=json_serializable)}
            #             # {"output": json.dumps({"sql_query": sql_query_block, "data": data, "heading": heading, "csv_filename": file_name, "visuals": visuals}, default=json_serializable)}
            #         )
            #     except Exception as e:
            #         print(f"Error in memory save: {e}")

            responses.append(response_dict)

        #! Save data in chat history table
        chat_history.add_message(HumanMessage(content=user_prompt))
        chat_history.add_message(AIMessage(content=responses))


        #! step-9: Save user query, SQL query, and data response in memory
        # print("Saving in memory")
        # try:
        #     memory.save_context(
        #         {"input": user_prompt},
        #         {"output": json.dumps(omit_data(responses), default=json_serializable)}
        #         # {"output": json.dumps({"sql_query": sql_query_block, "data": data, "heading": heading, "csv_filename": file_name, "visuals": visuals}, default=json_serializable)}
        #     )
        # except Exception as e:
        #     print(f"Error in memory save: {e}")

        return jsonify(responses), 200
    
    if request.method == 'GET':
        return render_template('chat.html')