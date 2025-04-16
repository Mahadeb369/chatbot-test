import openai
import json
import os

api_key = os.getenv("OPEN_AI_API_KEY") or ""
client = openai.OpenAI(api_key=api_key)

# SQL_PROMPT_TEMPLATE = """
# You are an expert SQL query generator. Your task is to generate SQL queries based on a natural language user query. The query should extract relevant records from the public.times_ooh table, following these rules:

# Location and Property Type Filtering:
# - The Property column contains both the city and the media type (e.g., BANGALORE_SKYWALK).
# - If a city (e.g., Bangalore, Mumbai, Chennai) is mentioned, apply filtering **only** on the Property column:
# - Use case-insensitive filtering:
#   Example: To filter for "Skywalks in Bangalore", apply:
#   LOWER("Property") LIKE '%bangalore%' AND LOWER("Property") LIKE '%skywalk%'
# - When filtering by specific locations, always check across all relevant location columns:
#   LOWER("Location") LIKE '%{location}%'
#   OR LOWER("Sub Location") LIKE '%{location}%'
#   OR LOWER("LandMark") LIKE '%{location}%'
#   OR LOWER("Towards") LIKE '%{location}%'

# If mentioned **as on date** in the query:
# - Always take CURRENT_DATE for comparission.

# Availability Logic:
# - Vacant: Directly available.
# - Sold: Available only if there is no overlap between the user’s campaign dates and the existing Campaign Start Date and Campaign End Date:
#   "Status" ILIKE 'SOLD' 
#   AND NOT ('{start_date}' <= "Campaign End Date" AND '{end_date}' >= "Campaign Start Date')
# - Advance Booked: Available only if there is no overlap between the user’s campaign dates and the existing Advance Book Start Date and Advance Book End Date:
#   "Status" ILIKE 'Advance Booked' 
#   AND NOT ('{start_date}' <= "Advance Book End Date" AND '{end_date}' >= "Advance Book Start Date')

# Query Format:
# The SQL query should return the following columns:
# "Site", "Material Code", "Rate Card", "Location", "Sub Location", "LandMark", "Towards", "Property", "Status", 
# "Campaign Start Date", "Campaign End Date", "Advance Book Start Date", "Advance Book End Date"

# Now, generate a SQL query for the following user request:
# """

# SQL_PROMPT_TEMPLATE = """
# You are an expert PostgreSQL query generator. Your task is to generate SQL queries based on a natural language user query. The query should extract relevant records from the public.times_ooh table, following these rules:
# Location and Property Type Filtering:
# - The `Property` column contains both the **city** and **media type** (e.g., `BANGALORE_SKYWALK`).
# - If a **city** (e.g., Bangalore, Mumbai, Chennai) is mentioned, apply filtering **ONLY** on the `Property` column.
# - **DO NOT filter** the city using `"Location"`, `"Sub Location"`, `"LandMark"`, or `"Towards"`.
# - Use case-insensitive filtering:
#   Example: To filter for "Skywalks in Bangalore", apply:
#   LOWER("Property") LIKE '%bangalore%' AND LOWER("Property") LIKE '%skywalk%'
# - If a **specific location within a city** is mentioned (e.g., `"Kalamandir near Silk Board"`):
#   - First, check `"Kalamandir"` across all location columns.
#   - Then, separately check `"Silk Board"` across all location columns.
#   - **Use `AND` between them** so that the Skywalk is near both locations.
#   ( LOWER("Location") LIKE '%kalamandir%'
#   OR LOWER("Sub Location") LIKE '%kalamandir%'
#   OR LOWER("LandMark") LIKE '%kalamandir%'
#   OR LOWER("Towards") LIKE '%kalamandir%' )
#   AND ( LOWER("Location") LIKE '%silk board%'
#   OR LOWER("Sub Location") LIKE '%silk board%'
#   OR LOWER("LandMark") LIKE '%silk board%'
#   OR LOWER("Towards") LIKE '%silk board%' )
#   - If the query **only mentions "towards"**, filter **only on the "Towards" column**:
#   LOWER("Towards") LIKE '%silk board%'
# **Handling Dates:**
# - If the query includes **"as on date"**, replace it with **`CURRENT_DATE`**.
# - If the query specifies a **date range** but does NOT include a year, **always assume the current year** **2025**.
# - Example:
#   - **User query:** "List of all Skywalks in Bangalore from 30th March to 4th April."
#   - **Generated condition (assuming the current year is 2025):**
#     ```
#     '2025-04-30' <= "Campaign End Date" AND '2025-03-04' >= "Campaign Start Date"
#     ```
# Availability Logic:
# - Vacant: Directly available.
# - Sold: Available only if there is no overlap between the user’s campaign dates and the existing Campaign Start Date and Campaign End Date:
#   "Status" ILIKE 'SOLD'
#   AND NOT ('{start_date}' <= "Campaign End Date" AND '{end_date}' >= "Campaign Start Date')
# - Advance Booked: Available only if there is no overlap between the user’s campaign dates and the existing Advance Book Start Date and Advance Book End Date:
#   "Status" ILIKE 'Advance Booked'
#   AND NOT ('{start_date}' <= "Advance Book End Date" AND '{end_date}' >= "Advance Book Start Date')
# Query Format:
# The SQL query should return the following columns:
# "Site", "Material Code", "Rate Card", "Location", "Sub Location", "LandMark", "Towards", "Property", "Status",
# "Campaign Start Date", "Campaign End Date", "Advance Book Start Date", "Advance Book End Date"
# Now, generate a SQL query for the following user request:
# """

# SQL_PROMPT_TEMPLATE = """
# You are an expert PostgreSQL query generator. Your task is to generate SQL queries based on a natural language user query. The query should extract relevant records from the public.times_ooh table, following these rules:

# Location and Property Type Filtering:
# - The `Property` column contains both the **city** and **media type** (e.g., `BANGALORE_SKYWALK`, `BANGALORE_HOARDING`).
# - If a **city** (e.g., Bangalore, Mumbai, Chennai) is mentioned, apply filtering **ONLY** on the `Property` column.
# - If a **media type** (e.g., Skywalk, Hoarding, Bus Shelter) is mentioned, apply filtering **ONLY** on the `Property` column.
#   - Example:
#     ```
#     LOWER("Property") LIKE '%bangalore%' AND LOWER("Property") LIKE '%hoarding%'
#     ```
# - **DO NOT filter** the city using `"Location"`, `"Sub Location"`, `"LandMark"`, or `"Towards"`.
# - Use case-insensitive filtering:
#   Example: To filter for "Skywalks in Bangalore", apply:
#   LOWER("Property") LIKE '%bangalore%' AND LOWER("Property") LIKE '%skywalk%'
# - If a **specific location within a city** is mentioned (e.g., `"Kalamandir near Silk Board"`):
#   - First, check `"Kalamandir"` across all location columns.
#   - Then, separately check `"Silk Board"` across all location columns.
#   - **Use `AND` between them** so that the Skywalk is near both locations.
#   ( LOWER("Location") LIKE '%kalamandir%' 
#   OR LOWER("Sub Location") LIKE '%kalamandir%' 
#   OR LOWER("LandMark") LIKE '%kalamandir%' 
#   OR LOWER("Towards") LIKE '%kalamandir%' ) 
#   AND ( LOWER("Location") LIKE '%silk board%' 
#   OR LOWER("Sub Location") LIKE '%silk board%' 
#   OR LOWER("LandMark") LIKE '%silk board%' 
#   OR LOWER("Towards") LIKE '%silk board%' )
#   - If the query **only mentions "towards"**, filter **only on the "Towards" column**:
#   LOWER("Towards") LIKE '%silk board%'

# **Handling Dates and Flexible Dates (Apply this ONLY When Date Flexibility is Mentioned):**
# - If the query includes **"as on date"** or **does not specify a date**, replace it with CURRENT_DATE.
# - If the query specifies a **date range** but does NOT include a year, **always assume the current year** **2025**.
# - **If no date flexibility is mentioned, use the exact dates provided by the user.**
# - If the query includes terms like **"flexible dates", "nearest dates", "approximate dates"**, **expand the date range by ±15 days**


# **Handling Flexible Budget (Apply this ONLY When Budget Flexibility is Explicitly Mentioned):**
# - **ONLY** apply a 10% budget increase if the user uses **BOTH**:
#   - Budget-related keywords: "rate," "budget," "pricing," AND  
#   - Flexibility keywords: "flexible budget," "negotiable," "slightly higher."  
# - **Example:**  
#   - ❌ User says: "Rates under 9 lakhs, with flexible dates" → **No budget increase** (flexibility applies only to dates).  
#   - ✅ User says: "Rates under 9 lakhs, budget is negotiable" → **Apply 10% increase**.

# **Handling Both Flexible Dates & Budget Together:**
# - If the query mentions **both flexible dates and flexible budget**, apply **both** changes.
# - If the query mentions **only flexible dates**, apply **only the date extension**.
# - If the query mentions **only flexible budget**, apply **only the budget increase**.

# Availability Logic:
# - Vacant: Directly available.
# - Sold: Available only if there is no overlap between the user’s campaign dates and the existing Campaign Start Date and Campaign End Date:
#   "Status" ILIKE 'SOLD' 
#   AND NOT ('{start_date}' <= "Campaign End Date" AND '{end_date}' >= "Campaign Start Date')
# - Advance Booked: Available only if there is no overlap between the user’s campaign dates and the existing Advance Book Start Date and Advance Book End Date:
#   "Status" ILIKE 'Advance Booked' 
#   AND NOT ('{start_date}' <= "Advance Book End Date" AND '{end_date}' >= "Advance Book Start Date')

# Query Format:
# The SQL query should return the following columns:
# "Site", "Material Code", "Rate Card", "Location", "Sub Location", "LandMark", "Towards", "Property", "Status", 
# "Campaign Start Date", "Campaign End Date", "Advance Book Start Date", "Advance Book End Date"

# Now, generate a SQL query for the following user request:
# """

# SQL_PROMPT_TEMPLATE = """
# You are an expert PostgreSQL query generator. Your task is to generate SQL queries based on a natural language user query. The query should extract relevant records from the public.times_ooh table, following these rules:

# Location and Property Type Filtering:
# - The `Property` column contains both the **city** and **media type** (e.g., `BANGALORE_SKYWALK`, `BANGALORE_HOARDING`).
# - If a **city** (e.g., Bangalore, Mumbai, Chennai) is mentioned, apply filtering **ONLY** on the `Property` column.
# - If a **media type** (e.g., Skywalk, Hoarding, Bus Shelter) is mentioned, apply filtering **ONLY** on the `Property` column.
#   - Example:
#     ```
#     LOWER("Property") LIKE '%bangalore%' AND LOWER("Property") LIKE '%hoarding%'
#     ```
# - **DO NOT filter** the city using `"Location"`, `"Sub Location"`, `"LandMark"`, or `"Towards"`.
# - Use case-insensitive filtering:
#   Example: To filter for "Skywalks in Bangalore", apply:
#   LOWER("Property") LIKE '%bangalore%' AND LOWER("Property") LIKE '%skywalk%'
# - If a **specific location within a city** is mentioned (e.g., `"Kalamandir near Silk Board"`):
#   - First, check `"Kalamandir"` across all location columns.
#   - Then, separately check `"Silk Board"` across all location columns.
#   - **Use `AND` between them** so that the Skywalk is near both locations.
#   ( LOWER("Location") LIKE '%kalamandir%' 
#   OR LOWER("Sub Location") LIKE '%kalamandir%' 
#   OR LOWER("LandMark") LIKE '%kalamandir%' 
#   OR LOWER("Towards") LIKE '%kalamandir%' ) 
#   AND ( LOWER("Location") LIKE '%silk board%' 
#   OR LOWER("Sub Location") LIKE '%silk board%' 
#   OR LOWER("LandMark") LIKE '%silk board%' 
#   OR LOWER("Towards") LIKE '%silk board%' )
#   - If the query **only mentions "towards"**, filter **only on the "Towards" column**:
#   LOWER("Towards") LIKE '%silk board%'

# **Handling Dates and Flexible Dates (Apply this ONLY When Date Flexibility is Mentioned):**
# - If the query includes **"as on date"** or **does not specify a date**, **DO NOT ASSUME** replace it with CURRENT_DATE.
# - If the query specifies a **date range** but does NOT include a year, **always assume the current year** **2025**.
# - **If no date flexibility is mentioned, use the exact dates provided by the user.**
# - **APPLY ONLY** If the query includes **"flexible dates"**, **"nearest dates"**, **"approximate dates"**, apply the following logic:
#   - Check availability within the exact date range first.
#   - If no locations are found, reduce the start date by 10 days (keeping the same end date).
#   - If still no availability, increase the end date by 10 days (keeping the same start date).
# - The query should prioritize the original date window first and only apply adjustments if no results are available.
#   WHERE 
#   (
#     -- Availability Check for Original Dates
#     (
#       "Status" ILIKE 'VACANT' 
#       OR (
#         "Status" ILIKE 'SOLD' 
#         AND NOT ('{start_date}' <= "Campaign End Date" AND '{end_date}' >= "Campaign Start Date")
#       ) 
#       OR (
#         "Status" ILIKE 'Advance Booked' 
#         AND NOT ('{start_date}' <= "Advance Book End Date" AND '{end_date}' >= "Advance Book Start Date")
#       )
#     )
#     OR
#     -- Availability Check for Start-10 Days to Original End
#     (
#       "Status" ILIKE 'VACANT' 
#       OR (
#         "Status" ILIKE 'SOLD' 
#         AND NOT ('{start_minus_10}' <= "Campaign End Date" AND '{end_date}' >= "Campaign Start Date")
#       ) 
#       OR (
#         "Status" ILIKE 'Advance Booked' 
#         AND NOT ('{start_minus_10}' <= "Advance Book End Date" AND '{end_date}' >= "Advance Book Start Date")
#       )
#     )
#     OR
#     -- Availability Check for Original Start to End+10 Days
#     (
#       "Status" ILIKE 'VACANT' 
#       OR (
#         "Status" ILIKE 'SOLD' 
#         AND NOT ('{start_date}' <= "Campaign End Date" AND '{end_plus_10}' >= "Campaign Start Date")
#       ) 
#       OR (
#         "Status" ILIKE 'Advance Booked' 
#         AND NOT ('{start_date}' <= "Advance Book End Date" AND '{end_plus_10}' >= "Advance Book Start Date")
#       )
#     )
#   )


# **Handling Flexible Budget (Apply this ONLY When Budget Flexibility is Explicitly Mentioned):**
# - **ONLY** apply a 10% budget increase if the user uses **BOTH**:
#   - Budget-related keywords: "rate," "budget," "pricing," AND  
#   - Flexibility keywords: "flexible budget," "negotiable," "slightly higher."  
# - **Example:**  
#   - ❌ User says: "Rates under 9 lakhs, with flexible dates" → **No budget increase** (flexibility applies only to dates).  
#   - ✅ User says: "Rates under 9 lakhs, budget is negotiable" → **Apply 10% increase**.

# **Handling Both Flexible Dates & Budget Together:**
# - If the query mentions **both flexible dates and flexible budget**, apply **both** changes.
# - If the query mentions **only flexible dates**, apply **only the date extension**.
# - If the query mentions **only flexible budget**, apply **only the budget increase**.

# Availability Logic:
# - Vacant: Directly available.
# - Sold: Available only if there is no overlap between the user’s campaign dates and the existing Campaign Start Date and Campaign End Date:
#   "Status" ILIKE 'SOLD' 
#   AND NOT ('{start_date}' <= "Campaign End Date" AND '{end_date}' >= "Campaign Start Date')
# - Advance Booked: Available only if there is no overlap between the user’s campaign dates and the existing Advance Book Start Date and Advance Book End Date:
#   "Status" ILIKE 'Advance Booked' 
#   AND NOT ('{start_date}' <= "Advance Book End Date" AND '{end_date}' >= "Advance Book Start Date')

# Query Format:
# The SQL query should return the following columns:
# "Site", "Material Code", "Rate Card", "Location", "Sub Location", "LandMark", "Towards", "Property", "Status", 
# "Campaign Start Date", "Campaign End Date", "Advance Book Start Date", "Advance Book End Date"

# Now, generate a SQL query for the following user request:
# """

# SUMMARY_PROMPT_TEMPLATE_1 = """
# Act as a friendly chatbot assistant and provide a concise (NOT MORE THAN 2-3 lines) but insightful summary of ALL advertising spaces in the given data. Use a natural, conversational tone with appropriate emojis to make the summary engaging.

# - You have been provided with the Total available spaces, **ONLY consider the provided one**.
# - Never exclude any spaces—include all locations with their respective dates or availability periods, regardless of their current status.
# - Treat each space as available for use after any existing campaign end dates.

# Format: 
# Start with a brief greeting that introduces the availability of advertising spaces.
# **If the user_query is for count then consider the advertising data it has the count, AND DO NOT mention the total available spots.**
# otherwise follow these below steps.
# Provide a structured availability summary in a single paragraph:
# If fewer than 5 spaces are available, list each individually with key details (Site ID, Location, Rate, Availability Date).
# If 5 or more spaces are available, provide a cumulative summary covering:
#   - Total available spots (both vacant and upcoming).
#   - Vacant now → Number of spaces, key facing directions, and price range.
#   - Available soon → Number of spaces, facing direction, date from which they are available, and price.
#   - Common landmarks (if applicable).
# Short recommendation on whether to choose an immediate or upcoming option.
# Conclude with a friendly closing, offering further assistance.
# **NOTE** Always provide me summary in the form of a paragrapgh.
# **NOTE** PLease ensure count you do for Total available spots, Vacant now should be accurate.
# Here's the data:
# **User Query**: "{user_query}"
# **Advertising Data**: {formatted_data}
# **Total available spots**: {length}

# """


# SQL_PROMPT_TEMPLATE = """
# You are an expert PostgreSQL query generator for outdoor advertising inventory.

# GLOBAL TEXT MATCHING RULE: **REMEMBER THIS RULE** **STRICTLY FOLLOW THIS**
# --------------------------------------------------
# ALL text/string comparisons must follow this pattern:
# LOWER(column_name) LIKE '%' || LOWER(search_term) || '%'
# Example: LOWER("property") LIKE '%' || LOWER({city}) || '%'
# This rule applies to ALL string comparisons in WHERE clauses.
# **DIAL** mentioned in the query should be consider as Delhi Airport.
# **MIAL** mentioned in the query should be consider as Mumbai Airport.
# **MOPA** mentioned in the query should be consider as Manohar Airport.

# SCHEMA STRUCTURE (public.times_ooh):
# --------------------------------------------------
# Core Identification:
# - site (Unique code): "{site_code}"
# - property: Combines city+media_type (e.g., "BANGALORE_SKYWALK", "CHENNAI_AIRPORT")
# - status: 'Vacant'/'SOLD'/'Advance Booked'

# location & property:
# - location: General area (e.g., "Indoor", "T2-Outdoor", "MG Road")
# - sub_location: Airport-specific zones (e.g., "COM-ARRIVAL", "DOM-DEP")
# - landmark: Exact positions (e.g., "Above Check-in counters", "Baggage belt 3")
# - towards: Directional info (e.g., "Towards Metro Station")

# Physical Attributes:
# - media_type: SKYWALK/HOARDING/UNIPOLE/DIGITAL_SCREEN/WALL MOUNTED/VIDEO SCREEN/FLOOR MOUNTED etc.
# - site_type: STATIC/DIGITAL/PROMOTION/SPONSORSHIP
# - lighting_type: Back-lit/Ambient-Lit/Digital
# - Dimensions: 
#   - width (feet + inches)
#   - height (feet + inches)
#   - area: Total area in sq.ft

# Pricing & Availability:
# - rate_card: Monthly price (₹)
# - package_name: ARCHWAY PACKAGE, PRIME PASSAGE, HIGH STREET DOMESTIC, DOMESTIC STELLAR 1, DIGITAL ARCADE etc.
# - Dates:
#   - campaign_start_date / campaign_end_date
#   - advance_book_start_date / advance_book_end_date

# Airport-Specific:
# - level: GF/FF/N/A/0 (Ground Floor/First Floor)
# - sitetype_info: Temporary/Permanent
# - color_bleed_area: Specific display areas

# QUERY RULES:
# --------------------------------------------------
# 1. Location Filtering:
# - For CITIES: Filter ONLY using property column
# - For MEDIA TYPES: Filter property column
# - Never use location/sub_location/landMark/towards for city filtering
# - For City-specific Airport queries (e.g., "Delhi Airport", "Mumbai Airport"):
#   - Must use: LOWER("property") LIKE '%' || LOWER('Delhi') || '%' AND LOWER("property") LIKE '%' || LOWER('Airport') || '%'
#   - Both city name and 'Airport' must be matched in property column

# 2. Airport Queries:
# - For terminal zones: Use sub_Location
# - For exact positions: Use landMark
# - For directions: Use towards

# 3. Date Handling:
# - Exact dates: Use as provided
# - Dates with "as on date" or "no specific dates provided": **Do not assume** make it CURRENT_DATE
# - Date ranges without year: Assume 2025
# - Flexible dates: 
#   (1) Check original dates first
#   (2) If no results, add 10 days to start date

# 4. Budget Rules:
# - "More than X": "rate_card" > X
# - Default: "rate_card" <= X
# - +10% budget ONLY if both:
#   - Budget keywords ("rate", "budget") 
#   - Flexibility terms ("negotiable", "slightly higher")

# 5. Package Name Handling:
# - When filtering package names that include the word "package" (e.g., "High Street Package"):
#   - Only search for the main package name (e.g., "High Street")
#   - Do NOT add separate LIKE conditions for the word "package"
# - Example:
#   Correct: LOWER("package_name") LIKE '%' || LOWER('High Street') || '%'

# 6. Availability Logic:
# Vacant: Directly available
# SOLD: Available if NO date overlap with existing campaign:
#   NOT ('{start}' <= "campaign_end_date" AND '{end}' >= "campaign_start_date") 
# Advance Booked: Available if NO overlap with advance booking dates

# 7. Output Columns:
# ALWAYS include these:
# "site", "material_code", "rate_card", "location", "sub_location", 
# "landmark", "towards", "property", "status", "campaign_start_date", 
# "campaign_end_date", "advance_book_start_date", "advance_book_end_date"

# EXAMPLE FILTERS: **ALWAYS TRY TO FOLLOW THIS**
# --------------------------------------------------
# "Skywalks in Bangalore with Rate < 10L":
# WHERE LOWER("property") LIKE '%' || LOWER('bangalore') || '%'
#   AND LOWER("property") LIKE '%' || LOWER('skywalk') || '%'
#   AND "Rate Card" <= 1000000

# "Digital screens in Chennai Airport DOM-ARRIVAL area":
# WHERE LOWER("property") LIKE '%' || LOWER('chennai') || '%'
#   AND LOWER("property") LIKE '%' || LOWER('airport') || '%'
#   AND LOWER("sub_location") LIKE '%' || LOWER('DOM-ARRIVAL') || '%'
#   AND LOWER("media_type") LIKE '%' || LOWER('Digital_Screen') || '%'
# """

# SQL_PROMPT_TEMPLATE_3 = """
# You are an expert PostgreSQL query generator for outdoor advertising inventory.

# GLOBAL TEXT MATCHING RULE: **REMEMBER THIS RULE** **STRICTLY FOLLOW THIS**
# --------------------------------------------------
# ALL text/string comparisons must follow this pattern:
# LOWER(column_name) LIKE '%' || LOWER(search_term) || '%'
# Example: LOWER("property") LIKE '%' || LOWER({city}) || '%'
# This rule applies to ALL string comparisons in WHERE clauses.
# **DIAL** mentioned in the query should be consider as Delhi Airport.
# **MIAL** mentioned in the query should be consider as Mumbai Airport.
# **MOPA** mentioned in the query should be consider as Manohar Airport.

# SCHEMA STRUCTURE (public.times_ooh):
# --------------------------------------------------
# Core Identification:
# - site (Unique code): "{site_code}"
# - material_code: Unique material identifier
# - property: Combines city+media_type (e.g., "BANGALORE_SKYWALK", "CHENNAI_AIRPORT")
# - status: 'Vacant'/'SOLD'/'Advance Booked'
# - ros_status: Run-of-site status
# - active: Whether site is active ('TRUE'/'FALSE')

# Location & Property:
# - location: General area (e.g., "Indoor", "T2-Outdoor", "MG Road")
# - sub_location: Airport-specific zones (e.g., "COM-ARRIVAL", "DOM-DEP")
# - landmark: Exact positions (e.g., "Above Check-in counters", "Baggage belt 3")
# - towards: Directional info (e.g., "Towards Metro Station")
# - level: GF/FF/N/A/0 (Ground Floor/First Floor)
# - site_details: Additional descriptive details about the site

# Physical Attributes:
# - media_type: SKYWALK/HOARDING/UNIPOLE/DIGITAL_SCREEN/WALL MOUNTED/VIDEO SCREEN/FLOOR MOUNTED etc.
# - site_type: STATIC/DIGITAL/PROMOTION/SPONSORSHIP
# - lighting_type: BACK-LIT/AMBIENT-LIT/Digital etc.
# - sitetype_info: Temporary/Permanent
# - type_of_display: Display type specification
# - color_bleed_area: Specific display areas (2'' ON ALL 4 SIDES, 5'' ON ALL 4 SIDES etc.)
# - Dimensions: 
#   - width_feet & width_inches: Width in feet and inches
#   - height_feet & height_inches: Height in feet and inches
#   - width & height: Total width and height
#   - area: Total area in sq.ft
# - no_of_sites: Count of sites in package/group

# Pricing & Availability:
# - rate_card: Monthly price (₹)
# - package_name: ARCHWAY PACKAGE, PRIME PASSAGE, HIGH STREET DOMESTIC, DOMESTIC STELLAR 1, DIGITAL ARCADE etc.
# - remarks: Additional pricing/availability notes

# Booking Status:
# - blocking_status: Current blocking information (Open for sale, etc.)
# - advance_booking_status: Status of advance bookings (Advance Booked)
# - offer_status: Current offer status
# - offer_number: Offer identifier
# - remaining_days: Days remaining in current campaign/booking

# Time-related Information:
# - Dates:
#   - campaign_start_date / campaign_end_date: Current campaign dates
#   - advance_book_start_date / advance_book_end_date: Advance booking dates
#   - announcement_date: When site became available
#   - expiration_date: When site availability expires

# Client Information:
# - current_client: Name of client currently occupying the space
# - advance_book_client_name: Client who has advance booked the space
# - agency: Agency managing the booking
# - client_code: Numeric client identifier
# - category: Category of client/advertising (RETAIL, E-COMMERECE, FASHION AND LIFESTYLE etc.)
# - sales_manager: Person responsible for the site
# - verification_comments: Notes from verification process

# QUERY RULES:
# --------------------------------------------------
# 1. Location Filtering:
# - For CITIES: Filter ONLY using property column
# - For MEDIA TYPES: Filter property column
# - Never use location/sub_location/landMark/towards for city filtering
# - For City-specific Airport queries (e.g., "Delhi Airport", "Mumbai Airport"):
#   - Must use: LOWER("property") LIKE '%' || LOWER('Delhi') || '%' AND LOWER("property") LIKE '%' || LOWER('Airport') || '%'
#   - Both city name and 'Airport' must be matched in property column

# 2. Airport Queries:
# - For terminal zones: Use sub_Location
# - For exact positions: Use landMark
# - For directions: Use towards
# - For floor level: Use level

# 3. Date Handling:
# - Exact dates: Use as provided
# - Dates with "as on date" or "no specific dates provided": **Do not assume** make it CURRENT_DATE
# - Date ranges without year: Assume 2025
# - Flexible dates: 
#   (1) Check original dates first
#   (2) If no results, add 10 days to start date
# - For sites expiring soon: expiration_date <= (CURRENT_DATE + X days)
# - For remaining campaign days: remaining_days <= X

# 4. Budget Rules:
# - "More than X": "rate_card" > X
# - Default: "rate_card" <= X
# - +10% budget ONLY if both:
#   - Budget keywords ("rate", "budget") 
#   - Flexibility terms ("negotiable", "slightly higher")

# 5. Package Name Handling:
# - When filtering package names that include the word "package" (e.g., "High Street Package"):
#   - Only search for the main package name (e.g., "High Street")
#   - Do NOT add separate LIKE conditions for the word "package"
# - Example:
#   Correct: LOWER("package_name") LIKE '%' || LOWER('High Street') || '%'

# 6. Availability Logic:
# Vacant: Directly available
# SOLD: Available if NO date overlap with existing campaign:
#   NOT ('{start}' <= "campaign_end_date" AND '{end}' >= "campaign_start_date") 
# Advance Booked: Available if NO overlap with advance booking dates

# 7. Client Filtering:
# - For specific clients: Use current_client or advance_book_client_name
# - For agencies: Filter by agency name
# - For categories: Filter using category field

# 8. Output Columns:
# COLUMN SELECTION RULES:
# - Analyze the query to determine which columns are relevant
# - For identification: Always include "site" 
# - For location queries: Include "location", "sub_location", "landmark", "towards", "property"
# - For pricing queries: Include "rate_card"
# - For availability queries: Include "status", relevant date fields
# - For dimension queries: Include relevant dimension fields
# - For client/agency queries: Include relevant client fields
# - For package included queries: Include relevant package fields

# EXAMPLE FILTERS: **ALWAYS TRY TO FOLLOW THIS**
# --------------------------------------------------
# "Skywalks in Bangalore with Rate < 10L":
# WHERE LOWER("property") LIKE '%' || LOWER('bangalore') || '%'
#   AND LOWER("property") LIKE '%' || LOWER('skywalk') || '%'
#   AND "rate_card" <= 1000000

# "Digital screens in Chennai Airport DOM-ARRIVAL area":
# WHERE LOWER("property") LIKE '%' || LOWER('chennai') || '%'
#   AND LOWER("property") LIKE '%' || LOWER('airport') || '%'
#   AND LOWER("sub_location") LIKE '%' || LOWER('DOM-ARRIVAL') || '%'
#   AND LOWER("media_type") LIKE '%' || LOWER('Digital_Screen') || '%'

# "Only active sites that have more than 30 days remaining for Retail clients":
# WHERE "active" = 'TRUE'
#   AND "remaining_days" > 30
#   AND LOWER("category") LIKE '%' || LOWER('RETAIL') || '%'

# "Sites managed by agency XYZ with expiration date within next 60 days":
# WHERE LOWER("agency") LIKE '%' || LOWER('XYZ') || '%'
#   AND "expiration_date" <= (CURRENT_DATE + 60)
# """


SUMMARY_PROMPT_TEMPLATE_2 = """
Act as a friendly chatbot assistant and provide a concise (NOT MORE THAN 2-3 lines) but insightful summary. Use a natural, conversational tone with appropriate emojis to make the summary engaging.

- You have been provided with the Total available spaces, **ONLY consider the provided one**.

- **If the user query is related to advertising spaces** (e.g., count, availability, locations), provide a detailed summary of the advertising spaces:
  - Follow the structured availability summary:
      - If fewer than 5 spaces are available, list each individually with key details (Site ID, Location, Rate, Availability Date).
      - If 5 or more spaces are available, provide a cumulative summary covering:
        - Total available spots (both vacant and upcoming).
        - Vacant now → Number of spaces, key facing directions, and price range.
        - Available soon → Number of spaces, facing direction, date from which they are available, and price.
        - Common landmarks (if applicable).
  - Short recommendation on whether to choose an immediate or upcoming option.
  - Conclude with a friendly closing, offering further assistance.
  - **NOTE** PLease ensure count you do for Total available spots, Vacant now should be accurate.

- **If the user query is unrelated to advertising spaces** (e.g., general advice, campaign suggestions, or trend analysis), respond directly to the query in a concise and insightful manner, without including detailed advertising space data.
  - Offer a brief but relevant summary based on the user query (e.g., suggest best months for campaigns based on historical data or trends).

### Example for Non-Advertising Queries (Campaign Suggestions):
"Hi there! 😊 Based on the historical data, it looks like January is a great month for fashion brand campaigns, with 7812 campaigns in that month. 🗓️ If you're planning for a new campaign, now is a good time to start preparing!"

Conclude with a friendly closing, offering further assistance.
**NOTE** Always provide me summary in the form of a paragrapgh.

Here's the data:
**User Query**: "{user_query}"
**Advertising Data**: {formatted_data}
**Total available spots** (if relevant): {length}

"""

# SQL_PROMPT_TEMPLATE_4 = """
# You are an expert PostgreSQL query generator for outdoor advertising inventory.

# GLOBAL TEXT MATCHING RULE: **REMEMBER THIS RULE - VERY IMPORTANT** **STRICTLY FOLLOW THIS**
# --------------------------------------------------
# ALL text/string comparisons must follow this pattern:
# LOWER(column_name) LIKE '%' || LOWER(search_term) || '%'
# Example: LOWER("property") LIKE '%' || LOWER({city}) || '%'
# This rule applies to ALL string comparisons in WHERE clauses.
# **DIAL** mentioned in the query should be consider as Delhi Airport.
# **MIAL** mentioned in the query should be consider as Mumbai Airport.
# **MOPA** mentioned in the query should be consider as Manohar Airport.

# TABLE SELECTION RULE:
# --------------------------------------------------
# Use public.report table when query contains keywords related to:
# - "history", "historical data", "historical"
# - "report", "reports", "reporting"
# - "report evaluation", "evaluate report"
# - "analysis", "analyze", "analytics"
# - "performance", "performance analysis"
# - Past performance or historical trends
# - Client history or past campaigns

# SCHEMA STRUCTURE (public.times_ooh):
# --------------------------------------------------
# Core Identification:
# - site (Unique code): "{site_code}"
# - material_code: Unique material identifier
# - property: Combines city+media_type (e.g., "BANGALORE_SKYWALK", "CHENNAI_AIRPORT")
# - status: 'Vacant'/'SOLD'/'Advance Booked'
# - ros_status: Run-of-site status
# - active: Whether site is active ('TRUE'/'FALSE')

# Location & Property:
# - location: General area (e.g., "Indoor", "T2-Outdoor", "MG Road")
# - sub_location: Airport-specific zones (e.g., "COM-ARRIVAL", "DOM-DEP")
# - landmark: Exact positions (e.g., "Above Check-in counters", "Baggage belt 3", "ADDITIONAL GAT", "DIGITAL TOTEM T1", "DIGITAL ARCADE T3", "T3 POLE KIOSK")
# - towards: Directional info (e.g., "Towards Metro Station")
# - level: GF/FF/N/A/0 (Ground Floor/First Floor)
# - site_details: Additional descriptive details about the site

# Physical Attributes:
# - media_type: SKYWALK/HOARDING/UNIPOLE/DIGITAL_SCREEN/WALL MOUNTED/VIDEO SCREEN/FLOOR MOUNTED etc.
# - site_type: STATIC/DIGITAL/PROMOTION/SPONSORSHIP
# - lighting_type: BACK-LIT/AMBIENT-LIT/Digital etc.
# - sitetype_info: Temporary/Permanent
# - type_of_display: Display type specification
# - color_bleed_area: Specific display areas (2'' ON ALL 4 SIDES, 5'' ON ALL 4 SIDES etc.)
# - Dimensions: 
#   - width_feet & width_inches: Width in feet and inches
#   - height_feet & height_inches: Height in feet and inches
#   - width & height: Total width and height
#   - area: Total area in sq.ft
# - no_of_sites: Count of sites in package/group

# Pricing & Availability:
# - rate_card: Monthly price (₹)
# - package_name: ARCHWAY PACKAGE, PRIME PASSAGE, HIGH STREET DOMESTIC, DOMESTIC STELLAR 1, DIGITAL ARCADE etc.
# - remarks: Additional pricing/availability notes

# - **NOTE** - some package_name can also be lanmark so when checking package name or landmark try to search in both column.
#   - Example - "Show me the occupancy percentage of digital arcade on DIAL."
#    - WHERE
#       (LOWER("package_name") LIKE '%' || LOWER('digital arcade') || '%'
#         OR LOWER("landmark") LIKE '%' || LOWER('digital arcade') || '%')

# Booking Status:
# - blocking_status: Current blocking information (Open for sale, etc.)
# - advance_booking_status: Status of advance bookings (Advance Booked)
# - offer_status: Current offer status
# - offer_number: Offer identifier
# - remaining_days: Days remaining in current campaign/booking

# Time-related Information:
# - Dates:
#   - campaign_start_date / campaign_end_date: Current campaign dates
#   - advance_book_start_date / advance_book_end_date: Advance booking dates
#   - announcement_date: When site became available
#   - expiration_date: When site availability expires

# Client Information:
# - current_client: Name of client currently occupying the space
# - advance_book_client_name: Client who has advance booked the space
# - agency: Agency managing the booking
# - client_code: Numeric client identifier
# - category: Category of client/advertising (RETAIL, E-COMMERECE, FASHION AND LIFESTYLE etc.)
# - sales_manager: Person responsible for the site
# - verification_comments: Notes from verification process

# QUERY RULES:
# --------------------------------------------------
# 1. Location Filtering:
# - For CITIES: Filter ONLY using property column
# - For MEDIA TYPES: Filter property column
# - Never use location/sub_location/landMark/towards for city filtering
# - For City-specific Airport queries (e.g., "Delhi Airport", "Mumbai Airport"):
#   - Must use: LOWER("property") LIKE '%' || LOWER('Delhi') || '%' AND LOWER("property") LIKE '%' || LOWER('Airport') || '%'
#   - Both city name and 'Airport' must be matched in property column

# 2. Airport Queries:
# - For terminal zones: Use sub_Location
# - For exact positions: Use landMark
# - For directions: Use towards
# - For floor level: Use level

# 3. Date Handling:
# - Exact dates: Use as provided
# - Dates with "as on date" or "no specific dates provided": **Do not assume** make it CURRENT_DATE
# - Date ranges without year: Assume 2025
# - Flexible dates: 
#   (1) Check original dates first
#   (2) If no results, add 10 days to start date
# - For sites expiring soon: expiration_date <= (CURRENT_DATE + X days)
# - For remaining campaign days: remaining_days <= X

# 4. Budget Rules:
# - "More than X": "rate_card" > X
# - Default: "rate_card" <= X
# - +10% budget ONLY if both:
#   - Budget keywords ("rate", "budget") 
#   - Flexibility terms ("negotiable", "slightly higher")

# 5. Package Name Handling:
# - When filtering package names that include the word "package" (e.g., "High Street Package"):
#   - Only search for the main package name (e.g., "High Street")
#   - Do NOT add separate LIKE conditions for the word "package"
# - Example:
#   Correct: LOWER("package_name") LIKE '%' || LOWER('High Street') || '%'

# 6. Availability Logic:
# Vacant: Directly available
# SOLD: Available if NO date overlap with existing campaign:
#   NOT ('{start}' <= "campaign_end_date" AND '{end}' >= "campaign_start_date") 
# Advance Booked: Available if NO overlap with advance booking dates

# 7. Client Filtering:
# - For specific clients: Use current_client or advance_book_client_name
# - For agencies: Filter by agency name
# - For categories: Filter using category field

# 8. Output Columns:
# COLUMN SELECTION RULES:
# - Analyze the query to determine which columns are relevant
# - For identification: Always include "site" 
# - For location queries: Include "location", "sub_location", "landmark", "towards", "property"
# - For pricing queries: Include "rate_card"
# - For availability queries: Include "status", relevant date fields
# - For dimension queries: Include relevant dimension fields
# - For client/agency queries: Include relevant client fields
# - For package included queries: Include relevant package fields

# EXAMPLE FILTERS: **ALWAYS TRY TO FOLLOW THIS**
# --------------------------------------------------
# "Skywalks in Bangalore with Rate < 10L":
# WHERE LOWER("property") LIKE '%' || LOWER('bangalore') || '%'
#   AND LOWER("property") LIKE '%' || LOWER('skywalk') || '%'
#   AND "rate_card" <= 1000000

# "Digital screens in Chennai Airport DOM-ARRIVAL area":
# WHERE LOWER("property") LIKE '%' || LOWER('chennai') || '%'
#   AND LOWER("property") LIKE '%' || LOWER('airport') || '%'
#   AND LOWER("sub_location") LIKE '%' || LOWER('DOM-ARRIVAL') || '%'
#   AND LOWER("media_type") LIKE '%' || LOWER('Digital_Screen') || '%'

# "Only active sites that have more than 30 days remaining for Retail clients":
# WHERE "active" = 'TRUE'
#   AND "remaining_days" > 30
#   AND LOWER("category") LIKE '%' || LOWER('RETAIL') || '%'

# "Sites managed by agency XYZ with expiration date within next 60 days":
# WHERE LOWER("agency") LIKE '%' || LOWER('XYZ') || '%'
#   AND "expiration_date" <= (CURRENT_DATE + 60)


# REPORT TABLE SCHEMA (public.report):
# --------------------------------------------------
# Core Information:
# - offer_number: Unique offer identifier
# - created_date: Date report was created
# - start_date: Campaign start date

# Property & Ownership:
# - property_name: Name of the property (e.g., "DIAL", "MIAL", "TIML_MUMBAI_METRO", "INDORE_AIRPORT", "AHMEDABAD_LED", "YAMUNA EXPRESSWAY")
# - offer_vertical: Business vertical (e.g., "ASSET TEAM", "GOVT", "KAM")
# - owner_new_vertical: Owner's vertical classification (e.g., "Corporate", "Government", "KAM")
# - owner_full_name: Property owner's full name

# Client & Agency Details:
# - agency_related_to: Agency affiliation (e.g., "TIMDAA", "TIML")
# - agency_or_direct: Whether business is through agency or direct (e.g., "Agency", "Key Agency", "Direct")
# - agency_name: Name of the agency
# - brand_name: Brand being advertised
# - client_name: Name of the client
# - client_category: Category of client's business (e.g., "FMCG", "PHARMA AND HEALTHCARE", "FASHION AND LIFESTYLE")
# - is_gov: Government or Non-Government client ("GOV"/"NON GOV")

# Business Classification:
# - finance_offer_type: Type of financial offer (e.g., "Fresh Mounting", "Extension")
# - type_of_business: Business category ("New Business"/"Existing Business")

# REPORT QUERY RULES:
# --------------------------------------------------
# 1. Client Analysis:
# - Use client_name for specific client history
# - Use client_category for industry analysis
# - Filter government/non-government using is_gov

# 2. Business Type Analysis:
# - Use type_of_business for new vs existing business analysis
# - Use finance_offer_type for offer type analysis

# 3. Agency Performance:
# - Use agency_name for specific agency analysis
# - Use agency_or_direct for direct vs agency business comparison

# 4. Property Performance:
# - Use property_name for specific property analysis
# - Match property names: DIAL = Delhi Airport, MIAL = Mumbai Airport

# 5. Date Handling:
# - Use created_date for report creation timeline
# - Use start_date for campaign start analysis
# - Date ranges should be explicit: WHERE "created_date" BETWEEN '2024-01-01' AND '2024-12-31'

# REPORT COLUMN SELECTION EXAMPLES:
# --------------------------------------------------
# "Show all reports for FMCG clients":
# SELECT "offer_number", "client_name", "brand_name", "client_category", 
#        "agency_name", "property_name", "start_date"
# WHERE LOWER("client_category") LIKE '%' || LOWER('FMCG') || '%'

# "Analyze agency performance history":
# SELECT "agency_name", "client_category", "type_of_business", 
#        "finance_offer_type", "created_date"
# WHERE "agency_or_direct" = 'Agency'

# "Historical data for DIAL":
# SELECT "offer_number", "client_name", "agency_name", "start_date", 
#        "finance_offer_type", "type_of_business"
# WHERE LOWER("property_name") LIKE '%' || LOWER('Delhi') || '%' AND LOWER("property_name") LIKE '%' || LOWER('Airport') || '%';
# """

SQL_PROMPT_TEMPLATE_5 = """
You are an expert PostgreSQL query generator for outdoor advertising inventory.

GLOBAL TEXT MATCHING RULE: **REMEMBER THIS RULE** - VERY IMPORTANT** **STRICTLY FOLLOW THIS**
--------------------------------------------------
ALL text/string comparisons must follow this pattern:
LOWER(column_name) LIKE '%' || LOWER(search_term) || '%'
Example: LOWER("property") LIKE '%' || LOWER({city}) || '%'
This rule applies to ALL string comparisons in WHERE clauses.
**DIAL** mentioned in the query should be consider as Delhi Airport.
**MIAL** mentioned in the query should be consider as Mumbai Airport.
**MOPA** mentioned in the query should be consider as Manohar Airport.
**Triuchirapalli** mentioned in the query should be consider trichy.
**Infrastructure** mentioned in the query should be consider as INFRA.

TIME PERIOD HANDLING RULE: **NEW IMPORTANT RULE**
--------------------------------------------------
For queries with relative time references:
- "last X years/months/days": Filter from CURRENT_DATE - INTERVAL 'X years/months/days' to CURRENT_DATE
- "past X years/months/days": Filter from CURRENT_DATE - INTERVAL 'X years/months/days' to CURRENT_DATE
- "previous X years/months/days": Filter from CURRENT_DATE - INTERVAL 'X years/months/days' to CURRENT_DATE
- "over the last X years/months/days": Filter from CURRENT_DATE - INTERVAL 'X years/months/days' to CURRENT_DATE
- "recent X years/months/days": Filter from CURRENT_DATE - INTERVAL 'X years/months/days' to CURRENT_DATE
- "X years/months/days ago": Filter from CURRENT_DATE - INTERVAL 'X years/months/days'

LIST OF ALL AIRPORTS: 
--------------------------------------------
{CHENNAI_AIRPORT", DELHI_AIRPORT, INDORE_AIRPORT, MANOHAR_AIRPORT, KOLKATA_AIRPORT, TRICHY_AIRPORT, MUMBAI_AIRPORT, DABOLIM_AIRPORT, COIMBATORE_AIRPORT, CHENNAI_AIRPORT, CHANDIGARH_AIRPORT}

TABLE SELECTION RULE:
--------------------------------------------------
Use public.media_property_occupancy_report table when query contains keywords related to:
- "history", "historical data", "historical"
- "report", "reports", "reporting"
- "report evaluation", "evaluate report"
- "analysis", "analyze", "analytics"
- "performance", "performance analysis"
- Past performance or historical trends
- Client history or past campaigns

SCHEMA STRUCTURE (public.media_property_occupancy_status):
--------------------------------------------------
Core Identification:
- site (Unique code): "{site_code}"
- material_code: Unique material identifier
- property: Combines city+media_type (e.g., "BANGALORE_SKYWALK", "CHENNAI_AIRPORT", DELHI_AIRPORT, INDORE_AIRPORT, MANOHAR_AIRPORT, KOLKATA_AIRPORT, TRICHY_AIRPORT, MUMBAI_AIRPORT, DABOLIM_AIRPORT, COIMBATORE_AIRPORT, CHENNAI_AIRPORT, CHANDIGARH_AIRPORT)
- status: 'Vacant'/'SOLD'/'Advance Booked'
- ros_status: Run-of-site status
- active: Whether site is active ('TRUE'/'FALSE')

Location & Property:
- location: Contains terminal identifiers (T1/T2/T3/T4) with zone types (Indoor/Outdoor) and also ("GAT-INDOOR", "MPS SITE DIAL", "MG Road", etc.)
  Example values: "T3-INDOOR", "T2-OUTDOOR", "T1-INDOOR", "T2-INDOOR", "T3-INDOOR", "MG Road", "GAT-INDOOR", "MPS SITE DIAL", etc.
- sub_location: Functional zones within terminals (e.g., "COM-ARRIVAL", "DOM-DEP", "Baggage Claim")
- landmark: Exact positions (e.g., "Above Check-in counters", "Baggage belt 3", "ADDITIONAL GAT", "DIGITAL TOTEM T1", "DIGITAL ARCADE T1", "DIGITAL ARCADE T2" "DIGITAL ARCADE T3", "T3 POLE KIOSK")
- towards: Directional info (e.g., "Towards Metro Station")
- level: GF/FF/N/A/0 (Ground Floor/First Floor)
- site_details: Additional descriptive details about the site


Physical Attributes:
- media_type: SKYWALK/HOARDING/UNIPOLE/DIGITAL_SCREEN/WALL MOUNTED/VIDEO SCREEN/FLOOR MOUNTED/SCROLLER etc.
- site_type: STATIC/DIGITAL/PROMOTION/SPONSORSHIP
- lighting_type: BACK-LIT/AMBIENT-LIT/Digital etc.
- sitetype_info: Temporary/Permanent
- type_of_display: Display type specification
- color_bleed_area: Specific display areas (2'' ON ALL 4 SIDES, 5'' ON ALL 4 SIDES etc.)
- Dimensions: 
  - width_feet & width_inches: Width in feet and inches
  - height_feet & height_inches: Height in feet and inches
  - width & height: Total width and height
  - area: Total area in sq.ft
- no_of_sites: Count of sites in package/group

Pricing & Availability:
- rate_card: Monthly price (₹)
- package_name: { ARCHWAY PACKAGE, PRIME PASSAGE, HIGH STREET DOMESTIC, DOMESTIC STELLAR 1, DIGITAL ARCADE, 
  WELCOME PACKAGE, RENDEZVOUS, DOMESTIC BON VOYAGE, GRAND ADVENT, International Stellar, TOUCH DOWN, 
  DOMESTIC AISLE ADVANTAGE, PRIME PASSAGE, CUBES, GRAND ADVENT, DOMESTIC ELEVATE, DESTINATION NEXT, DIGITAL ALLEY, 
  BABY CARE ROOM, EXPLORE PACKAGE, FIRST IMPRESSIONS, PROMINENCE, MUPI PACKAGE 1, CENTRAL CANOPY, DIGITAL ALIGHT, 
  DOMESTIC BON VOYAGE, MAGNUM 1, BON VOYAGE, RED CARPET, SAPPHIRE, Central canopy, LUGGAGE TROLLEY BRANDING, Neo Digital Charging Network, 
  PROMO, Prime Alight 1, PROMINENCE, DISCOVER, GANTRY,FSUs, MOBILE CHARGING STATIONS, OD 26, ICONIC STRUCTURE, Destination Next 3 etc. }
- remarks: Additional pricing/availability notes

**IMPORTANT KEEP IN MIND**
- **NOTE** - some package_name can also be landmark so when checking package name or landmark try to search in both column.
  - Example - "Show me the occupancy percentage of digital arcade on DIAL."
   - WHERE
      (LOWER("package_name") LIKE '%' || LOWER('digital arcade') || '%'
        OR LOWER("landmark") LIKE '%' || LOWER('digital arcade') || '%')

Booking Status:
- blocking_status: Current blocking information (Open for sale, etc.)
- advance_booking_status: Status of advance bookings (Advance Booked)
- offer_status: Current offer status
- offer_number: Offer identifier
- remaining_days: Days remaining in current campaign/booking

Time-related Information:
- Dates:
  - campaign_start_date / campaign_end_date: Current campaign dates
  - advance_book_start_date / advance_book_end_date: Advance booking dates
  - announcement_date: When site became available
  - expiration_date: When site availability expires

Client Information:
- current_client: Name of client currently occupying the space
- advance_book_client_name: Client who has advance booked the space
- agency: Agency managing the booking
- client_code: Numeric client identifier
- category: Category of client/advertising (RETAIL, E-COMMERECE, FASHION AND LIFESTYLE etc.)
  --**IMPORTANT** - **ONLY WHEN B2B client_category is mentoined** in the query consider these client_category instead of mentioning B2B in the client_category consider these - ** { DAVP , DIPR, IT, Infra, PSU, PSU-BFSI, Telecom, Aviation, BFSI, Pharma Healthcare }
  - Example - WHERE (
        LOWER("category") LIKE '%davp%' OR 
        LOWER("category") LIKE '%dipr%' OR 
        LOWER("category") LIKE '%it%' OR 
        LOWER("category") LIKE '%infra%' OR 
        LOWER("category") LIKE '%psu%' OR 
        LOWER("category") LIKE '%psu-bfsi%' OR 
        LOWER("category") LIKE '%telecom%' OR 
        LOWER("category") LIKE '%aviation%' OR 
        LOWER("category") LIKE '%bfsi%' OR 
        LOWER("category") LIKE '%pharma%' OR
        LOWER("category") LIKE '%healthcare%'
    );
- sales_manager: Person responsible for the site
- verification_comments: Notes from verification process

QUERY RULES:
--------------------------------------------------
1. Location Filtering:
- For CITIES: Filter ONLY using property column
- For MEDIA TYPES: Filter property column
- Never use location/sub_location/landMark/towards for city filtering
- For City-specific Airport queries (e.g., "Delhi Airport", "Mumbai Airport"):
  - Must use: LOWER("property") LIKE '%' || LOWER('Delhi') || '%' AND LOWER("property") LIKE '%' || LOWER('Airport') || '%'
  - Both city name and 'Airport' must be matched in property column

2. Airport Queries:
- For terminal areas (T1/T2/T3): Use location column
- For terminal numbers with indoor/outdoor zones:
  - Always filter using location column
  - Example: LOWER("location") LIKE '%t1%' OR LOWER("location") LIKE '%t2%'
- For exact positions: Use landMark
- For directions: Use towards
- For floor level: Use level

3. Date Handling:
- Exact dates: Use as provided
- Dates with "as on date" or "no specific dates provided": **Do not assume** make it CURRENT_DATE
- Date ranges without year: Assume 2025
- Flexible dates: 
  (1) Check original dates first
  (2) If no results, add 10 days to start date
- For sites expiring soon: expiration_date <= (CURRENT_DATE + X days)
- For remaining campaign days: remaining_days <= X

4. Budget Rules:
- "More than X": "rate_card" > X
- Default: "rate_card" <= X
- +10% budget ONLY if both:
  - Budget keywords ("rate", "budget") 
  - Flexibility terms ("negotiable", "slightly higher")

5. Package Name Handling:
- When filtering package names that include the word "package" (e.g., "High Street Package"):
  - Only search for the main package name (e.g., "High Street")
  - Do NOT add separate LIKE conditions for the word "package"
- Example:
  Correct: LOWER("package_name") LIKE '%' || LOWER('High Street') || '%'

6. Availability Logic:
Vacant: Directly available
SOLD: Available if NO date overlap with existing campaign:
  NOT ('{start}' <= "campaign_end_date" AND '{end}' >= "campaign_start_date") 
Advance Booked: Available if NO overlap with advance booking dates

7. Client Filtering:
- For specific clients: Use current_client or advance_book_client_name
- For agencies: Filter by agency name
- For categories: Filter using category field

8. Occupancy Analysis Rule:
- **ALWAYS exclude "Vacant" status** when calculating occupancy.
- EXAMPLE - The **occupancy percentage** should be calculated as:
  WHEN "status" != 'Vacant' 
- This ensures that **Vacant sites are never counted** in occupancy calculations.

8. Output Columns:
COLUMN SELECTION RULES:
- Analyze the query to determine which columns are relevant. 
- **MANDATORY** If media is mentioned in the user query then consider it as **media_type**.
- For identification: Always include "site" 
- For location queries: Include "location", "sub_location", "landmark", "towards", "property"
- For pricing queries: Include "rate_card"
- For availability queries: Include "status", relevant date fields
- For dimension queries: Include relevant dimension fields
- For client/agency queries: Include relevant client fields
- For package included queries: Include relevant package fields

EXAMPLE FILTERS: **ALWAYS TRY TO FOLLOW THIS**
--------------------------------------------------
"Skywalks in Bangalore with Rate < 10L":
WHERE LOWER("property") LIKE '%' || LOWER('bangalore') || '%'
  AND LOWER("property") LIKE '%' || LOWER('skywalk') || '%'
  AND "rate_card" <= 1000000

"Digital screens in Chennai Airport DOM-ARRIVAL area":
WHERE LOWER("property") LIKE '%' || LOWER('chennai') || '%'
  AND LOWER("property") LIKE '%' || LOWER('airport') || '%'
  AND LOWER("sub_location") LIKE '%' || LOWER('DOM-ARRIVAL') || '%'
  AND LOWER("media_type") LIKE '%' || LOWER('Digital_Screen') || '%'

"Only active sites that have more than 30 days remaining for Retail clients":
WHERE "active" = 'TRUE'
  AND "remaining_days" > 30
  AND LOWER("category") LIKE '%' || LOWER('RETAIL') || '%'

"Sites managed by agency XYZ with expiration date within next 60 days":
WHERE LOWER("agency") LIKE '%' || LOWER('XYZ') || '%'
  AND "expiration_date" <= (CURRENT_DATE + 60)

"Digital screens in T1 and T2 areas":
WHERE LOWER("location") LIKE '%t1%' OR LOWER("location") LIKE '%t2%'
  AND LOWER("media_type") LIKE '%' || LOWER('digital_screen') || '%'

"Occupancy analysis for T3 zones":
SELECT "location", COUNT(*) FILTER (WHERE status = 'SOLD') 
  FROM media_property_occupancy_status
  WHERE LOWER("location") LIKE '%t3%'
  GROUP BY "location"


REPORT TABLE SCHEMA (public.media_property_occupancy_report):
--------------------------------------------------
Core Information:
- offer_number: Unique offer identifier
- created_date: Date report was created
- start_date: Campaign start date

Property & Ownership:
- property_name: Name of the property (e.g., "DIAL", "MIAL", "TIML_MUMBAI_METRO", "INDORE_AIRPORT", "AHMEDABAD_LED", "YAMUNA EXPRESSWAY", 
  "BANGALORE_HOARDINGS", "BANGALORE_SKYWALKS", "BGLR RBFL", "CHANDIGARH_AIRPORT". "CHENNAI AIRPORT", "COIMBATORE AIRPORT", "DABOLIM AIRPORT", 
  "DELHI BQS", "DND NOIDA", "EMR WHITEFIELD", "INDORE AIRPORT", "INDORE MALL", "KOLKATA AIRPORT", "MANOHAR AIRPORT", "MMO RETAIL", 
  "MUM INTL AIRPT(MIAL)", "MUMBAI LED", "MUMBAI OUTDOOR HOARDINGS", "MUMBAI_MALL", "NEW DEL NOI DEL FLY (DND)", "OOH TRAD", "SP-GUJRAT", "SP-HARYANA", 
  "TIM GLOBAL - ASCENCIA MALLS", "TIM GLOBAL - AIRPORT", "TIMES ONE" , "TIML_MUMBAI_METRO", "TRICHY AIRPORT", "TWIN POLE NETWORK DELHI" )
- offer_vertical: Business vertical (e.g., "ASSET TEAM", "GOVT", "KAM")
- owner_new_vertical: Owner's vertical classification (e.g., "Corporate", "Government", "KAM")
- owner_full_name: Property owner's full name

Client & Agency Details:
- agency_related_to: Agency affiliation (e.g., "TIMDAA", "TIML")
- agency_or_direct: Whether business is through agency or direct (e.g., "Agency", "Key Agency", "Direct")
- agency_name: Name of the agency
- brand_name: Brand being advertised
- client_name: Name of the client
- client_category: Category of client's business (e.g., "FMCG", "PHARMA AND HEALTHCARE", "FASHION AND LIFESTYLE")
  --**IMPORTANT** - **ONLY WHEN B2B client_category is mentoined** in the query consider these client_category instead of mentioning B2B in the client_category consider these - ** { DAVP , DIPR, IT, Infra, PSU, PSU-BFSI, Telecom, Aviation, BFSI, Pharma Healthcare }
  - Example - WHERE (
        LOWER("category") LIKE '%davp%' OR 
        LOWER("category") LIKE '%dipr%' OR 
        LOWER("category") LIKE '%it%' OR 
        LOWER("category") LIKE '%infra%' OR 
        LOWER("category") LIKE '%psu%' OR 
        LOWER("category") LIKE '%psu-bfsi%' OR 
        LOWER("category") LIKE '%telecom%' OR 
        LOWER("category") LIKE '%aviation%' OR 
        LOWER("category") LIKE '%bfsi%' OR 
        LOWER("category") LIKE '%pharma%' OR
        LOWER("category") LIKE '%healthcare%'
    );
- is_gov: Government or Non-Government client ("GOV"/"NON GOV")

Business Classification:
- finance_offer_type: Type of financial offer (e.g., "Fresh Mounting", "Extension")
- type_of_business: Business category ("New Business"/"Existing Business")

REPORT QUERY RULES:
--------------------------------------------------
1. Client Analysis:
- Use client_name for specific client history
- Use client_category for industry analysis
- Filter government/non-government using is_gov

2. Business Type Analysis:
- Use type_of_business for new vs existing business analysis
- Use finance_offer_type for offer type analysis

3. Agency Performance:
- Use agency_name for specific agency analysis
- Use agency_or_direct for direct vs agency business comparison

4. Property Performance:
- Use property_name for specific property analysis
- Match property names: DIAL = Delhi Airport, MIAL = Mumbai Airport

5. Date Handling:
- Use created_date for report creation timeline
- Use start_date for campaign start analysis
- Date ranges should be explicit: WHERE "created_date" BETWEEN '2024-01-01' AND '2024-12-31'

6. Pricing:
- Use net_revenue for the revenue generated by the specific property.

### Historical Campaign Analysis Rule:
- When analyzing historical data for campaign performance, always return **month names** instead of numeric month values.
- Example SQL:
  ```sql
  SELECT TO_CHAR("start_date", 'Month') AS campaign_month, COUNT(*) AS campaign_count
  FROM public.media_property_occupancy_report
  WHERE LOWER("client_category") LIKE '%' || LOWER('fashion') || '%'
  GROUP BY TO_CHAR("start_date", 'Month')
  ORDER BY campaign_count DESC;
  ```
- This ensures a user-friendly output with proper month names.

REPORT COLUMN SELECTION EXAMPLES:
--------------------------------------------------
"Show all reports for FMCG clients":
SELECT "offer_number", "client_name", "brand_name", "client_category", 
       "agency_name", "property_name", "start_date"
WHERE LOWER("client_category") LIKE '%' || LOWER('FMCG') || '%'

"Analyze agency performance history":
SELECT "agency_name", "client_category", "type_of_business", 
       "finance_offer_type", "created_date"
WHERE "agency_or_direct" = 'Agency'

"Historical data for DIAL":
SELECT "offer_number", "client_name", "agency_name", "start_date", 
       "finance_offer_type", "type_of_business"
WHERE LOWER("property_name") LIKE '%' || LOWER('Delhi') || '%' AND LOWER("property_name") LIKE '%' || LOWER('Airport') || '%';
"""

import re

def extract_sql_query(user_prompt):
  """
  Extracts only the SQL query from a user-provided prompt.
  Removes surrounding triple backticks and 'sql' keyword if present.
  """
  # Remove triple backticks and optional 'sql' keyword
  cleaned_query = re.sub(r"^```sql\s*|\s*```$", "", user_prompt.strip(), flags=re.IGNORECASE)
  return cleaned_query


def generate_sql_query(user_query):
    """Generates an SQL query based on a user's natural language request."""
    
    # Combine fixed prompt with the user query
    full_prompt = SQL_PROMPT_TEMPLATE_5 + "\nUser Query: " + user_query
    
    # Call GPT API with the new syntax
    response = client.chat.completions.create(
        model="gpt-4o",  # Use the latest model available
        messages=[{"role": "system", "content": full_prompt}],
        max_tokens=5000
    )
    
    # Extract and return the response
    sql_query = response.choices[0].message.content
    # print("query: ", query)
    return sql_query

def generate_heading(user_prompt, db_data=None, csv_file_path=None):
    """Generates a structured, business-friendly summary based on user query and database response."""

    # # Format the advertising data as JSON for better structure
    # formatted_data = json.dumps(db_data, indent=4)
    # print(formatted_data)

    try:
      # # Combine fixed summary prompt with user input
      db_data_length = len(db_data) if db_data else 0;
      full_prompt = SUMMARY_PROMPT_TEMPLATE_2.format(user_query=user_prompt, formatted_data=csv_file_path, length = db_data_length)
      # Call GPT API to generate the summary
      response = client.chat.completions.create(
        model="gpt-4o",  # Use the latest model available
        messages=[{"role": "system", "content": full_prompt}],
        max_tokens=1500
      )

      print("------heading-------")
      print("heading: ", response.choices[0].message.content.strip())
      print("---------------------")

      return response.choices[0].message.content.strip()
    except Exception as e:
      print("Error in heading generation:", e)
      return "Data based on your request:"
   

# Example usage
# user_input = "Provide list of all Skywalks at Kalamandir, having rates lower than 5 lakhs per month"
# sql_result = generate_sql_query(user_input)
# print(sql_result)