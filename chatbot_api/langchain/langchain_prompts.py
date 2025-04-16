from langchain.prompts import PromptTemplate

sql_prompt = PromptTemplate(
  input_variables=["history", "query", "new_status_columns", "new_report_columns"],
  template = """
    You are an expert PostgreSQL query generator for outdoor advertising inventory. Given the conversation history:
    {history}

    Generate an optimized PostgreSQL query for the following user request:
    "{query}"

    GLOBAL TEXT MATCHING RULE: **REMEMBER THIS RULE** - VERY IMPORTANT** **STRICTLY FOLLOW THIS**
    --------------------------------------------------
    ALL text/string comparisons must follow this pattern:
    LOWER(column_name) LIKE '%' || LOWER(search_term) || '%'
    Example: LOWER("property") LIKE '%' || LOWER(city) || '%'
    This rule applies to ALL string comparisons in WHERE clauses.
    **DIAL** mentioned in the query should be consider as Delhi Airport.
    **MIAL** mentioned in the query should be consider as Mumbai Airport.
    **MOPA** mentioned in the query should be consider as Manohar Airport.
    **Triuchirapalli** mentioned in the query should be consider trichy.
    **Infrastructure** mentioned in the query should be consider as INFRA.

    TIME PERIOD HANDLING RULE: **NEW IMPORTANT RULE**
    --------------------------------------------------
    For queries with relative time references:
    - "last year": Filter where year = EXTRACT(YEAR FROM CURRENT_DATE) - 1
    - "last X years": Filter where year >= EXTRACT(YEAR FROM CURRENT_DATE) - X AND year <= EXTRACT(YEAR FROM CURRENT_DATE) - 1
    - "past X years/months/days": Filter from CURRENT_DATE - INTERVAL 'X years/months/days' to CURRENT_DATE
    - "previous X years/months/days": Filter from CURRENT_DATE - INTERVAL 'X years/months/days' to CURRENT_DATE
    - "over the last X years/months/days": Filter from CURRENT_DATE - INTERVAL 'X years/months/days' to CURRENT_DATE
    - "recent X years/months/days": Filter from CURRENT_DATE - INTERVAL 'X years/months/days' to CURRENT_DATE
    - "X years/months/days ago": Filter from CURRENT_DATE - INTERVAL 'X years/months/days'

    MONTH NAME HANDLING RULE:
    --------------------------------------------------
    For queries with specific month names (like "April 2024"):
    - Use EXTRACT function to convert month names to their numeric values:
      EXTRACT(MONTH FROM "start_date") = [month_number] AND EXTRACT(YEAR FROM "start_date") = [year]
    - Example: "April 2024" becomes EXTRACT(MONTH FROM "start_date") = 4 AND EXTRACT(YEAR FROM "start_date") = 2024

    LIST OF ALL AIRPORTS:
    --------------------------------------------
    [CHENNAI AIRPORT, DELHI AIRPORT, INDORE AIRPORT, MANOHAR AIRPORT, KOLKATA AIRPORT, TRICHY AIRPORT, MUMBAI AIRPORT, DABOLIM AIRPORT, COIMBATORE AIRPORT, CHENNAI AIRPORT, CHANDIGARH AIRPORT]

    **TABLE SELECTION RULE**:
    --------------------------------------------------
    Use public.media_property_occupancy_report table when query contains keywords related to:
    - "past", "past data", "history", "historical data", "historical"
    - "report", "reports", "reporting"
    - "report evaluation", "evaluate report"
    - "analysis", "analyze", "analytics"
    - "performance", "performance analysis"
    - Past performance or historical trends
    - Client history or past campaigns

    SCHEMA STRUCTURE (public.media_property_occupancy_status):
    --------------------------------------------------
    Core Identification:
    - site (Unique code): "This is a unique site code"
    - material_code: Unique material identifier
    - property: Combines city+media_type (e.g., "BANGALORE_SKYWALK", "CHENNAI_AIRPORT", DELHI_AIRPORT, INDORE_AIRPORT, MANOHAR_AIRPORT, KOLKATA_AIRPORT, TRICHY_AIRPORT, MUMBAI_AIRPORT, DABOLIM_AIRPORT, COIMBATORE_AIRPORT, CHENNAI_AIRPORT, CHANDIGARH_AIRPORT)
    - status: 'Vacant'/'SOLD'/'Advance Booked'
    - ros_status: Run-of-site status

    Location & Property:
    - location: Contains terminal identifiers (T1/T2/T3/T4) with zone types (Indoor/Outdoor) and also ("GAT-INDOOR", "MPS SITE DIAL", "MG Road", etc.)
      **LOCATION EXAMPLES TO CONSIDER**:
      ---------------------------------
      GAT-INDOOR
      T1E-INDOOR
      T4 - OUTDOOR
      COIMBATORE AIRPORT-ADL
      Advance/DABOLIM
      MPS SITE DIAL
      T1 & T4 -INDOOR
      Advance DIAL
      T2-OUTDOOR
      CN/Chennai Airport Location
      T4 - INDOOR
      NEW MLCP
      T1A-INDOOR
      MPS Site MIAL
      T3-INDOOR
      T1 & T4 -OUTDOOR
      T3-OUTDOOR
      COMMON - OUTDOOR
      T2-INDOOR
      T1 - INDOOR
      Outdoor
      AD-Location
      CN-Location
      Advance/MOPA
      T1+T2-INDOOR
      T1-INDOOR
      T1B-INDOOR
      T1C-INDOOR
      T1 - OUTDOOR
      Mum Intl Airpt(MIAL)-ADL
      Advance Location Chandigarh
      T1-OUTDOOR
      Indoor
      MPS Kolkata Location
      CN Location Chandigarh
      T1- INDOOR

    - sub_location: Functional zones within terminals.
      **SUB-LOCATION EXAMPLES TO CONSIDER**:
      ---------------------------------
      CN Sub Location Chandigarh
      OD/DEP
      MPS Site-DIAL
      Advance Sub Location Chandigarh
      CN-Sub Location
      INT-ARR
      CN/Chennai Airport Sub-Location
      INTL-DEP
      OD
      OD/DEP-ARR
      OUTDOOR
      DOM/DEPT
      INT-ARRIVAL
      MPS Site-MIAL
      DOM-ARRIVAL
      INTL/ARR
      DOM-DEP+ARRIVAL
      DOM-ARR
      DABOLIM-ADSL
      COM-DEP
      ADvance DIAL SBL
      DOM/ARR
      COM-ARR
      DOM/DEP
      DEPARTURE
      INTL/DEPT
      COIMBATORE AIRPORT-ADSL
      COM-ARRIVAL
      INT-DEP
      COMMON AREA
      MPS Kolkata Sub-Location
      Mum Intl Airpt(MIAL)-ADSL
      INTL-DEP+ARRIVAL
      OD/ARR
      AD-Sub Location
      COM-DEP+ARRIVAL
      MOPA-ADSL
      DOM-DEP

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
    - package_name: [ ARCHWAY PACKAGE, PRIME PASSAGE, HIGH STREET DOMESTIC, DOMESTIC STELLAR 1, DIGITAL ARCADE,
      WELCOME PACKAGE, RENDEZVOUS, DOMESTIC BON VOYAGE, GRAND ADVENT, International Stellar, TOUCH DOWN,
      DOMESTIC AISLE ADVANTAGE, PRIME PASSAGE, CUBES, GRAND ADVENT, DOMESTIC ELEVATE, DESTINATION NEXT, DIGITAL ALLEY,
      BABY CARE ROOM, EXPLORE PACKAGE, FIRST IMPRESSIONS, PROMINENCE, MUPI PACKAGE 1, CENTRAL CANOPY, DIGITAL ALIGHT,
      DOMESTIC BON VOYAGE, MAGNUM 1, BON VOYAGE, RED CARPET, SAPPHIRE, Central canopy, LUGGAGE TROLLEY BRANDING, Neo Digital Charging Network,
      PROMO, Prime Alight 1, PROMINENCE, DISCOVER, GANTRY,FSUs, MOBILE CHARGING STATIONS, OD 26, ICONIC STRUCTURE, Destination Next 3 etc. ]
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
      --**IMPORTANT** - **ONLY WHEN B2B client_category is mentoined** in the query consider these client_category instead of mentioning B2B in the client_category consider these - ** ( DAVP , DIPR, IT, Infra, PSU, PSU-BFSI, Telecom, Aviation, BFSI, Pharma Healthcare )
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

    **Also Consider these new columns/fieds added in the schema**
    --------------------------------------------------
    {new_status_columns}

    QUERY RULES:
    --------------------------------------------------
    0. **LOCATION SEARCH RULE (NEW SUPER RULE)**:
    - For ANY location-related terms (terminals, zones, areas, landmarks, directions, levels):
      **MUST SEARCH ALL THREE COLUMNS**:
      (LOWER("location") LIKE '%' || LOWER(search_term) || '%'
        OR LOWER("sub_location") LIKE '%' || LOWER(search_term) || '%'
        OR LOWER("landmark") LIKE '%' || LOWER(search_term) || '%')
    - **IMPORTANT** **KEEP IN MIND**- **Departue and Arrival** are also consider as **DEP and ARR** respectively so search for both.

    1. Enhanced Location Filtering:
    - For CITIES: Filter ONLY using property column
    - For MEDIA TYPES: Filter property column
    - Never use location/sub_location/landMark/towards for city filtering
    - For City-specific Airport queries (e.g., "Delhi Airport", "Mumbai Airport"):
      - **Must use**: LOWER("property") LIKE '%' || LOWER('Delhi') || '%' AND LOWER("property") LIKE '%' || LOWER('Airport') || '%'
      - Both city name and 'Airport' must be matched in property column

    2. Enhanced Airport Queries:
    - For airport-specific searches combine property filter with Rule 0:
      - Example: LOWER("location") LIKE '%t2%' OR LOWER("sub-location") LIKE '%t2%' OR LOWER("landmark") LIKE '%t2%'
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

    6. **Availability Logic**:
    Vacant: Directly available
    SOLD: Available if NO date overlap with existing campaign:
      NOT ('(start)' <= "campaign_end_date" AND '(end)' >= "campaign_start_date")
    Advance Booked: Available if NO overlap with advance booking dates:
      NOT ('(start)' <= "advance_book_end_date" AND '(end)' >= "advance_book_start_date")

    7. Client Filtering:
    - For specific clients: Use current_client or advance_book_client_name
    - For agencies: Filter by agency name
    - For categories: Filter using category field

    8. Occupancy Analysis Rule:
    - **ALWAYS exclude "Vacant" status** when calculating occupancy.
    - EXAMPLE - The **occupancy percentage** should be calculated as:
      WHEN "status" != 'Vacant'
    - This ensures that **Vacant sites are never counted** in occupancy calculations.
    - **IMPORTANT** - **ALWAYS show result upto two decimal places.
    - EXAMPLE - instead of this "50.00000000000000000000" provide this "50.00"

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

    "Available sites near baggage claim in T2":
    WHERE (LOWER("location") LIKE '%t2%'
           OR LOWER("sub_location") LIKE '%t2%'
           OR LOWER("landmark") LIKE '%t2%')
      AND (LOWER("location") LIKE '%baggage%' 
           OR LOWER("sub_location") LIKE '%baggage%'
           OR LOWER("landmark") LIKE '%baggage%')

    "Skywalks in Bangalore with Rate < 10L":
    WHERE LOWER("property") LIKE '%' || LOWER('bangalore') || '%'
      AND LOWER("property") LIKE '%' || LOWER('skywalk') || '%'
      AND "rate_card" <= 1000000

    "Digital screens in Chennai Airport DOM-ARRIVAL area":
    WHERE LOWER("property") LIKE '%' || LOWER('chennai') || '%'
      AND LOWER("property") LIKE '%' || LOWER('airport') || '%'
      AND LOWER("sub_location") LIKE '%' || LOWER('DOM-ARRIVAL') || '%'
      AND LOWER("media_type") LIKE '%' || LOWER('Digital_Screen') || '%'

    "Sites managed by agency XYZ with expiration date within next 60 days":
    WHERE LOWER("agency") LIKE '%' || LOWER('XYZ') || '%'
      AND "expiration_date" <= (CURRENT_DATE + 60)

    "Digital screens in T1 and T2 areas":
    WHERE LOWER("location") LIKE '%t1%' OR LOWER("location") LIKE '%t2%'
      AND LOWER("media_type") LIKE '%' || LOWER('digital_screen') || '%'

    "Occupancy analysis for T3 zones":
    SELECT "location", COUNT(*) FILTER (WHERE status != 'Vacant')
      FROM media_property_occupancy_status
      WHERE LOWER("location") LIKE '%t3%'
      GROUP BY "location"

    "Suggest 5 best packages or media sites most suitable for fashion and lifestyle brand":
    SELECT "site", "property", "package_name", "rate_card", "status"
      FROM public.media_property_occupancy_status
      WHERE LOWER("category") LIKE '%' || LOWER('fashion and lifestyle') || '%'
      ORDER BY "rate_card" DESC
      LIMIT 5;


    REPORT TABLE SCHEMA (public.media_property_occupancy_report):
    --------------------------------------------------
    Core Information:
    - offer_number: Unique offer identifier
    - created_date: Date report was created
    - start_date: Campaign start date
    - po_date: The date when the Purchase Order (PO) was issued by the client or agency.

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
    - agency_parent_account_agency_name: Parent agency name
    - brand_name: Brand being advertised
    - client_name: Name of the client
    - client_category: Category of client's business (e.g., "FMCG", "PHARMA AND HEALTHCARE", "FASHION AND LIFESTYLE")
      --**IMPORTANT** - **ONLY WHEN B2B client_category is mentoined** in the query consider these client_category instead of mentioning B2B in the client_category consider these - ** [ DAVP , DIPR, IT, Infra, PSU, PSU-BFSI, Telecom, Aviation, BFSI, Pharma Healthcare ]
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
    - rh - Regional Head, This field will have name of the person who has the designation of Regional Head.
    - is_gov: Government or Non-Government client ("GOV."/"NON GOV.")

    Business Classification:
    - finance_offer_type: Type of financial offer (e.g., "Fresh Mounting", "Extension")
    - type_of_business: Business category ("New Business"/"Existing Business")

    Price & Package Information:
    - net_revenue: The revenue generated by the specific property.
    - package_name: [ ARCHWAY PACKAGE, PRIME PASSAGE, HIGH STREET DOMESTIC, DOMESTIC STELLAR 1, DIGITAL ARCADE,
      WELCOME PACKAGE, RENDEZVOUS, DOMESTIC BON VOYAGE, GRAND ADVENT, International Stellar, TOUCH DOWN,
      DOMESTIC AISLE ADVANTAGE, PRIME PASSAGE, CUBES, GRAND ADVENT, DOMESTIC ELEVATE, DESTINATION NEXT, DIGITAL ALLEY,
      BABY CARE ROOM, EXPLORE PACKAGE, FIRST IMPRESSIONS, PROMINENCE, MUPI PACKAGE 1, CENTRAL CANOPY, DIGITAL ALIGHT,
      DOMESTIC BON VOYAGE, MAGNUM 1, BON VOYAGE, RED CARPET, SAPPHIRE, Central canopy, LUGGAGE TROLLEY BRANDING, Neo Digital Charging Network,
      PROMO, Prime Alight 1, PROMINENCE, DISCOVER, GANTRY,FSUs, MOBILE CHARGING STATIONS, OD 26, ICONIC STRUCTURE, Destination Next 3 etc. ]
    - cn_raised: Whether a contract note has been raised, this field will have values as "Yes" or Empty.

    **Also Consider these new columns/fieds added in the schema**
    --------------------------------------------------
    {new_report_columns}

    REPORT QUERY RULES:
    --------------------------------------------------

    1. **IMPORTANT** Package/Media Substitution Rule:
    - When working with report table (media_property_occupancy_report):
      - If "package_name" or "media" columns are :
        * Use "property_name" as well as "package_name" fallback column

    2. Client Analysis:
    - Use client_name for specific client history
    - Use client_category for industry analysis
    - Filter government/non-government using is_gov

    3. Business Type Analysis:
    - Use type_of_business for new vs existing business analysis
    - Use finance_offer_type for offer type analysis

    4. Agency Performance:
    - Use agency_name for specific agency analysis
    - Use agency_or_direct for direct vs agency business comparison

    5. Property Performance:
    - Use property_name for specific property analysis
    - Match property names: DIAL = Delhi Airport, MIAL = Mumbai Airport

    6. Date Handling:
    - Use created_date for report creation timeline
    - Use start_date for campaign start analysis
    - Date ranges should be explicit: WHERE "created_date" BETWEEN '2024-01-01' AND '2024-12-31'

    7. Pricing & Package:
    - Use net_revenue for the revenue generated by the specific property.
    - Use package_name for the respective packages related query.

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
)

heading_prompt = PromptTemplate(
    input_variables=["user_query", "data", "length"],
    template="""
    Act as a Friendly Chatbot assistant, Generate ONLY a 3-5 line heading based on EXACTLY these rules:

    ### Data Handling Protocol
    1. FIRST check {data} for these exact fields:
       - "count", "total_spots", "available_sites", "percentage"
    2. If found → Use THOSE NUMBERS VERBATIM (e.g., 1110 not "1k+")
    3. If NOT found → Use provided length: {length}
    4. Never convert numbers (show 1110 as 1110, length 1 as 1)

    ### Response Structure
    **Advertising Queries**:
    - Start with exact number from data/length
    - Add availability details
    - Time-sensitive recommendation
    - Friendly closing

    **Non-Advertising Queries**:
    - Consider {data}
    - Direct answer + emojis
    - Historical trends if relevant

    ### Examples
    1. **Data with Numbers**:
       Query: "Available sites?"
       Data: {{"AVAILABLE_SITES": 1110}}
       Response: "🚀 Wow! We have 1110 premium locations ready!..."

    2. **Length Fallback**:
       Query: "Vacant billboards?"
       Data: {{"status": "available"}} (length=1)
       Response: "📌 Currently 1 prime spot available!..."

    3. **Non-Advertising**:
       Query: "Best campaign season?"
       Response: "🎄 December sees 2x engagement!..."

    ### Current Context
    User Query: "{user_query}"
    Advertising Data: {data}
    Data Length: {length}
    """
)

fallback_heading_prompt = PromptTemplate(
  input_variables=["user_query"],
  template = """
  You're a friendly chatbot that creates short, natural-sounding headers from user prompts. Keep the response to **one line**, and make it sound like a helpful assistant is speaking.

  Important Rules:
  - ONLY include information explicitly mentioned in the user prompt.
  - DO NOT assume or add details (like occupancy, status, table names, etc.) unless clearly stated.
  - DO NOT reference any internal data sources like "tables", "databases", or "columns".
  - Clearly reflect the user's request and intent.
  - Use a friendly tone with 1–2 relevant emojis.
  - Keep the header clean, conversational, and suitable for frontend display above a result section.

  ### Example:
  User Prompt: Show all the properties at all airports  
  Output Header: Here's a list of all properties across airports 🛫🏢.

  User Prompt: Give me all the packages from all airports  
  Output Header: Here's every package 📦 from all airports ✈️.

  Now generate a one-line, chatbot-style header for this user prompt:  
  "{user_query}"
  """


)

query_decomposition_prompt = PromptTemplate(
  input_variables=["user_query"],
  template="""
  You are an expert at analyzing natural language queries about outdoor advertising inventory data and determining whether they should be decomposed into multiple independent SQL queries.

  Your task is to:
  1. Analyze the user's query carefully
  2. Determine if the query contains multiple distinct requests that would be better handled by separate SQL queries
  3. Identify which queries require historical data vs. current data
  4. If decomposition is needed, break the user's query into independent sub-queries with appropriate table selection keywords
  5. If decomposition is not needed, simply return the original query with appropriate table selection keywords

  ---

  ## Query Context Handling Rules:
  - NEVER modify the user's original query text.
  - Treat each query as a standalone request even if it references previous conversations.
  - Phrases like "basis the previous answer", "based on the above", or "also" **may indicate** a separate request, but only decompose if the logic truly requires multiple queries.
  - Focus only on whether the current query itself needs decomposition.

  ---

  ## Table Selection Intelligence:
  Use the following rules to decide whether a query requires:

  - **Current data** → from `public.media_property_occupancy_status`
  - **Historical data** → from `public.media_property_occupancy_report`
  - **Both** → decompose the query into two parts

  ### HISTORICAL data keywords (use `public.media_property_occupancy_report`):
  - "history", "historical", "past trends", "previous years", "report", "reports", "reporting"
  - "analysis", "analyze", "analytics", "performance analysis"
  - "best months", "client list", "client category", "spending trends", "past campaigns", "previous clients"
  - "revenue", "net revenue", "total revenue".

  ### CURRENT data keywords (use `public.media_property_occupancy_status`):
  - "current", "currently", "now", "present", "existing"
  - "available", "vacancy", "vacant", "occupancy" (without historical context)
  - "rate card", "pricing", "site status"

  ---

  ## Enhanced Decomposition Logic:

  ### DECOMPOSE when:
  - The query requests **multiple unrelated data points or analyses**.
  - The query includes **both historical and current data** analysis.
  - The query has a **clear list structure** ("1)... 2)... 3)...") that asks for distinct types of information.
  - There are **disjointed goals**, like availability check **and** client revenue analysis.
  - The query involves **different dimensions** (e.g., occupancy vs. revenue vs. client category).

  ### DO NOT DECOMPOSE when:
  - The query uses **multiple locations** for **comparison or overlap analysis** (e.g., “clients in Chandigarh and Delhi” or “find common clients between A and B”).
  - The query intends to show **differences, similarities, or intersections** between two or more entities (this can be handled in a single query with SQL logic like `JOIN`, `INTERSECT`, etc.).
  - The query requests data for **multiple airports/sites** but for the **same dimension or metric**.
  - The request for visual representation (e.g., “show in Venn diagram”) is **presentation-layer only**.
  - The query is **asking for a union or comparison** rather than independent evaluations.

  ---

  ## STRICT RULE — Never Combine Historical & Current Data in One Query String:
  If a user query requires **both current and historical data**, it **must be split into two separate sub-queries**, even if the user phrased it as a single sentence.

  ❌ INCORRECT:
  "give airport wise spending both current and historical spending month wise (historical data, report analysis, and current data, occupancy status)"

  ✅ CORRECT:
  "give airport wise current spending month wise (use occupancy status table)"
  "give airport wise historical spending month wise (use historical data, occupancy report table)"

  This ensures that each sub-query is routed to the correct table without ambiguity.

  ---

  ## Output Enrichment Rules:

  For **each query or sub-query**, append a parenthetical label to help downstream SQL generators:

  - **(use occupancy status table)** → for present availability, rate cards, status checks
  - **(use historical data, occupancy report table)** → for past trends, campaign history, client categories
  - If a query requires both types of data, split and tag accordingly.

  ### Output Format:
  **IMPORTANT** **STRICTLY FOLLOW THIS**
  - If decomposition results in MULTIPLE queries → return a JSON array with table information in brackets
  - If decomposition results in ONLY ONE query → return a JSON array with the query WITHOUT table information in brackets
  - If NO decomposition is needed → return a JSON array with the original query WITHOUT table information in brackets

  ---

  ## Special Handling for Visualization:

  If the user query **includes a request for visualization or graphing**, handle it using the following logic:

  1. ✅ **If the visualization instruction is mentioned at the end of the query** (e.g., "also make a graphical visualization", "plot this", "show a graph"), then assume it applies to **every decomposed query**. Append the visualization instruction to each sub-query.

  2. ✅ **If the visualization is mentioned mid-sentence or only in a specific part of the query**, then apply it **only to that specific sub-query**. Do **not** append it to unrelated sub-queries.

  3. ❌ **Never reference or duplicate visualization instructions unnecessarily** — apply only when relevant.

  ### Examples:

  **Case 1: Visualization at the end — apply to all**
  User Query: suggest best media for fashion brands and give spending by airport, also make a graph  
  Output:
  [
    "suggest best media for fashion brands (use historical data, occupancy report table). also make a graph",
    "give spending by airport (use occupancy status table). also make a graph"
  ]

  **Case 2: Visualization attached to one part only**, STRICTLY - **If not mentioned in a specific part do not apply**
  User Query: List all sites with a rate card above 900000 in Chandigarh, Indore, Chennai airport, make a graph also. Show me 10 vacant Digital sites as well  
  Output:
  [
    "List all sites with a rate card above 900000 in Chandigarh, Indore, Chennai airport (use occupancy status table). make a graph also",
    "Show me 10 vacant Digital sites as well (use occupancy status table)"
  ]

  ## Examples:

  **Example 1: Should NOT be decomposed**
  > "real estate and infrastructure clients in Chandigarh and Delhi airport. also mention if any clients are common between the two airports. show the data in a visually appealing format also (output in venn diagram and text)"

  **Output:**
  ```json
  [
    "real estate and infrastructure clients in Chandigarh and Delhi airport. also mention if any clients are common between the two airports. show the data in a visually appealing format also (output in venn diagram and text) (use historical data, occupancy report table)"
  ]
  User Query: "{user_query}"
  """
)

# query_decomposition_prompt = PromptTemplate(
#   input_variables=["user_query"],
#   template="""
#   You are an expert at analyzing natural language queries about outdoor advertising inventory data and determining whether they should be decomposed into multiple independent SQL queries.

#   Your task is to:
#   1. Analyze the user's query carefully
#   2. Determine if the query contains multiple distinct requests that would be better handled by separate SQL queries
#   3. Identify which queries require historical data vs. current data
#   4. If decomposition is needed, break the user's query into independent sub-queries 
#   5. If decomposition is not needed, simply return the original query

#   ---

#   ## Query Context Handling Rules:
#   - NEVER modify the user's original query text.
#   - Treat each query as a standalone request even if it references previous conversations.
#   - Phrases like "basis the previous answer", "based on the above", or "also" **may indicate** a separate request, but only decompose if the logic truly requires multiple queries.
#   - Focus only on whether the current query itself needs decomposition.

#   ---

#   ## Table Selection Intelligence:
#   Use the following rules to decide whether a query requires current or historical data.

#   ### HISTORICAL data keywords:
#   - "history", "historical", "past trends", "previous years", "report", "reports", "reporting"
#   - "analysis", "analyze", "analytics", "performance analysis"
#   - "best months", "client list", "client category", "spending trends", "past campaigns", "previous clients"

#   ### CURRENT data keywords:
#   - "current", "currently", "now", "present", "existing"
#   - "available", "vacancy", "vacant", "occupancy" (without historical context)
#   - "rate card", "pricing", "site status"

#   ---

#   ## Enhanced Decomposition Logic:

#   ### DECOMPOSE when:
#   - The query requests **multiple unrelated data points or analyses**.
#   - The query includes **both historical and current data** analysis.
#   - The query has a **clear list structure** ("1)... 2)... 3)...") that asks for distinct types of information.
#   - There are **disjointed goals**, like availability check **and** client revenue analysis.
#   - The query involves **different dimensions** (e.g., occupancy vs. revenue vs. client category).

#   ### DO NOT DECOMPOSE when:
#   - The query uses **multiple locations** for **comparison or overlap analysis** (e.g., "clients in Chandigarh and Delhi" or "find common clients between A and B").
#   - The query intends to show **differences, similarities, or intersections** between two or more entities (this can be handled in a single query with SQL logic like `JOIN`, `INTERSECT`, etc.).
#   - The query requests data for **multiple airports/sites** but for the **same dimension or metric**.
#   - The request for visual representation (e.g., "show in Venn diagram") is **presentation-layer only**.
#   - The query is **asking for a union or comparison** rather than independent evaluations.

#   ---

#   ## STRICT RULE — Never Combine Historical & Current Data in One Query String:
#   If a user query requires **both current and historical data**, it **must be split into two separate sub-queries**, even if the user phrased it as a single sentence.

#   ❌ INCORRECT:
#   "give airport wise spending both current and historical spending month wise"

#   ✅ CORRECT:
#   "give airport wise current spending month wise"
#   "give airport wise historical spending month wise"

#   This ensures that each sub-query is routed to the correct table without ambiguity.

#   ---

#   ## Output Enrichment Rules:

#   ### Output Format:

#   - If decomposition is required → return a JSON array of multiple query strings
#   - If decomposition is NOT required → return a JSON array with a single element (the original query)

#   ---

#   ## Special Handling for Visualization:

#   If the user query **includes a request for visualization or graphing**, handle it using the following logic:

#   1. ✅ **If the visualization instruction is mentioned at the end of the query** (e.g., "also make a graphical visualization", "plot this", "show a graph"), then assume it applies to **every decomposed query**. Append the visualization instruction to each sub-query.

#   2. ✅ **If the visualization is mentioned mid-sentence or only in a specific part of the query**, then apply it **only to that specific sub-query**. Do **not** append it to unrelated sub-queries.

#   3. ❌ **Never reference or duplicate visualization instructions unnecessarily** — apply only when relevant.

#   ### Examples:

#   **Case 1: Visualization at the end — apply to all**
#   User Query: suggest best media for fashion brands and give spending by airport, also make a graph  
#   Output:
#   [
#     "suggest best media for fashion brands. also make a graph",
#     "give spending by airport. also make a graph"
#   ]

#   **Case 2: Visualization attached to one part only**, STRICTLY - **If not mentioned in a specific part do not apply**
#   User Query: List all sites with a rate card above 900000 in Chandigarh, Indore, Chennai airport, make a graph also. Show me 10 vacant Digital sites as well  
#   Output:
#   [
#     "List all sites with a rate card above 900000 in Chandigarh, Indore, Chennai airport. make a graph also",
#     "Show me 10 vacant Digital sites as well"
#   ]

#   ## Examples:

#   **Example 1: Should NOT be decomposed**
#   > "real estate and infrastructure clients in Chandigarh and Delhi airport. also mention if any clients are common between the two airports. show the data in a visually appealing format also (output in venn diagram and text)"

#   **Output:**
#   ```json
#   [
#     "real estate and infrastructure clients in Chandigarh and Delhi airport. also mention if any clients are common between the two airports. show the data in a visually appealing format also (output in venn diagram and text)"
#   ]
#   User Query: "{user_query}"
#   """
# )

