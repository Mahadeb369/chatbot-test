from datetime import datetime
import pandas as pd
import time
import os
from flask import current_app as app

SAVED_CSV_FOLDER = '/app/saved_csv'
os.makedirs(SAVED_CSV_FOLDER, exist_ok=True)
app.config['SAVED_CSV_FOLDER'] = SAVED_CSV_FOLDER


def file_to_list_of_dicts(file_path):
    # Read the file based on its extension
    if file_path.lower().endswith('.csv'):
        df = pd.read_csv(file_path, encoding='utf-8-sig')
    else:
        df = pd.read_excel(file_path)
    
    # Process headers: strip, lowercase, replace spaces, colons, and slashes
    processed_headers = [
        header.strip().lower().replace(' ', '_').replace(':', '').replace('/', '_')
        for header in df.columns
    ]
    df.columns = processed_headers
    
    data = []
    for _, row in df.iterrows():
        entry = {}
        for header in processed_headers:
            value = row[header]
            
            # Handle NaN values and convert to stripped string
            if pd.isna(value):
                stripped_value = ''
            else:
                stripped_value = str(value).strip()
            
            if not stripped_value:
                entry[header] = None
            else:
                # Check if the value is numeric
                if stripped_value.replace('.', '', 1).isdigit():
                    if '.' in stripped_value:
                        entry[header] = float(stripped_value)
                    else:
                        entry[header] = int(stripped_value)
                else:
                    # Replace specific string values
                    if stripped_value == "DIAL":
                        stripped_value = "Delhi International Airport Limited(DIAL)"
                    elif stripped_value == "Mum Intl Airpt(MIAL)":
                        stripped_value = "Mumbai International Airport Limited(MIAL)"
                    entry[header] = stripped_value
        data.append(entry)
    
    return data


def format_date(date_str):
    """ Format date string to 'YYYY-MM-DD' format """
    try:
        if not date_str:
            return None
        
        # Convert to string and extract date part (before first space)
        date_part = str(date_str).strip().split()[0]
        
        # Ordered list of supported date formats
        date_formats = [
            "%d/%m/%Y",   # 05/01/2024
            "%d-%m-%Y",   # 05-01-2024
            "%Y-%m-%d",   # 2024-01-05 (ISO format)
            "%m/%d/%Y",   # 01/05/2024 (US format)
        ]
        
        parsed_date = None
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_part, fmt)
                break
            except ValueError:
                continue
        
        if not parsed_date:
            raise ValueError(f"Unrecognized date format: {date_str}")
            
        return parsed_date.strftime("%Y-%m-%d")
        
    except ValueError as ve:
        print(f"Date parsing error: {ve}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


def process_inventorty_data(inventorty_data: list) -> list:
    """ Process raw inventory data and return a list of cleaned dictionaries """

    if inventorty_data:
        processed_data = []

        for row in inventorty_data:
            # Extract and clean data from each row
            row_data = {
                'site': row.get("site") if row.get("site") else row.get("site_code"),
                'ros_status': row.get("ros_status") if row.get("ros_status") else None,
                'site_details': row.get("site_details") if row.get("site_details") else None,
                'level': row.get("level") if row.get("level") else None,
                'package_name': row.get("package_name") if row.get("package_name") else None,
                'site_type': row.get("site_type") if row.get("site_type") else None,
                'lighting_type': row.get("lighting_type") if row.get("lighting_type") else None,
                'sitetype_info': row.get("sitetype_info") if row.get("sitetype_info") else None,
                'media_type': row.get("media_type") if row.get("media_type") else None,
                'width_feet': row.get("width_feet") if row.get("width_feet") and isinstance(row.get("width_feet"), (int, float)) else 0,
                'width_inches': row.get("width_inches") if row.get("width_inches") and isinstance(row.get("width_inches"), (int, float)) else 0,
                'height_feet': row.get("height_feet") if row.get("height_feet") and isinstance(row.get("height_feet"), (int, float)) else 0,
                'height_inches': row.get("height_inches") if row.get("height_inches") and isinstance(row.get("height_inches"), (int, float)) else 0,
                'color_bleed_area': row.get("color_bleed_area") if row.get("color_bleed_area") else None,
                'no_of_sites': row.get("no_of_sites") if row.get("no_of_sites") else None,
                'active': row.get("active") if row.get("active") else None,
                'announcement_date': format_date(row.get("announcement_date")) if row.get("announcement_date") else None,
                'expiration_date': format_date(row.get("expiration_date")) if row.get("expiration_date") else None,
                'remarks': row.get("remarks") if row.get("remarks") and row.get("remarks") != "" else None,
                'material_code': row.get("material_code") if row.get("material_code") else None,
                'rate_card': row.get("rate_card") if row.get("rate_card") else None,
                'type_of_display': row.get("type_of_display") if row.get("type_of_display") else None,
                'location': row.get("location") if row.get("location") else None,
                'sub_location': row.get("sub_location") if row.get("sub_location") else None,
                'landmark': row.get("landmark") if row.get("landmark") else row.get("land_mark") if row.get("land_mark") else None,
                'width': row.get("width") if row.get("width") and isinstance(row.get("width"), (int, float)) else 0,
                'height': row.get("height") if row.get("height") and isinstance(row.get("height"), (int, float)) else 0,
                'area': row.get("area") if row.get("area") and isinstance(row.get("area"), (int, float)) else 0,
                'towards': row.get("towards") if row.get("towards") else None,
                'property': row.get("property") if row.get("property") else None,
                'sales_manager': row.get("sales_manager") if row.get("sales_manager") else None,
                'offer_status': row.get("offer_status") if row.get("offer_status") else None,
                'offer_number': row.get("offer_number") if row.get("offer_number") else None,
                'status': row.get("status") if row.get("status") else None,
                'blocking_status': row.get("blocking_status") if row.get("blocking_status") else None,
                'advance_booking_status': row.get("advance_booking_status") if row.get("advance_booking_status") else None,
                'advance_book_start_date': format_date(row.get("advance_book_start_date")) if row.get("advance_book_start_date") else None,
                'advance_book_end_date': format_date(row.get("advance_book_end_date")) if row.get("advance_book_end_date") else None,
                'advance_book_client_name': row.get("advance_book_client_name") if row.get("advance_book_client_name") else None,
                'remaining_days': row.get("remaining_days") if row.get("remaining_days") else None,
                'agency': row.get("agency") if row.get("agency") else None,
                'client_code': row.get("client_code") if row.get("client_code") and isinstance(row.get("client_code"), (int, float)) else None,
                'current_client': row.get("current_client") if row.get("current_client") else None,
                'category': row.get("category") if row.get("category") else None,
                'campaign_start_date': format_date(row.get("campaign_start_date")) if row.get("campaign_start_date") else None,
                'campaign_end_date': format_date(row.get("campaign_end_date")) if row.get("campaign_end_date") else None,
                'verification_comments': row.get("verification_comments") if row.get("verification_comments") else None,
            }

            # Inside the loop where each row is processed
            row_data = {k: v for k, v in row_data.items() if v is not None}
            processed_data.append(row_data)

        return processed_data

    else:
        return []



def process_report_data(report_data: list) -> list:
    """ Process raw report data and return a list of cleaned dictionaries """

    if report_data:
        processed_data = []

        for row in report_data:
            # Extract and clean data from each row
            row_data = {
                'agency_related_to': row.get('agency_related_to') if row.get('agency_related_to') else None,
                'created_date': format_date(row.get('created_date')) if row.get('created_date') else None,
                'offer_number': row.get('offer_number') if row.get('offer_number') else None,
                'property_name': row.get('propertyname') if row.get('propertyname') else None,
                'offer_vertical': row.get('offer_vertical') if row.get('offer_vertical') else None,
                'owner_new_vertical': row.get('owner_new_vertical') if row.get('owner_new_vertical') else None,
                'owner_full_name': row.get('owner_full_name') if row.get('owner_full_name') else None,
                'agency_or_direct': row.get('agency_direct') if row.get('agency_direct') else None,
                'agency_name': row.get('agency_agency_name') if row.get('agency_agency_name') else None,
                'brand_name': row.get('brand_name') if row.get('brand_name') else None,
                'client_name': row.get('client_client_name') if row.get('client_client_name') else None,
                'client_category': row.get('client_category') if row.get('client_category') else None,
                'is_gov': row.get('gov_non_gov') if row.get('gov_non_gov') else None,
                'finance_offer_type': row.get('finance_offer_type') if row.get('finance_offer_type') else None,
                'type_of_business': row.get('type_of_business') if row.get('type_of_business') else None,
                'start_date': format_date(row.get('start_date')) if row.get('start_date') else None,
            }

            row_data = {k: v for k, v in row_data.items() if v is not None}
            processed_data.append(row_data)
        
        return processed_data
    
    else:
        return []


def data_to_csv(data):
    """ Save data to CSV file """
    try:
        if data:
            df = pd.DataFrame(data)
            file_name = f"output_{int(time.time())}.csv"
            df.to_csv(f"{app.config['SAVED_CSV_FOLDER']}/{file_name}", index=False)
            file_path = f"{app.config['SAVED_CSV_FOLDER']}/{file_name}"
            print(f"Data saved to {file_path}")
            return file_path
        else:
            print("No data to save")
            return None

    except Exception as e:
        print(f"Error saving data to CSV: {e}")
        return None