# import autogen
# import re
# from typing import List, Dict, Any
# import json
# from application.agents1 import (
#     availability_check_agent,
#     location_selection_agent,
#     finance_agent,
#     final_aggregator_agent,
#     user_proxy_agent
# )

# class Inference:
#     """
#     Inference class for analyzing advertising inventory using multiple specialized agents.
#     """

#     def __init__(self, inventory_data: List[Dict[str, Any]], user_query: str):
#         self.inventory_data = inventory_data
#         self.user_query = user_query
#         self.chat_history = []
#         self.result = None
#         self.final_summary = None  # Stores final descriptive output

#     def create_sequential_chat(self) -> None:
#         """
#         Creates and configures a sequence of chats, where each agent processes the result from the previous one.
#         """

#         initial_message = (
#             "Process this advertising request through sequential agents, ensuring each agent provides a response in valid JSON format.\n\n"
#             "Required steps and response formats:\n"
#             "1. Location Selection Agent: Return JSON with 'available_locations' array filtered by location.\n"
#             "2. Availability Check Agent: Return JSON with 'available_locations' array filtered by availability dates.\n"
#             "3. Finance Agent: Return JSON with 'available_locations' array filtered by budget, and 'budget_allocation' if applicable.\n"
#             "4. Final Aggregator: Return a structured JSON response **AND** a human-readable summary at the end.\n\n"
#             f"User Query: {self.user_query}\n\n"
#             "Context:\n"
#             f"{json.dumps({'inventory_data': self.inventory_data}, indent=2)}"
#         )

#         chat_results = user_proxy_agent.initiate_chats([
#             {
#                 "recipient": location_selection_agent,
#                 "message": initial_message,
#                 "max_turns": 2,
#                 "summary_method": "last_msg",
#             },
#             {
#                 "recipient": availability_check_agent,
#                 "message": "Process the filtered locations for availability.",
#                 "max_turns": 2,
#                 "summary_method": "last_msg",
#             },
#             {
#                 "recipient": finance_agent,
#                 "message": "Apply budget constraints to the available locations.",
#                 "max_turns": 2,
#                 "summary_method": "last_msg",
#             },
#             {
#                 "recipient": final_aggregator_agent,
#                 "message": "Compile the final results and generate a summary.",
#                 "max_turns": 2,
#                 "summary_method": "last_msg",
#             },
#         ])

#         self.chat_history = chat_results

#     def process_query(self):
#         """
#         Processes the user query through the multi-agent system in sequential mode.
#         """
#         print("Starting query processing with sequential chats...")

#         try:
#             self.create_sequential_chat()

#             final_chat = self.chat_history[-1]["messages"][-1]
#             self.result, self.final_summary = self.extract_final_output(final_chat)

#         except Exception as e:
#             print(f"Error during chat processing: {str(e)}")
#             self.result = {"error": f"Processing failed: {str(e)}"}
#             self.final_summary = "Error encountered during processing."

#     def extract_final_output(self, message: Dict[str, Any]) -> (Dict[str, Any], str):
#         """
#         Extracts the final JSON result and summary from the last chat.
#         """
#         content = message.get("content", "")
#         extracted_json = None
#         extracted_summary = None

#         json_match = re.search(r"```json\n(.*?)\n```", content, re.DOTALL)
#         if json_match:
#             try:
#                 extracted_json = json.loads(json_match.group(1))
#             except json.JSONDecodeError:
#                 pass

#         summary_match = re.search(r"\*\*Final Summary:\*\*(.*?)$", content, re.DOTALL)
#         if summary_match:
#             extracted_summary = summary_match.group(1).strip()

#         return extracted_json if extracted_json else {"error": "No valid JSON result"}, extracted_summary if extracted_summary else "Summary not available."

#     def run(self) -> Dict[str, Any]:
#         """
#         Runs the complete inference process and returns both JSON results and a final summary.
#         """
#         print("Starting Inference in Sequential Mode...")
#         self.process_query()
#         print("Inference complete.")

#         if self.result:
#             print(f"Final result: {json.dumps(self.result, indent=2)}")

#         print("\n===== Final Summary =====")
#         print(self.final_summary)

#         return {
#             "json_result": self.result,
#             "final_summary": self.final_summary
#         }


import autogen
import re
from typing import List, Dict, Any
import json
from application.agents1 import (
    availability_check_agent,
    location_selection_agent,
    # finance_agent,
    final_aggregator_agent,
    user_proxy_agent
)

class Inference:
    """
    Inference class for analyzing advertising inventory using multiple specialized agents.
    """

    def __init__(self, inventory_data: List[Dict[str, Any]], user_query: str):
        self.inventory_data = inventory_data
        self.user_query = user_query
        self.chat_history = []
        self.result = None
        self.final_summary = None  # Stores final descriptive output

    def create_group_chat(self) -> autogen.GroupChat:
        """
        Creates and configures the group chat with all necessary agents.
        """
        agents = [
            user_proxy_agent,
            location_selection_agent,  # Start with location filtering
            availability_check_agent,  # Then check availability
            # finance_agent,             # Apply budget constraints
            final_aggregator_agent     # Compile final results
        ]

        return autogen.GroupChat(
            agents=agents,
            messages=[],
            max_round=10,
            speaker_selection_method="round_robin"
        )

    def create_chat_manager(self, group_chat: autogen.GroupChat) -> autogen.GroupChatManager:
        """
        Creates the group chat manager with proper configuration.
        """
        return autogen.GroupChatManager(
            groupchat=group_chat,
            llm_config=final_aggregator_agent.llm_config
        )

    def process_query(self):
        """
        Processes the user query through the multi-agent system.
        """
        print("Starting query processing...")

        group_chat = self.create_group_chat()
        manager = self.create_chat_manager(group_chat)

        # initial_message = (
        #     "Process this advertising request and ensure each agent provides a response in valid JSON format.\n\n"
        #     "Required steps and response formats:\n"
        #     "1. Location Selection Agent: Return JSON with 'available_locations' array filtered by location.\n"
        #     "2. Availability Check Agent: Return JSON with 'available_locations' array filtered by availability dates.\n"
        #     "3. Finance Agent: Return JSON with 'available_locations' array filtered by budget, and 'budget_allocation' if applicable.\n"
        #     "4. Final Aggregator: Return a structured JSON response **AND** a human-readable summary at the end.\n\n"
        #     "**IMPORTANT:** Ensure the human-readable summary starts with '**Final Summary:**' and strictly follows the below structure:\n\n"
        #     "1. **Media Types Considered**: Skywalks, Hoardings\n"
        #     "2. **Budget Applied**: Rs. XX,XX,XXX (as per constraints)\n"
        #     "3. **Available Locations**:\n"
        #     "   - **Site**: <Site ID> | **Material Code**: <Material Name>\n"
        #     "   - **Rate Card**: Rs. <Rate Amount>\n"
        #     "   - **Location**: <Main Location> | **Sub Location**: <Specific Area>\n"
        #     "   - **Landmark**: <Landmark if available>\n"
        #     "   - **Availability**: Available Immediately / Available after <Date>\n"
        #     "   - **Remarks**: <Additional Notes>\n"
        #     "4. **Budget Allocation Breakdown**:\n"
        #     "   - **Skywalks**: Rs. <Allocated Budget> (XX% of Total)\n"
        #     "   - **Hoardings**: Rs. <Allocated Budget> (XX% of Total)\n\n"
        #     "Ensure that this format is followed exactly for all summaries, with no deviations.\n\n"
        #     f"User Query: {self.user_query}\n\n"
        #     "Context:\n"
        #     f"{json.dumps({'inventory_data': self.inventory_data}, indent=2)}"
        # )

        initial_message = (
            "Process this advertising request and ensure each agent provides a response in valid JSON format.\n\n"
            "Required steps and response formats:\n"
            "1. Location Selection Agent: Return JSON with 'available_locations' array filtered by location.\n"
            "2. Availability Check Agent: Return JSON with 'available_locations' array filtered by availability dates.\n"
            "3. Finance Agent: Return JSON with 'available_locations' array filtered by budget, and 'budget_allocation' if applicable.\n"
            "4. Final Aggregator: Return a structured JSON response **AND** a human-readable summary at the end.\n\n"
            "**IMPORTANT:** Ensure the human-readable summary starts with '**Final Summary:**' and strictly follows the below structure:\n\n"
            "**Below are the results as per your need:**\n\n"
            "**Site 1**:\n"
            "    **Site ID**: <ID>\n"
            "    **Material Code**: <Code>\n"
            "    **Rate Card**: Rs. <Amount>\n"
            "    **Location**: <Main Location>\n"
            "    **Sub Location**: <Area>\n"
            "    **Landmark**: <Landmark>\n"
            "    **Availability**: <Status>\n"
            "    **Remarks**: <Notes>\n\n"
            "___________________________\n\n"
            "**Site 2**:\n"
            "    **Site ID**: <ID>\n"
            "    **Material Code**: <Code>\n"
            "    **Rate Card**: Rs. <Amount>\n"
            "    **Location**: <Main Location>\n"
            "    **Sub Location**: <Area>\n"
            "    **Landmark**: <Landmark>\n"
            "    **Availability**: <Status>\n"
            "    **Remarks**: <Notes>\n\n"
            "___________________________\n\n"
            "Ensure that this format is followed exactly for all summaries, with no deviations.\n\n"
            f"User Query: {self.user_query}\n\n"
            "Context:\n"
            f"{json.dumps({'inventory_data': self.inventory_data}, indent=2)}"
        )

        try:
            print("Initiating chat with agents...")
            chat_response = user_proxy_agent.initiate_chat(manager, message=initial_message)

            self.chat_history = group_chat.messages
            print(f"Total messages in chat history: {len(self.chat_history)}")

            extracted_json = None  # Variable to hold the final extracted JSON
            extracted_summary = None  # Variable to hold the final human-readable summary

            for idx, message in enumerate(self.chat_history):
                if not isinstance(message, dict):
                    print(f"\nMessage {idx + 1} is not a dictionary. Skipping.")
                    continue

                print(f"\nMessage {idx + 1}:")
                print(f"Raw Message: {json.dumps(message, indent=2)}")  # Debug full message
                
                content = message.get("content", "")

                # Extract JSON from Markdown code block (```json ... ```)
                json_match = re.search(r"```json\n(.*?)\n```", content, re.DOTALL)
                if json_match:
                    try:
                        extracted_json = json.loads(json_match.group(1))
                        print(f"Successfully extracted JSON from Message {idx + 1}")
                    except json.JSONDecodeError:
                        print(f"JSON decoding failed for Message {idx + 1}")
                        continue

                # Extract final summary (assuming it's placed after JSON in plain text)
                summary_match = re.search(r"\*\*Final Summary:\*\*(.*?)$", content, re.DOTALL)
                if summary_match:
                    extracted_summary = summary_match.group(1).strip()
                    print(f"Successfully extracted Final Summary from Message {idx + 1}")

            if extracted_json:
                self.result = extracted_json
            else:
                print("No valid JSON results found in any message")
                self.result = {"error": "No valid results from any agent"}

            if extracted_summary:
                self.final_summary = extracted_summary
            else:
                print("No final summary found in any message")
                self.final_summary = "Summary not available."

        except Exception as e:
            print(f"Error during chat processing: {str(e)}")
            self.result = {"error": f"Processing failed: {str(e)}"}
            self.final_summary = "Error encountered during processing."

    def run(self) -> Dict[str, Any]:
        """
        Runs the complete inference process and returns both JSON results and a final summary.
        """
        print("Starting Inference...")
        self.process_query()
        print("Inference complete.")

        if self.result:
            print(f"Final result type: {type(self.result)}")
            print(f"Final result contents: {json.dumps(self.result, indent=2)}")

        print("\n===== Final Summary =====")
        print(self.final_summary)

        return {
            "json_result": self.result,
            "final_summary": self.final_summary
        }



# import autogen
# import re
# from typing import List, Dict, Any
# import json
# from application.agents1 import (
#     availability_check_agent,
#     location_selection_agent,
#     finance_agent,
#     final_aggregator_agent,
#     user_proxy_agent
# )

# class Inference:
#     """
#     Inference class for analyzing advertising inventory using multiple specialized agents.
#     """

#     def __init__(self, inventory_data: List[Dict[str, Any]], user_query: str):
#         self.inventory_data = inventory_data
#         self.user_query = user_query
#         self.chat_history = []
#         self.result = None
#         self.final_summary = None  # Stores markdown-formatted summary

#     def create_group_chat(self) -> autogen.GroupChat:
#         """
#         Creates and configures the group chat with all necessary agents.
#         """
#         agents = [
#             user_proxy_agent,
#             location_selection_agent,  # Start with location filtering
#             availability_check_agent,  # Then check availability
#             finance_agent,             # Apply budget constraints
#             final_aggregator_agent     # Compile final results
#         ]

#         return autogen.GroupChat(
#             agents=agents,
#             messages=[],
#             max_round=5,
#             speaker_selection_method="round_robin"
#         )

#     def create_chat_manager(self, group_chat: autogen.GroupChat) -> autogen.GroupChatManager:
#         """
#         Creates the group chat manager with proper configuration.
#         """
#         return autogen.GroupChatManager(
#             groupchat=group_chat,
#             llm_config=final_aggregator_agent.llm_config
#         )

#     def process_query(self):
#         """
#         Processes the user query through the multi-agent system.
#         """
#         print("Starting query processing...")

#         group_chat = self.create_group_chat()
#         manager = self.create_chat_manager(group_chat)

#         initial_message = (
#             "Process this advertising request and ensure each agent provides a response in valid JSON format.\n\n"
#             "Required steps and response formats:\n"
#             "1. Location Selection Agent: Return JSON with 'available_locations' array filtered by location.\n"
#             "2. Availability Check Agent: Return JSON with 'available_locations' array filtered by availability dates.\n"
#             "3. Finance Agent: Return JSON with 'available_locations' array filtered by budget, and 'budget_allocation' if applicable.\n"
#             "4. Final Aggregator: Return a structured JSON response **AND** a markdown-formatted summary.\n\n"
#             "**IMPORTANT:** The summary must be provided in markdown format within a markdown code block:\n\n"
#             "```markdown\n"
#             "## 📊 Final Summary\n"
#             "---\n"
#             "### 1. Total Available Locations\n"
#             "{total_count}\n"
#             "---\n"
#             "### 2. Media Types Considered\n"
#             "{media_types}\n"
#             "---\n"
#             "### 3. Budget Applied\n"
#             "Rs. {budget_amount}\n"
#             "---\n"
#             "### 4. Best Available Locations\n\n"
#             "#### 📍 Location 1\n"
#             "- Site: *{site_id}*\n"
#             "- Material Code: *{material_name}*\n"
#             "- Rate Card: Rs. {rate_amount}\n"
#             "- Location: *{main_location}*\n"
#             "  - Sub Location: *{specific_area}*\n"
#             "  - Landmark: *{landmark}*\n"
#             "- Availability: *{availability_status}*\n"
#             "- Remarks: *{remarks}*\n"
#             "---\n"
#             "[Additional locations follow same format with Location 2, 3, etc.]\n\n"
#             "### 5. Budget Allocation Breakdown\n\n"
#             "#### 🏗️ Skywalks\n"
#             "Rs. {skywalk_budget} (*{skywalk_percentage}%* of Total)\n\n"
#             "#### 🎯 Hoardings\n"
#             "Rs. {hoarding_budget} (*{hoarding_percentage}%* of Total)\n"
#             "```\n\n"
#             f"User Query: {self.user_query}\n\n"
#             "Context:\n"
#             f"{json.dumps({'inventory_data': self.inventory_data}, indent=2)}"
#         )

#         try:
#             print("Initiating chat with agents...")
#             chat_response = user_proxy_agent.initiate_chat(manager, message=initial_message)

#             self.chat_history = group_chat.messages
#             print(f"Total messages in chat history: {len(self.chat_history)}")

#             extracted_json = None
#             extracted_summary = None

#             for idx, message in enumerate(self.chat_history):
#                 if not isinstance(message, dict):
#                     print(f"\nMessage {idx + 1} is not a dictionary. Skipping.")
#                     continue

#                 print(f"\nMessage {idx + 1}:")
#                 print(f"Raw Message: {json.dumps(message, indent=2)}")
                
#                 content = message.get("content", "")

#                 # Extract JSON from code block
#                 json_match = re.search(r"```json\n(.*?)\n```", content, re.DOTALL)
#                 if json_match:
#                     try:
#                         extracted_json = json.loads(json_match.group(1))
#                         print(f"Successfully extracted JSON from Message {idx + 1}")
#                     except json.JSONDecodeError:
#                         print(f"JSON decoding failed for Message {idx + 1}")
#                         continue

#                 # Extract markdown summary from markdown code block
#                 markdown_match = re.search(r"```markdown\n(.*?)\n```", content, re.DOTALL)
#                 if markdown_match:
#                     extracted_summary = markdown_match.group(1).strip()
#                     print(f"Successfully extracted Markdown summary from Message {idx + 1}")

#                 # Fallback: Try to find markdown without code block but with proper headers
#                 if not extracted_summary:
#                     markdown_fallback = re.search(r"# Final Summary\n\n(.*?)(?=\n#|$)", content, re.DOTALL)
#                     if markdown_fallback:
#                         extracted_summary = markdown_fallback.group(0).strip()
#                         print(f"Successfully extracted Markdown summary using fallback from Message {idx + 1}")

#             if extracted_json:
#                 self.result = extracted_json
#             else:
#                 print("No valid JSON results found in any message")
#                 self.result = {"error": "No valid results from any agent"}

#             if extracted_summary:
#                 self.final_summary = extracted_summary
#             else:
#                 print("No markdown summary found in any message")
#                 self.final_summary = """# Final Summary

# ## Error
# Summary not available."""

#         except Exception as e:
#             print(f"Error during chat processing: {str(e)}")
#             self.result = {"error": f"Processing failed: {str(e)}"}
#             self.final_summary = """# Final Summary

# ## Error
# Error encountered during processing."""

#     def run(self) -> Dict[str, Any]:
#         """
#         Runs the complete inference process and returns both JSON results and a markdown-formatted summary.
#         """
#         print("Starting Inference...")
#         self.process_query()
#         print("Inference complete.")

#         if self.result:
#             print(f"Final result type: {type(self.result)}")
#             print(f"Final result contents: {json.dumps(self.result, indent=2)}")

#         print("\n===== Markdown Summary =====")
#         print(self.final_summary)

#         return {
#             "json_result": self.result,
#             "final_summary": self.final_summary
        # }
###############LATEST WORKING
# import autogen
# import re
# from typing import List, Dict, Any
# import json
# from application.agents import (
#     availability_check_agent,
#     location_selection_agent,
#     finance_agent,
#     final_aggregator_agent,
#     user_proxy_agent
# )

# class Inference:
#     """
#     Inference class for analyzing advertising inventory using multiple specialized agents.
#     """

#     def __init__(self, inventory_data: List[Dict[str, Any]], user_query: str):
#         self.inventory_data = inventory_data
#         self.user_query = user_query
#         self.chat_history = []
#         self.result = None
#         self.final_summary = None  # Stores final descriptive output

#     def create_group_chat(self) -> autogen.GroupChat:
#         """
#         Creates and configures the group chat with all necessary agents.
#         """
#         agents = [
#             user_proxy_agent,
#             availability_check_agent,
#             location_selection_agent,
#             finance_agent,
#             final_aggregator_agent
#         ]

#         return autogen.GroupChat(
#             agents=agents,
#             messages=[],
#             max_round=10,
#             speaker_selection_method="round_robin"
#         )

#     def create_chat_manager(self, group_chat: autogen.GroupChat) -> autogen.GroupChatManager:
#         """
#         Creates the group chat manager with proper configuration.
#         """
#         return autogen.GroupChatManager(
#             groupchat=group_chat,
#             llm_config=final_aggregator_agent.llm_config
#         )

#     def process_query(self):
#         """
#         Processes the user query through the multi-agent system.
#         """
#         print("Starting query processing...")

#         group_chat = self.create_group_chat()
#         manager = self.create_chat_manager(group_chat)

#         # initial_message = (
#         #     "Process this advertising request and ensure each agent provides a response in valid JSON format.\n\n"
#         #     "Required steps and response formats:\n"
#         #     "1. Availability Check Agent: Return JSON with 'available_spots' array\n"
#         #     "2. Location Selection Agent: Return JSON with 'selected_locations' array\n"
#         #     "3. Finance Agent: Return JSON with 'financial_analysis' object\n"
#         #     "4. Final Aggregator: Return a structured JSON response **AND** a human-readable summary at the end.\n\n"
#         #     f"User Query: {self.user_query}\n\n"
#         #     "Context:\n"
#         #     f"{json.dumps({'inventory_data': self.inventory_data}, indent=2)}"
#         # )

#         initial_message = (
#             "Process this advertising request and ensure each agent provides a response in valid JSON format.\n\n"
#             "Required steps and response formats:\n"
#             "1. Availability Check Agent: Return JSON with 'available_spots' array\n"
#             "2. Location Selection Agent: Return JSON with 'selected_locations' array\n"
#             "3. Finance Agent: Return JSON with 'financial_analysis' object\n"
#             "4. Final Aggregator: Return a structured JSON response **AND** a human-readable summary at the end.\n\n"
#             "**IMPORTANT:** Ensure the human-readable summary starts with '**Final Summary:**' and strictly follows the below structure:\n\n"
#             "1. **Total Available Locations:** <number>\n"
#             "2. **Media Types Considered:** <media types>\n"
#             "3. **Budget Applied:** Rs. <amount> (as per constraints)\n"
#             "4. **Best Available Locations:**\n"
#             "   - **Site:** <Site ID> | **Material Code:** <Material Name>\n"
#             "   - **Rate Card:** Rs. <Rate Amount>\n"
#             "   - **Location:** <Main Location> | **Sub Location:** <Specific Area>\n"
#             "   - **Landmark:** <Landmark if available>\n"
#             "   - **Availability:** Available Immediately / Available after <Date>\n"
#             "   - **Remarks:** <Additional Notes>\n"
#             "5. **Budget Allocation Breakdown:**\n"
#             "   - **<Media Type>:** Rs. <Allocated Budget> (XX% of Total)\n\n"
#             "Ensure that this format is followed exactly for all summaries, with no deviations.\n\n"
#             f"User Query: {self.user_query}\n\n"
#             "Context:\n"
#             f"{json.dumps({'inventory_data': self.inventory_data}, indent=2)}"
#         )

#         try:
#             print("Initiating chat with agents...")
#             chat_response = user_proxy_agent.initiate_chat(manager, message=initial_message)

#             self.chat_history = group_chat.messages
#             print(f"Total messages in chat history: {len(self.chat_history)}")

#             extracted_json = None  # Variable to hold the final extracted JSON
#             extracted_summary = None  # Variable to hold the final human-readable summary

#             for idx, message in enumerate(self.chat_history):
#                 if not isinstance(message, dict):
#                     print(f"\nMessage {idx + 1} is not a dictionary. Skipping.")
#                     continue

#                 print(f"\nMessage {idx + 1}:")
#                 print(f"Raw Message: {json.dumps(message, indent=2)}")  # Debug full message
                
#                 content = message.get("content", "")

#                 # Extract JSON from Markdown code block (```json ... ```)
#                 json_match = re.search(r"```json\n(.*?)\n```", content, re.DOTALL)
#                 if json_match:
#                     try:
#                         extracted_json = json.loads(json_match.group(1))
#                         print(f"Successfully extracted JSON from Message {idx + 1}")
#                     except json.JSONDecodeError:
#                         print(f"JSON decoding failed for Message {idx + 1}")
#                         continue

#                 # Extract final summary (assuming it's placed after JSON in plain text)
#                 summary_match = re.search(r"\*\*Final Summary:\*\*(.*?)$", content, re.DOTALL)
#                 if summary_match:
#                     extracted_summary = summary_match.group(1).strip()
#                     print(f"Successfully extracted Final Summary from Message {idx + 1}")

#             if extracted_json:
#                 self.result = extracted_json
#             else:
#                 print("No valid JSON results found in any message")
#                 self.result = {"error": "No valid results from any agent"}

#             if extracted_summary:
#                 self.final_summary = extracted_summary
#             else:
#                 print("No final summary found in any message")
#                 self.final_summary = "Summary not available."

#         except Exception as e:
#             print(f"Error during chat processing: {str(e)}")
#             self.result = {"error": f"Processing failed: {str(e)}"}
#             self.final_summary = "Error encountered during processing."

#     def run(self) -> Dict[str, Any]:
#         """
#         Runs the complete inference process and returns both JSON results and a final summary.
#         """
#         print("Starting Inference...")
#         self.process_query()
#         print("Inference complete.")

#         if self.result:
#             print(f"Final result type: {type(self.result)}")
#             print(f"Final result contents: {json.dumps(self.result, indent=2)}")

#         print("\n===== Final Summary =====")
#         print(self.final_summary)

#         return {
#             "json_result": self.result,
#             "final_summary": self.final_summary
#         }
############LATEST WORKING
# import autogen
# from typing import List, Dict, Any
# import json
# from application.agents import (
#     availability_check_agent,
#     location_selection_agent,
#     finance_agent,
#     final_aggregator_agent,
#     user_proxy_agent
# )

# class Inference:
#     """
#     Inference class for analyzing advertising inventory using multiple specialized agents.
#     """

#     def __init__(self, inventory_data: List[Dict[str, Any]], user_query: str):
#         self.inventory_data = inventory_data
#         self.user_query = user_query
#         self.chat_history = []
#         self.result = None
#         self.final_summary = None  # Stores final descriptive output

#     def create_group_chat(self) -> autogen.GroupChat:
#         """
#         Creates and configures the group chat with all necessary agents.
#         """
#         agents = [
#             user_proxy_agent,
#             availability_check_agent,
#             location_selection_agent,
#             finance_agent,
#             final_aggregator_agent
#         ]

#         return autogen.GroupChat(
#             agents=agents,
#             messages=[],
#             max_round=10,
#             speaker_selection_method="round_robin"
#         )

#     def create_chat_manager(self, group_chat: autogen.GroupChat) -> autogen.GroupChatManager:
#         """
#         Creates the group chat manager with proper configuration.
#         """
#         return autogen.GroupChatManager(
#             groupchat=group_chat,
#             llm_config=final_aggregator_agent.llm_config
#         )

#     def extract_final_summary(self, content: str) -> str:
#         """
#         Extracts the final summary using direct indexing instead of regex.
#         """
#         summary_marker = "Final Summary"
#         lower_content = content.lower()
        
#         # Find the first occurrence of "Final Summary"
#         index = lower_content.find(summary_marker.lower())

#         if index != -1:
#             return content[index + len(summary_marker):].strip()

#         return "Summary not available."

#     def process_query(self):
#         """
#         Processes the user query through the multi-agent system.
#         """
#         print("Starting query processing...")

#         group_chat = self.create_group_chat()
#         manager = self.create_chat_manager(group_chat)

#         initial_message = (
#             "Process this advertising request and ensure each agent provides a response in valid JSON format.\n\n"
#             "Required steps and response formats:\n"
#             "1. Availability Check Agent: Return JSON with 'available_spots' array\n"
#             "2. Location Selection Agent: Return JSON with 'selected_locations' array\n"
#             "3. Finance Agent: Return JSON with 'financial_analysis' object\n"
#             "4. Final Aggregator: Return structured JSON output **AND** a human-readable summary at the end.\n\n"
#             f"User Query: {self.user_query}\n\n"
#             "Context:\n"
#             f"{json.dumps({'inventory_data': self.inventory_data}, indent=2)}"
#         )

#         try:
#             print("Initiating chat with agents...")
#             chat_response = user_proxy_agent.initiate_chat(manager, message=initial_message)

#             self.chat_history = group_chat.messages
#             print(f"Total messages in chat history: {len(self.chat_history)}")

#             extracted_json = None  # Variable to hold the final extracted JSON
#             extracted_summary = None  # Variable to hold the final human-readable summary

#             for idx, message in enumerate(self.chat_history):
#                 if not isinstance(message, dict):
#                     print(f"\nMessage {idx + 1} is not a dictionary. Skipping.")
#                     continue

#                 print(f"\nMessage {idx + 1}:")
#                 print(f"Raw Message: {json.dumps(message, indent=2)}")  # Debug full message
                
#                 content = message.get("content", "").strip()

#                 # Extract JSON from Markdown code block (```json ... ```)
#                 json_match = content.find("```json")
#                 if json_match != -1:
#                     try:
#                         json_start = content.find("{", json_match)
#                         json_end = content.rfind("}")
#                         extracted_json = json.loads(content[json_start:json_end+1])
#                         print(f"Successfully extracted JSON from Message {idx + 1}")
#                     except json.JSONDecodeError:
#                         print(f"JSON decoding failed for Message {idx + 1}")
#                         continue

#                 # Extract final summary using indexing
#                 summary = self.extract_final_summary(content)
#                 if summary and summary != "Summary not available.":
#                     extracted_summary = summary
#                     print(f"Successfully extracted Final Summary from Message {idx + 1}")

#             if extracted_json:
#                 self.result = extracted_json
#             else:
#                 print("No valid JSON results found in any message")
#                 self.result = {"error": "No valid results from any agent"}

#             if extracted_summary:
#                 self.final_summary = extracted_summary
#             else:
#                 print("No final summary found in any message")
#                 self.final_summary = "Summary not available."

#         except Exception as e:
#             print(f"Error during chat processing: {str(e)}")
#             self.result = {"error": f"Processing failed: {str(e)}"}
#             self.final_summary = "Error encountered during processing."

#     def run(self) -> Dict[str, Any]:
#         """
#         Runs the complete inference process and returns both JSON results and a final summary.
#         """
#         print("Starting Inference...")
#         self.process_query()
#         print("Inference complete.")

#         if self.result:
#             print(f"Final result type: {type(self.result)}")
#             print(f"Final result contents: {json.dumps(self.result, indent=2)}")

#         print("\n===== Final Summary =====")
#         print(self.final_summary)

#         return {
#             "json_result": self.result,
#             "final_summary": self.final_summary
#         }

