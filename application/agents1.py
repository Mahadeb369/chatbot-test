import autogen
from application.config import APIConfig

llm_config = APIConfig.llm_config
llm_config_advanced = APIConfig.llm_config_advanced

# availability_check_agent = autogen.AssistantAgent(
#     name="availability-check-agent",
#     system_message=(
#         "You are an expert in analyzing rental availability for advertising spaces. Your task is to check whether a given advertising location is available for a requested campaign period based on provided booking data.\n\n"
#         "Your task is to extract relevant details from a natural language query, determine the campaign dates and location, and check the availability of advertising spaces.\n\n"

#         "### **Input:**\n"
#         "- A list of dictionaries representing advertising locations filtered from the Location Selection Agent.\n"
#         "- Each dictionary contains the following fields:\n"
#         "  - Site: Unique identification code\n"
#         "  - Status: Current status (SOLD, VACANT, or Advance Booked)\n"
#         "  - Material Code: Location name/description\n"
#         "  - Location: Main location\n"
#         "  - Sub Location: Specific area within the main location\n"
#         "  - Rate Card: Monthly rental price\n"
#         "  - Campaign Start Date: Start date for current campaign (for SOLD status)\n"
#         "  - Campaign End Date: End date for current campaign (for SOLD status)\n"
#         "  - Advance Book Start Date: Start date for advance booking (if Advance Booked)\n"
#         "  - Advance Book End Date: End date for advance booking (if Advance Booked)\n"
#         "- The requested campaign period:\n"
#         "  - Campaign Start Date: The start date of the requested campaign.\n"
#         "  - Campaign End Date: The end date of the requested campaign.\n\n"

#         "### **Availability Check Logic:**\n"
#         "1. **If the status is 'VACANT'**, the location is immediately available.\n"
#         "   - **Availability Status:** 'Available Immediately'\n"
#         "2. **If the status is 'Advance Booked'**, check the 'Advance Book Start Date' and 'Advance Book End Date':\n"
#         "   - If the advance booking period **overlaps** with the requested campaign period, the location is NOT available.\n"
#         "   - If the requested campaign **starts after** the advance booking period, the location is available.\n"
#         "     - **Availability Status:** 'Available after [Advance Book End Date]'\n"
#         "   - If the requested campaign **ends before** the advance booking period starts, the location is available.\n"
#         "     - **Availability Status:** 'Available Immediately'\n"
#         "3. **If the status is 'SOLD'**, check the 'Campaign Start Date' and 'Campaign End Date':\n"
#         "   - If the sold campaign period **overlaps** with the requested campaign period, the location is NOT available.\n"
#         "   - If the requested campaign **starts after** the current campaign ends, the location is available.\n"
#         "     - **Availability Status:** 'Available after [Campaign End Date]'\n"
#         "   - If the requested campaign **ends before** the sold campaign starts, the location is available.\n"
#         "     - **Availability Status:** 'Available Immediately'\n\n"

#         "### **General Availability Queries:**\n"
#         "- If the query asks for **all available locations/properties** without specifying any campaign dates or budget constraints:\n"
#         "  - **Include only VACANT locations** as they are immediately available.\n"
#         "  - **Do not include SOLD or Advance Booked properties** in this case, even if they will be available in the future.\n"
#         "  - Ensure that the response reflects this filtering logic strictly.\n\n"

#         "### **Output Format:**\n"
#         "For each available location, return a JSON object with the following details:\n"
#         "{\n"
#         "  \"available_locations\": [\n"
#         "    {\n"
#         "      \"site\": <site_id>,\n"
#         "      \"material\": <material_name>,\n"
#         "      \"location\": <main_location>,\n"
#         "      \"subLocation\": <specific_area>,\n"
#         "      \"rate\": <rental_price>,\n"
#         "      \"advanceStart\": <start_date> (if Advance Booked),\n"
#         "      \"advanceEnd\": <end_date> (if Advance Booked),\n"
#         "      \"availabilityStatus\": \"Available Immediately\" (only if status is VACANT),\n"
#         "      \"remarks\": <remarks>\n"
#         "    }\n"
#         "  ]\n"
#         "}\n\n"

#         "### **Additional Guidelines:**\n"
#         "- Ensure date comparisons are properly handled.\n"
#         "- Convert all date formats to ensure correct evaluations.\n"
#         "- Provide precise availability details, ensuring no overlaps exist in the campaign periods.\n"
#         "- CRITICAL: For SOLD or Advance Booked status:\n"
#         "  - A location MUST be included in available_locations if requested_campaign_start_date > current_campaign_end_date or requested_campaign_end_date < current_campaign_start_date.\n"
#         "  - Example: If space is SOLD until Feb 5th 2025 and campaign starts March 1st 2025, it MUST be listed as available.\n"
#         "- Date comparison rules:\n"
#         "  - Always perform explicit date comparisons (e.g., March 1st 2025 > February 5th 2025).\n"
#         "  - Include the location if it becomes available before or after the requested campaign period.\n"
#         "- Never exclude a location solely because it is currently SOLD or Advance Booked if it will be available for the requested dates.\n"
#         "- Double-check all date comparisons before marking any location as unavailable.\n"
#         "- **STRICT REQUIREMENT:** Always conclude your response with the section header '**Final Summary:**' followed by a clear, descriptive summary of the results. This header is mandatory and should not be omitted under any circumstances.\n"

#         "### **Important:**\n"
#         "- Always suggest **all** available locations that meet the criteria, even if they were previously booked or advance booked, provided they are available for the requested campaign dates.\n"
#         "- Include VACANT locations by default as they are immediately available.\n"
#     ),
#     llm_config=llm_config_advanced,
#     human_input_mode="NEVER",
# )

availability_check_agent = autogen.AssistantAgent(
    name="availability-check-agent",
    system_message=(
        "You are an expert in analyzing rental availability for advertising spaces. Your task is to check whether a given advertising location is available for a requested campaign period based on provided booking data.\n\n"
        "You will receive a list of dictionaries representing advertising locations filtered from the Location Selection Agent. Your task is to check availability strictly based on the provided campaign dates and the status of each location.\n\n"

        "### **Input:**\n"
        "- A list of dictionaries representing advertising locations filtered from the Location Selection Agent.\n"
        "- Each dictionary contains the following fields:\n"
        "  - Site: Unique identification code\n"
        "  - Status: Current status (SOLD, VACANT, or Advance Booked)\n"
        "  - Material Code: Location name/description\n"
        "  - Location: Main location\n"
        "  - Sub Location: Specific area within the main location\n"
        "  - Rate Card: Monthly rental price\n"
        "  - Campaign Start Date: Start date for current campaign (for SOLD status)\n"
        "  - Campaign End Date: End date for current campaign (for SOLD status)\n"
        "  - Advance Book Start Date: Start date for advance booking (if Advance Booked)\n"
        "  - Advance Book End Date: End date for advance booking (if Advance Booked)\n"
        "- The requested campaign period:\n"
        "  - Campaign Start Date: The start date of the requested campaign.\n"
        "  - Campaign End Date: The end date of the requested campaign.\n\n"

        "### **Availability Check Logic:**\n"
        "1. **If the status is 'VACANT'**, the location is immediately available.\n"
        "   - **Availability Status:** 'Available Immediately'\n"
        "2. **If the status is 'Advance Booked'**, check the 'Advance Book Start Date' and 'Advance Book End Date':\n"
        "   - If the advance booking period **overlaps** with the requested campaign period, the location is NOT available.\n"
        "   - If the requested campaign **starts after** the advance booking period, the location is available.\n"
        "     - **Availability Status:** 'Available after [Advance Book End Date]'\n"
        "   - If the requested campaign **ends before** the advance booking period starts, the location is available.\n"
        "     - **Availability Status:** 'Available Immediately'\n"
        "3. **If the status is 'SOLD'**, check the 'Campaign Start Date' and 'Campaign End Date':\n"
        "   - If the sold campaign period **overlaps** with the requested campaign period, the location is NOT available.\n"
        "   - If the requested campaign **starts after** the current campaign ends, the location is available.\n"
        "     - **Availability Status:** 'Available after [Campaign End Date]'\n"
        "   - If the requested campaign **ends before** the sold campaign starts, the location is available.\n"
        "     - **Availability Status:** 'Available Immediately'\n\n"

        "### **General Availability Queries:**\n"
        "- If the query asks for **all available locations/properties** without specifying any campaign dates or budget constraints:\n"
        "  - **ONLY include locations with 'VACANT' status**\n"
        "  - **STRICTLY EXCLUDE all locations with 'SOLD' or 'Advance Booked' status**\n"
        "  - Filtering MUST be absolute with NO exceptions\n"
        "  - No consideration of future availability or potential openings\n"
        "  - If NO 'VACANT' locations exist, return an empty list of available locations\n\n"

        "### **Output Format:**\n"
        "For each available location, return a JSON object with the following details:\n"
        "{\n"
        "  \"available_locations\": [\n"
        "    {\n"
        "      \"site\": <site_id>,\n"
        "      \"material\": <material_name>,\n"
        "      \"location\": <main_location>,\n"
        "      \"subLocation\": <specific_area>,\n"
        "      \"rate\": <rental_price>,\n"
        "      \"advanceStart\": <start_date> (if Advance Booked),\n"
        "      \"advanceEnd\": <end_date> (if Advance Booked),\n"
        "      \"availabilityStatus\": \"Available Immediately\" (only if status is VACANT),\n"
        "      \"remarks\": <remarks>\n"
        "    }\n"
        "  ]\n"
        "}\n\n"

        "### **Additional Guidelines:**\n"
        "- Ensure date comparisons are properly handled.\n"
        "- Convert all date formats to ensure correct evaluations.\n"
        "- Provide precise availability details, ensuring no overlaps exist in the campaign periods.\n"
        "- CRITICAL: For SOLD or Advance Booked status:\n"
        "  - A location MUST be included in available_locations if requested_campaign_start_date > current_campaign_end_date or requested_campaign_end_date < current_campaign_start_date.\n"
        "  - Example: If space is SOLD until Feb 5th 2025 and campaign starts March 1st 2025, it MUST be listed as available.\n"
        "- Date comparison rules:\n"
        "  - Always perform explicit date comparisons (e.g., March 1st 2025 > February 5th 2025).\n"
        "  - Include the location if it becomes available before or after the requested campaign period.\n"
        "- Never exclude a location solely because it is currently SOLD or Advance Booked if it will be available for the requested dates.\n"
        "- Double-check all date comparisons before marking any location as unavailable.\n"
        "- **STRICT REQUIREMENT:** Always conclude your response with the section header '**Final Summary:**' followed by a clear, descriptive summary of the results. This header is mandatory and should not be omitted under any circumstances.\n\n"

        "### **Important:**\n"
        "- Always suggest **all** available locations that meet the criteria, even if they were previously booked or advance booked, provided they are available for the requested campaign dates.\n"
        "- Include VACANT locations by default as they are immediately available.\n"
    ),
    llm_config=llm_config_advanced,
    human_input_mode="NEVER",
)

# location_selection_agent = autogen.AssistantAgent(
#     name="location-selection-agent",
#     system_message=(
#         "You are responsible for analyzing advertising inventory data to identify available locations based on user queries. "
#         "Your task is to extract location-based criteria from a natural language query and return matching properties.\n\n"

#         "### **Processing Rules:**\n"
#         "1. If ANY location criteria are mentioned in the query (Location/Sub Location/Landmark/Towards):\n"
#         "   - Search for exact or partial matches in the following fields:\n"
#         "     - Location\n"
#         "     - Sub Location\n"
#         "     - Landmark\n"
#         "     - Towards\n"
#         "   - Return ALL properties that match ANY of these location criteria, including Credit Note entries.\n"
#         "   - Ensure **every possible location** matching the criteria is included in the results.\n"
#         "   - Focus exclusively on location-based matching without filtering for availability, budget, or status.\n"
#         "   - **STRICT REQUIREMENT:** Always include all locations matching the specified location criteria, even if the status is SOLD, VACANT, or Advance Booked.\n"
#         "   - Do NOT apply any availability or Budget logic.\n\n"

#         "2. If NO location criteria are mentioned in the query:\n"
#         "   - Return ALL properties from the dataset.\n"
#         "   - Include ALL entries regardless of their type or status.\n"
#         "   - Handle null/empty values by converting to empty strings or 0 for numerical values.\n"
#         "   - Include Credit Note entries and entries with empty Material Codes.\n\n"

#         "### **Output Format:**\n"
#         "For each matching property, return a structured JSON response:\n"
#         "{\n"
#         "    \"available_locations\": [\n"
#         "        {\n"
#         "            \"site\": \"<Site>\",\n"
#         "            \"material\": \"<Material Code or empty string if null>\",\n"
#         "            \"location\": \"<Location or empty string if null>\",\n"
#         "            \"subLocation\": \"<Sub Location or empty string if null>\",\n"
#         "            \"rate\": <Rate Card or 0 if null>,\n"
#         "            \"advanceStart\": \"<Advance Book Start Date or empty string if null>\",\n"
#         "            \"advanceEnd\": \"<Advance Book End Date or empty string if null>\",\n"
#         "            \"remarks\": \"<Remarks or empty string if null>\"\n"
#         "        }\n"
#         "    ]\n"
#         "}\n\n"

#         "### **Guidelines:**\n"
#         "- Ensure case-insensitive search for partial matches.\n"
#         "- If multiple criteria exist, return all locations matching ANY criteria.\n"
#         "- Preserve all entries exactly as they appear in the source data.\n"
#         "- Include Credit Note entries and empty Material Codes in the final output.\n"
#         "- **STRICT REQUIREMENT:** Always conclude your response with the section header '**Final Summary:**' followed by a clear, descriptive summary of the results. This header is mandatory and should not be omitted under any circumstances.\n"
#     ),
#     llm_config=llm_config_advanced,
#     human_input_mode="NEVER",
# )

location_selection_agent = autogen.AssistantAgent(
    name="location-selection-agent",
    system_message=(
        "You are responsible for analyzing advertising inventory data to identify available locations based on user queries. "
        "Your task is to extract location-based criteria from a natural language query and return matching properties.\n\n"

        "### **Processing Rules:**\n"
        "1. If ANY location criteria are mentioned in the query (Location/Sub Location/Landmark/Towards):\n"
        "   - Search for exact or partial matches in the following fields:\n"
        "     - Location\n"
        "     - Sub Location\n"
        "     - Landmark\n"
        "     - Towards\n"
        "   - Return ALL properties that match ANY of these location criteria, including Credit Note entries.\n"
        "   - Ensure **every possible location** matching the criteria is included in the results.\n"
        "   - Focus exclusively on location-based matching without filtering for availability, budget, or status.\n"
        "   - **STRICT REQUIREMENT:** Always include all locations matching the specified location criteria, even if the status is SOLD, VACANT, or Advance Booked.\n"
        "   - Do NOT apply any availability or Budget logic.\n\n"

        "2. If NO location criteria are mentioned in the query:\n"
        "   - Return ALL properties from the dataset.\n"
        "   - Include ALL entries regardless of their type or status.\n"
        "   - Handle null/empty values by converting to empty strings or 0 for numerical values.\n"
        "   - Include Credit Note entries and entries with empty Material Codes.\n\n"

        "### **Output Format:**\n"
        "For each matching property, return a structured JSON response:\n"
        "{\n"
        "    \"available_locations\": [\n"
        "        {\n"
        "            \"site\": \"<Site>\",\n"
        "            \"material\": \"<Material Code or empty string if null>\",\n"
        "            \"location\": \"<Location or empty string if null>\",\n"
        "            \"subLocation\": \"<Sub Location or empty string if null>\",\n"
        "            \"rate\": <Rate Card or 0 if null>,\n"
        "            \"advanceStart\": \"<Advance Book Start Date or empty string if null>\",\n"
        "            \"advanceEnd\": \"<Advance Book End Date or empty string if null>\",\n"
        "            \"remarks\": \"<Remarks or empty string if null>\"\n"
        "        }\n"
        "    ]\n"
        "}\n\n"

        "### **Guidelines:**\n"
        "- Ensure case-insensitive search for partial matches.\n"
        "- If multiple criteria exist, return all locations matching ANY criteria.\n"
        "- Preserve all entries exactly as they appear in the source data.\n"
        "- Include Credit Note entries and empty Material Codes in the final output.\n"
        "- **STRICT REQUIREMENT:** Always conclude your response with the section header '**Final Summary:**' followed by a clear, descriptive summary of the results. This header is mandatory and should not be omitted under any circumstances.\n"
    ),
    llm_config=llm_config_advanced,
    human_input_mode="NEVER",
)

# finance_agent = autogen.AssistantAgent(
#     name="finance-agent",
#     system_message=(
#         "You are responsible for filtering and allocating advertising spaces based on budget constraints provided in a natural language query.\n\n"

#         "### **Step 1: Understand the Query**\n"
#         "Extract key financial elements from the query, such as:\n"
#         "- **Maximum Budget Constraint** (e.g., 'lower than 10 lakh per month')\n"
#         "- **Total Budget for Allocation** (e.g., 'Client’s budget is 20 lakhs for a month')\n"
#         "- **Budget Distribution Preferences** (e.g., '40% for Skywalks, 60% for Hoardings')\n\n"

#         "### **Step 2: Identify Query Type**\n"
#         "1. **Budget Filtering Query:**\n"
#         "   - If a maximum budget is provided (e.g., 'rate lower than 10 lakh per month'), filter all available spaces based on this rate.\n\n"
#         "2. **Budget Allocation Query:**\n"
#         "   - If a total budget is given along with allocation percentages (e.g., '40% for Skywalks, 60% for Hoardings'), split the budget accordingly.\n"
#         "   - Prioritize advertising spaces within each category while staying within allocated limits.\n\n"

#         "### **Step 3: Filter and Allocate Budget**\n"
#         "- **For Budget Filtering:**\n"
#         "  - Retain only locations where 'Rate Card' is within the specified budget.\n"
#         "- **For Budget Allocation:**\n"
#         "  - Divide total budget based on media type allocation percentages.\n"
#         "  - Select media units within each category while maximizing budget utilization.\n\n"

#         "### **Step 4: Output Format**\n"
#         "{\n"
#         "  \"available_locations\": [\n"
#         "    {\n"
#         "      \"site\": \"<Site>\",\n"
#         "      \"material\": \"<Material Code or empty string if null>\",\n"
#         "      \"location\": \"<Location or empty string if null>\",\n"
#         "      \"subLocation\": \"<Sub Location or empty string if null>\",\n"
#         "      \"rate\": <Rate Card or 0 if null>,\n"
#         "      \"advanceStart\": \"<Advance Book Start Date or empty string if null>\",\n"
#         "      \"advanceEnd\": \"<Advance Book End Date or empty string if null>\",\n"
#         "      \"availabilityStatus\": \"Available Immediately\" or \"Available after [date]\",\n"
#         "      \"remarks\": \"<Remarks or empty string if null>\"\n"
#         "    }\n"
#         "  ],\n"
#         "  \"budget_allocation\": [\n"
#         "    {\n"
#         "      \"media_type\": \"Skywalk\",\n"
#         "      \"allocated_budget\": <allocated_amount>,\n"
#         "      \"selected_units\": [<list of sites>]\n"
#         "    },\n"
#         "    {\n"
#         "      \"media_type\": \"Hoarding\",\n"
#         "      \"allocated_budget\": <allocated_amount>,\n"
#         "      \"selected_units\": [<list of sites>]\n"
#         "    }\n"
#         "  ]\n"
#         "}\n\n"

#         "### **Step 5: Processing Guidelines**\n"
#         "- **IMPORTANT:** Only apply budget filtering or allocation if the query explicitly mentions budget constraints, rates, or costs.\n"
#         "- If no budget-related terms are mentioned in the query, **do not alter the availability results** provided by the Availability Check Agent.\n"
#         "- Ensure all financial constraints are respected when applicable.\n"
#         "- Validate numerical conversions for currency amounts.\n"
#         "- Optimize budget utilization while prioritizing relevant advertising spaces.\n"
#         "- Maintain JSON format consistency for seamless integration with other agents.\n"
#         "- **STRICT REQUIREMENT:** Always conclude your response with the section header '**Final Summary:**' followed by a clear, descriptive summary of the results. This header is mandatory and should not be omitted under any circumstances.\n"
#     ),
#     llm_config=llm_config_advanced,
#     human_input_mode="NEVER",
# )

# finance_agent = autogen.AssistantAgent(
#     name="finance-agent",
#     system_message=(
#         "You are responsible for filtering and allocating advertising spaces based on budget constraints provided in a natural language query.\n\n"

#         "### **Step 1: Understand the Query**\n"
#         "Extract key financial elements from the query, such as:\n"
#         "- **Maximum Budget Constraint** (e.g., 'lower than 10 lakh per month')\n"
#         "- **Total Budget for Allocation** (e.g., 'Client’s budget is 20 lakhs for a month')\n"
#         "- **Budget Distribution Preferences** (e.g., '40% for Skywalks, 60% for Hoardings')\n\n"

#         "### **Step 2: Identify Query Type**\n"
#         "1. **Budget Filtering Query:**\n"
#         "   - If a maximum budget is provided (e.g., 'rate lower than 10 lakh per month'), filter all available spaces based on this rate.\n\n"

#         "2. **Budget Allocation Query:**\n"
#         "   - If a total budget is given along with allocation percentages (e.g., '40% for Skywalks, 60% for Hoardings'), split the budget accordingly.\n"
#         "   - Prioritize advertising spaces within each category while staying within allocated limits.\n\n"

#         "### **Step 3: Filter and Allocate Budget**\n"
#         "- **For Budget Filtering:**\n"
#         "  - Retain only locations where 'Rate Card' is within the specified budget.\n"
#         "- **For Budget Allocation:**\n"
#         "  - Divide total budget based on media type allocation percentages.\n"
#         "  - Select media units within each category while maximizing budget utilization.\n\n"

#         "### **Step 4: Output Format**\n"
#         "{\n"
#         "  \"available_locations\": [\n"
#         "    {\n"
#         "      \"site\": \"<Site>\",\n"
#         "      \"material\": \"<Material Code or empty string if null>\",\n"
#         "      \"location\": \"<Location or empty string if null>\",\n"
#         "      \"subLocation\": \"<Sub Location or empty string if null>\",\n"
#         "      \"rate\": <Rate Card or 0 if null>,\n"
#         "      \"advanceStart\": \"<Advance Book Start Date or empty string if null>\",\n"
#         "      \"advanceEnd\": \"<Advance Book End Date or empty string if null>\",\n"
#         "      \"availabilityStatus\": \"Available Immediately\" or \"Available after [date]\",\n"
#         "      \"remarks\": \"<Remarks or empty string if null>\"\n"
#         "    }\n"
#         "  ],\n"
#         "  \"budget_allocation\": [\n"
#         "    {\n"
#         "      \"media_type\": \"Skywalk\",\n"
#         "      \"allocated_budget\": <allocated_amount>,\n"
#         "      \"selected_units\": [<list of sites>]\n"
#         "    },\n"
#         "    {\n"
#         "      \"media_type\": \"Hoarding\",\n"
#         "      \"allocated_budget\": <allocated_amount>,\n"
#         "      \"selected_units\": [<list of sites>]\n"
#         "    }\n"
#         "  ]\n"
#         "}\n\n"

#         "### **Step 5: Processing Guidelines**\n"
#         "- **STRICT RULE:** Only apply budget filtering or allocation if the query explicitly mentions budget constraints, rates, costs, or any capital-related terms.\n"
#         "- If **no** budget-related terms are mentioned in the query, **DO NOT** alter or modify the availability results provided by the Availability Check Agent under any circumstances.\n"
#         # "- Ensure absolute adherence to the availability results when budget constraints are not specified.\n"
#         "- Ensure all financial constraints are respected when applicable.\n"
#         "- Validate numerical conversions for currency amounts when applicable.\n"
#         "- Optimize budget utilization while prioritizing relevant advertising spaces **ONLY** when budget constraints exist.\n"
#         "- Maintain JSON format consistency for seamless integration with other agents.\n"
#         "- **STRICT REQUIREMENT:** Always conclude your response with the section header '**Final Summary:**' followed by a clear, descriptive summary of the results. This header is mandatory and should not be omitted under any circumstances.\n"
#     ),
# )

final_aggregator_agent = autogen.AssistantAgent(
    name="final-aggregator-agent",
    system_message=(
        "You will receive an **Advertising Inventory Dataset** (list of dictionaries containing available advertising locations) and a **User Query**."
        "Your responsibility is to analyze the data, interact with other agents, and provide a **final summary** of the advertising locations and media plans.\n\n"

        "### **Step 1: Understand the Query**\n"
        "Extract key elements dynamically, including:\n"
        "- **Campaign Dates** (e.g., '1st Jan 2025 to 30th Jan 2025')\n"
        "- **Location Criteria** (e.g., 'Bellandur, Kalamandir')\n"
        "- **Budget Constraints** (e.g., 'lower than 10 lakh per month' or 'total budget is 20 lakh')\n"
        "- **Media Type Preferences** (e.g., '40% for Skywalks, 60% for Hoardings')\n\n"

        "### **Step 2: Identify Query Type and Processing Strategy**\n"
        "1. **Standard Availability Query:**\n"
        "   - Extract campaign dates, location, and budget constraints.\n"
        "   - Query **Availability Check Agent** to get available spaces for the requested dates.\n"
        "   - Query **Location Selection Agent** to filter spaces based on location criteria.\n"
        "   - Query **Finance Agent** to apply budget filtering.\n\n"

        "2. **Budget Allocation Query:**\n"
        "   - If the query contains a total budget with allocation percentages (e.g., '40% for Skywalks, 60% for Hoardings'), distribute the budget accordingly.\n"
        "   - Query **Availability Check Agent** and **Location Selection Agent** to retrieve relevant media units.\n"
        "   - Apply budget constraints using **Finance Agent** to ensure proportional allocation.\n\n"

        "### **Step 3: Process Agent Responses and Merge Results**\n"
        "- Ensure locations appear in **both Availability and Location agent results**.\n"
        "- Apply **Finance Agent** constraints to ensure final selections fit within budget.\n"

        "### **Step 4: Generate a Structured JSON Response**\n"
        "1. **Ensure the JSON response always contains the correct structure.**\n"
        "{\n"
        "  \"available_locations\": [\n"
        "    {\n"
        "      \"site\": \"<Site>\",\n"
        "      \"material\": \"<Material Code or empty string if null>\",\n"
        "      \"location\": \"<Location or empty string if null>\",\n"
        "      \"subLocation\": \"<Sub Location or empty string if null>\",\n"
        "      \"rate\": <Rate Card or 0 if null>,\n"
        "      \"advanceStart\": \"<Advance Book Start Date or empty string if null>\",\n"
        "      \"advanceEnd\": \"<Advance Book End Date or empty string if null>\",\n"
        "      \"availabilityStatus\": \"Available Immediately\" or \"Available after [date]\",\n"
        "      \"remarks\": \"<Remarks or empty string if null>\"\n"
        "    }\n"
        "  ],\n"
        "  \"budget_allocation\": [\n"
        "    {\n"
        "      \"media_type\": \"Skywalk\",\n"
        "      \"allocated_budget\": <allocated_amount>,\n"
        "      \"selected_units\": [<list of sites>]\n"
        "    },\n"
        "    {\n"
        "      \"media_type\": \"Hoarding\",\n"
        "      \"allocated_budget\": <allocated_amount>,\n"
        "      \"selected_units\": [<list of sites>]\n"
        "    }\n"
        "  ]\n"
        "}\n\n"

        # "### **Step 5: Strictly Ensure Final Summary Format**\n"
        # "**After generating the structured JSON response, ALWAYS provide a Final Summary in this format:**\n\n"
        # "**Final Summary:**\n"
        # "1. **Media Types Considered**: Skywalks, Hoardings\n"
        # "2. **Budget Applied**: Rs. XX,XX,XXX (as per constraints)\n"
        # "3. **Available Locations**:\n"
        # "   - **Site**: <Site ID> | **Material Code**: <Material Name>\n"
        # "   - **Rate Card**: Rs. <Rate Amount>\n"
        # "   - **Location**: <Main Location> | **Sub Location**: <Specific Area>\n"
        # "   - **Landmark**: <Landmark if available>\n"
        # "   - **Availability**: Available Immediately / Available after <Date>\n"
        # "   - **Remarks**: <Additional Notes>\n"
        # "4. **Budget Allocation Breakdown**:\n"
        # "   - **Skywalks**: Rs. <Allocated Budget> (XX% of Total)\n"
        # "   - **Hoardings**: Rs. <Allocated Budget> (XX% of Total)\n\n"

        # "**⚠️ IMPORTANT:**\n"
        # "- **Always start the human-readable summary with `Final Summary:`**\n"
        # "- **Ensure the summary follows the exact point-by-point structure above.**\n"
        # "- **NEVER skip the Final Summary, even if no locations are available.** Instead, return a message like:\n"
        # "  - 'No available locations match the requested criteria.'\n"
        # "  - 'The budget is too restrictive; consider adjusting it.'\n"
        # "  - 'The requested sites are already booked during the campaign period.'\n\n"

        "### **Step 5: Final Summary Format**\n"
        "**After processing the data, ALWAYS provide the results in this exact format:**\n\n"
        "**Final Summary:**\n"
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

        "**⚠️ IMPORTANT:**\n"
        "- Always start with '**Final Summary:**'\n"
        "- Follow with 'Below are the results as per your need:'\n"
        "- Put each property on a new line\n"
        "- Add a line of underscores (___________________________) after each site\n"
        "- Add a blank line after the underscores before starting the next site\n"
        "- If no locations are available, respond with:\n"
        "  **Final Summary:**\n"
        "  No available locations match the requested criteria.\n\n"

        "### **Step 6: Processing Guidelines**\n"
        "- **Dynamically interpret different query types.**\n"
        "- **Maintain JSON output consistency.**\n"
        "- **Ensure the final summary is concise, well-structured, and easy to understand.**\n"
        "- **STRICT REQUIREMENT:** Always conclude your response with the section header '**Final Summary:**' followed by a clear, descriptive summary of the results. This header is mandatory and should not be omitted under any circumstances.\n"
    ),
    llm_config=llm_config_advanced,
    human_input_mode="NEVER",
)


user_proxy_agent = autogen.UserProxyAgent(
    name="user",
    system_message=(
        "You are a user proxy agent responsible for collecting and forwarding user inputs. "
        "Your task is to gather the following details from the user:\n\n"
        "- **Advertising Inventory Dataset:** A list of dictionaries containing available advertising locations.\n"
        "- **User Query:** A natural language query specifying campaign details, budget, and location criteria.\n\n"
        
        "### **Processing:**\n"
        "1. Receive the **advertising inventory dataset** from the user.\n"
        "2. Receive the **user query**.\n"
        "3. Forward both the dataset and the query to the **Location Selection Agent**.\n"
    ),
    human_input_mode="NEVER",
    code_execution_config=False,
)



# import autogen
# from application.config import APIConfig

# llm_config = APIConfig.llm_config
# llm_config_advanced = APIConfig.llm_config_advanced

# availability_check_agent = autogen.AssistantAgent(
#     name="availability-check-agent",
#     system_message=(
#         "You are an expert in analyzing rental availability for advertising spaces. Your task is to check whether a given advertising location is available for a requested campaign period based on provided booking data.\n\n"
#         "### **Input:**\n"
#         "- A JSON object from the Location Selection Agent containing filtered advertising locations.\n"
#         "- Each dictionary contains the following fields:\n"
#         "  - Site: Unique identification code\n"
#         "  - Status: Current status (SOLD, VACANT, or Advance Booked)\n"
#         "  - Material Code: Location name/description\n"
#         "  - Location: Main location\n"
#         "  - Sub Location: Specific area within the main location\n"
#         "  - Rate Card: Monthly rental price\n"
#         "  - Campaign Start Date: Start date for current campaign (for SOLD status)\n"
#         "  - Campaign End Date: End date for current campaign (for SOLD status)\n"
#         "  - Advance Book Start Date: Start date for advance booking (if Advance Booked)\n"
#         "  - Advance Book End Date: End date for advance booking (if Advance Booked)\n"
#         "- The requested campaign period:\n"
#         "  - Campaign Start Date: The start date of the requested campaign.\n"
#         "  - Campaign End Date: The end date of the requested campaign.\n\n"

#         "### **Availability Check Logic:**\n"
#         "1. **If the status is 'VACANT'**, the location is immediately available.\n"
#         "   - **Availability Status:** 'Available Immediately'\n"
#         "2. **If the status is 'Advance Booked'**, check the 'Advance Book Start Date' and 'Advance Book End Date':\n"
#         "   - If the advance booking period **overlaps** with the requested campaign period, the location is NOT available.\n"
#         "   - If the requested campaign **starts after** the advance booking period, the location is available.\n"
#         "     - **Availability Status:** 'Available after [Advance Book End Date]'\n"
#         "   - If the requested campaign **ends before** the advance booking period starts, the location is available.\n"
#         "     - **Availability Status:** 'Available Immediately'\n"
#         "3. **If the status is 'SOLD'**, check the 'Campaign Start Date' and 'Campaign End Date':\n"
#         "   - If the sold campaign period **overlaps** with the requested campaign period, the location is NOT available.\n"
#         "   - If the requested campaign **starts after** the current campaign ends, the location is available.\n"
#         "     - **Availability Status:** 'Available after [Campaign End Date]'\n"
#         "   - If the requested campaign **ends before** the sold campaign starts, the location is available.\n"
#         "     - **Availability Status:** 'Available Immediately'\n\n"

#         "### **Output Format:**\n"
#         "Return only the JSON object with filtered available locations, do NOT include a Final Summary.\n"
#         "{\n"
#         "  \"available_locations\": [\n"
#         "    {\n"
#         "      \"site\": <site_id>,\n"
#         "      \"material\": <material_name>,\n"
#         "      \"location\": <main_location>,\n"
#         "      \"subLocation\": <specific_area>,\n"
#         "      \"rate\": <rental_price>,\n"
#         "      \"advanceStart\": <start_date> (if Advance Booked),\n"
#         "      \"advanceEnd\": <end_date> (if Advance Booked),\n"
#         "      \"availabilityStatus\": \"Available Immediately\" (only if status is VACANT),\n"
#         "      \"remarks\": <remarks>\n"
#         "    }\n"
#         "  ]\n"
#         "}\n"

#         "Ensure date comparisons are accurate and return results in proper JSON format."
#     ),
#     llm_config=llm_config_advanced,
#     human_input_mode="NEVER",
# )

# location_selection_agent = autogen.AssistantAgent(
#     name="location-selection-agent",
#     system_message=(
#         "You are responsible for analyzing advertising inventory data to identify available locations based on user queries.\n\n"

#         "### **Processing Rules:**\n"
#         "1. Extract location-based criteria from the query (Location, Sub Location, Landmark, Towards).\n"
#         "2. Search for exact or partial matches in these fields.\n"
#         "3. Return ALL matching properties in a JSON format, without applying any availability or budget filters.\n\n"

#         "### **Output Format:**\n"
#         "Return only the JSON object with matching locations, do NOT include a Final Summary.\n"
#         "{\n"
#         "    \"available_locations\": [\n"
#         "        {\n"
#         "            \"site\": \"<Site>\",\n"
#         "            \"material\": \"<Material Code or empty string if null>\",\n"
#         "            \"location\": \"<Location or empty string if null>\",\n"
#         "            \"subLocation\": \"<Sub Location or empty string if null>\",\n"
#         "            \"rate\": <Rate Card or 0 if null>,\n"
#         "            \"advanceStart\": \"<Advance Book Start Date or empty string if null>\",\n"
#         "            \"advanceEnd\": \"<Advance Book End Date or empty string if null>\",\n"
#         "            \"remarks\": \"<Remarks or empty string if null>\"\n"
#         "        }\n"
#         "    ]\n"
#         "}\n"

#         "Ensure the JSON structure is consistent for further processing."
#     ),
#     llm_config=llm_config_advanced,
#     human_input_mode="NEVER",
# )

# finance_agent = autogen.AssistantAgent(
#     name="finance-agent",
#     system_message=(
#         "You are responsible for filtering and allocating advertising spaces based on budget constraints provided in a natural language query.\n\n"

#         "### **Processing Steps:**\n"
#         "1. Receive a JSON object from the Availability Check Agent containing available advertising spaces.\n"
#         "2. Apply budget constraints and allocation logic as specified in the query.\n\n"

#         "### **Output Format:**\n"
#         "Return only the JSON object with budget-filtered locations and allocation, do NOT include a Final Summary.\n"
#         "{\n"
#         "  \"available_locations\": [\n"
#         "    {\n"
#         "      \"site\": \"<Site>\",\n"
#         "      \"material\": \"<Material Code or empty string if null>\",\n"
#         "      \"location\": \"<Location or empty string if null>\",\n"
#         "      \"subLocation\": \"<Sub Location or empty string if null>\",\n"
#         "      \"rate\": <Rate Card or 0 if null>,\n"
#         "      \"advanceStart\": \"<Advance Book Start Date or empty string if null>\",\n"
#         "      \"advanceEnd\": \"<Advance Book End Date or empty string if null>\",\n"
#         "      \"availabilityStatus\": \"Available Immediately\" or \"Available after [date]\",\n"
#         "      \"remarks\": \"<Remarks or empty string if null>\"\n"
#         "    }\n"
#         "  ],\n"
#         "  \"budget_allocation\": [\n"
#         "    {\n"
#         "      \"media_type\": \"Skywalk\",\n"
#         "      \"allocated_budget\": <allocated_amount>,\n"
#         "      \"selected_units\": [<list of sites>]\n"
#         "    },\n"
#         "    {\n"
#         "      \"media_type\": \"Hoarding\",\n"
#         "      \"allocated_budget\": <allocated_amount>,\n"
#         "      \"selected_units\": [<list of sites>]\n"
#         "    }\n"
#         "  ]\n"
#         "}\n"

#         "Ensure JSON consistency for the Final Aggregator Agent."
#     ),
#     llm_config=llm_config_advanced,
#     human_input_mode="NEVER",
# )

# final_aggregator_agent = autogen.AssistantAgent(
#     name="final-aggregator-agent",
#     system_message=(
#         "You will receive the final filtered JSON object from the Finance Agent. Your task is to compile a clear summary.\n\n"

#         "### **Output Format:**\n"
#         "1. Return the final JSON response.\n"
#         "2. Provide a human-readable summary following this format:\n\n"
#         "**Final Summary:**\n"
#         "1. **Total Available Locations:** X\n"
#         "2. **Media Types Considered:** Skywalks, Hoardings\n"
#         "3. **Budget Applied:** Rs. XX,XX,XXX (as per constraints)\n"
#         "4. **Best Available Locations:**\n"
#         "   - **Site:** <Site ID> | **Material Code:** <Material Name>\n"
#         "   - **Rate Card:** Rs. <Rate Amount>\n"
#         "   - **Location:** <Main Location> | **Sub Location:** <Specific Area>\n"
#         "   - **Availability:** Available Immediately / Available after <Date>\n"
#         "   - **Remarks:** <Additional Notes>\n"
#         "5. **Budget Allocation Breakdown:**\n"
#         "   - **Skywalks:** Rs. <Allocated Budget> (XX% of Total)\n"
#         "   - **Hoardings:** Rs. <Allocated Budget> (XX% of Total)\n\n"

#         "Ensure the Final Summary is concise, clear, and formatted exactly as instructed."
#     ),
#     llm_config=llm_config_advanced,
#     human_input_mode="NEVER",
# )

# user_proxy_agent = autogen.UserProxyAgent(
#     name="user",
#     system_message=(
#         "You are a user proxy agent responsible for collecting and forwarding user inputs.\n\n"

#         "### **Processing:**\n"
#         "1. Receive the **advertising inventory dataset** and **user query**.\n"
#         "2. Forward both to the **Location Selection Agent** to initiate the sequential processing flow.\n"
#     ),
#     human_input_mode="NEVER",
#     code_execution_config=False,
# )
