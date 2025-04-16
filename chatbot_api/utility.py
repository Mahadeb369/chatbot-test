from datetime import date
from decimal import Decimal

# Custom JSON encoder to convert date objects to string
def json_serializable(obj):
    try:
        if isinstance(obj, Decimal):  # Handle Decimal values
            return float(obj)  # Convert Decimal to float
        elif isinstance(obj, date):  # Check if the object is a date
            return obj.isoformat()  # Convert date to string format (YYYY-MM-DD)
        else:
            raise TypeError(f"Type {type(obj)} not serializable")
    except Exception as e:
        print(f"Error in JSON serializable: {e}")
        return None


def check_table_name(query, table_name="media_property_occupancy_report"):
    sql_query = query.split("```sql")[1].split("```")[0]
    sql_query = sql_query.lower()
    if sql_query.find("from") != -1:

        if table_name in sql_query:
            return True

        return False
    return False


def omit_data(input):
    """Removes the 'data' key from the input if it exists."""
    if isinstance(input, dict):
        print("it's a dict")
        return {key: value for key, value in input.items() if key != "data"}
    elif isinstance(input, list):
        print("it's a list")
        return [{key: value for key, value in item.items() if key != "data"} for item in input]
    else:
        return None