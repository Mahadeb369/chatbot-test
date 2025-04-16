import json
from .langchain_openai import query_decomposition_chain, get_memory
from langchain.schema import AIMessage, HumanMessage
from .langchain_pg_memory import PostgresChatMessageHistory

# def get_history_data(search_query):
#     history = memory.load_memory_variables({}).get("history")
#     conversation = history.strip().split('\n')
    
#     for index, item in enumerate(conversation):
#         previous_prompt = item.split("Human: ")[1].strip() if "Human:" in item else ""

#         if search_query.lower() == previous_prompt.lower() and index + 1 < len(conversation):
#             ai_line = conversation[index + 1]
#             # Remove "AI: " prefix to get the JSON string
#             json_str = ai_line[len("AI: "):]
#             try:
#                 data = json.loads(json_str)
#                 print("in get_history_data: ", data)
#                 print("length of data: ", len(data))
#                 return data
#                 # return json.loads(json_str)
#             except json.JSONDecodeError as e:
#                 print(f"JSON parsing error: {e}")
#                 return None
#     return None


def get_previous_messages(session_id, omit=True):
    try:
        pg_memory = PostgresChatMessageHistory(session_id=session_id)
        messages = []

        for message in pg_memory.get_all_messages(omit=omit, limit=30):
            
            if isinstance(message, AIMessage):
                messages.append({
                    "type": "AI",
                    "content": message.content
                })
            elif isinstance(message, HumanMessage):
                messages.append({
                    "type": "Human",
                    "content": message.content
                })
        print("length of messages: ", len(messages))

        return messages
    except Exception as e:
        print(f"Error in get_messages: {e}")
        return []

def get_most_recent_history_data(session_id=None):
    if session_id is None:
        return None

    memory = get_memory(session_id)
    memory_variables = memory.load_memory_variables({})
    history = memory_variables.get("history")

    # print("history from get_most_recent_history_data: ", history)

    # if there is a history and it has at least 2 messages (one human, one AI)
    if isinstance(history, list) and len(history) >= 2:
        human_msg = history[-2]
        ai_msg = history[-1]

        try:
            # Ensure they are correct message types
            if isinstance(human_msg, HumanMessage) and isinstance(ai_msg, AIMessage):
                human_data = human_msg.content
                ai_data = ai_msg.content

                # If ai_data is a JSON string, parse it
                if isinstance(ai_data, str):
                    ai_data = json.loads(ai_data)

                return ai_data
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            return None

    return None

def analyze_user_prompt(user_prompt):
    try:
        gpt_response = query_decomposition_chain.run({
            "user_query": user_prompt
        })
        decomposed_prompts = json.loads(gpt_response.split("```json\n")[1].split("```")[0])
        print("Decomposed prompts: ", decomposed_prompts)
        return decomposed_prompts
    except Exception as e:
        print(f"Error in decomposing user prompt: {e}")
        return e