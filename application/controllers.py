from flask import Flask, request, render_template, jsonify, request as flask_request, redirect, url_for
from flask import current_app as app
import os
from app import db
from application.model import uploaded_file_records
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import MetaData, Table, Column, inspect, exc, text
import pandas as pd
import chardet
from application.model import new_columns
from sqlalchemy import literal

UPLOAD_FOLDER = '/app/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.types import Integer, String, Date, Text, Float
import io
import re
import uuid
from datetime import datetime, timedelta



# Helper Functions
def format_date(date_str):
    try:
        if pd.isna(date_str) or not str(date_str).strip():
            return None
        
        date_part = str(date_str).strip().split()[0]
        
        date_formats = [
            "%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", 
            "%m/%d/%Y", "%Y/%m/%d", "%d.%m.%Y",
            "%b %d %Y", "%B %d %Y", "%Y%m%d"
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_part, fmt).date()
            except ValueError:
                continue
        return None
    except Exception as e:
        print(f"Date parsing error: {str(e)}")
        return None

def sanitize_column_name(name):
    try:
        # Remove namespace prefix (before colon)
        if ':' in name:
            col_name = name.split(':')
            if col_name[0].lower() in col_name[1].lower():
                name = name.split(':')[-1]
            else:
                name = " ".join(col_name)
        
        # Remove special characters and normalize
        name = re.sub(r'[^a-zA-Z0-9]+', '_', name).lower()
        name = re.sub(r'_+', '_', name).strip('_')
        
        # Special case handling
        if name in ['gov_non_gov', 'gov_direct']:
            name = 'is_gov'
        if name in ['propertyname']:
            name = 'property_name'
        if name in ["agency_direct"]:
            name = 'agency_or_direct'
        if "revenue" in name:
            name = 'net_revenue'
        
        return name
    except Exception as e:
        print(f"Column sanitization error: {str(e)}")
        return None


def process_dataframe(df):
    print("process_dataframe")
    try:
        # Remove columns that have no name
        df = df.loc[:, df.columns.notna()]  # Removes NaN column names
        df = df.loc[:, df.columns.str.strip() != ""]  # Removes empty string column names
        
        # Clean column names
        df.columns = [sanitize_column_name(col) for col in df.columns]
        
        # Convert date columns
        for col in df.columns:
            if 'date' in col:
                df[col] = df[col].apply(format_date)

        # Replace specific column values
        df.replace({
            "DIAL": "Delhi International Airport Limited(DIAL)",
            "Mum Intl Airpt(MIAL)": "Mumbai International Airport Limited(MIAL)"
        }, inplace=True)
        
        return df
    except Exception as e:
        print(f"DataFrame processing error: {str(e)}")
        return None


def determine_target_table(df):
    try:
        site_columns = {'site', 'site_code'}
        df_columns = set(df.columns)
        return 'media_property_occupancy_status' if site_columns & df_columns else 'media_property_occupancy_report'
    except Exception as e:
        print(f"Target table determination error: {str(e)}")
        return None

def get_sql_type(dtype):
    try:
        if pd.api.types.is_integer_dtype(dtype):
            return Integer()
        elif pd.api.types.is_float_dtype(dtype):
            return Float()
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            return Date()
        else:
            return String(500)
    except Exception as e:
        print(f"SQL type conversion error: {str(e)}")
        return String(500)

def check_and_add_columns(df, table_name):
    try:
        # Drop columns with 'Unnamed' in their names
        df = df.loc[:, ~df.columns.str.contains('^unnamed')]

        engine = db.get_engine()
        inspector = inspect(engine)
        existing_columns = {col['name'] for col in inspector.get_columns(table_name)}
        
        extra_columns = set(df.columns) - existing_columns

        print("\n")
        print("new_columns: ", extra_columns)
        print("existing_columns: ", existing_columns)
        print("table_name: ", table_name)
        print("\n")

        for col in df.columns:
            # ignore if there is no name for the column
            if not col or str(col).isdigit():
                continue

            if col not in existing_columns and col != 'id':
                # Check if the column is completely empty (all NaN)
                if df[col].isnull().all():
                    dtype = String(500)  # Default to String for empty columns
                else:
                    dtype = get_sql_type(df[col].dtype)

                with engine.begin() as conn:
                    conn.execute(text(
                        f'ALTER TABLE {table_name} ADD COLUMN "{col}" {dtype.compile(dialect=engine.dialect)}'
                    ))

        # Add new columns to the new_columns table

        with engine.begin() as conn:
            try:
                columns = ""
                for col in extra_columns:
                    columns += col + ", "

                if columns:
                    columns = columns[:-2]  # remove last comma and space
                    print("columns before upserting: ", columns)

                    stmt = insert(new_columns.__table__).values({
                        "table_name": table_name,
                        "column_name": columns,
                        "created_at": datetime.now()
                    })

                    upsert_stmt = stmt.on_conflict_do_update(
                        index_elements=["table_name"],
                        set_={
                            "column_name": new_columns.__table__.c.column_name + literal(", " + columns),
                            "created_at": datetime.now()
                        }
                    )

                    conn.execute(upsert_stmt)

            except Exception as e:
                print(f"Error adding/updating new columns in the new_columns table: {e}")


    except Exception as e:
        print(f"Column addition error: {str(e)}")



def clean_data(df, table_name):
    try:
        engine = db.get_engine()
        metadata = MetaData()
        table = Table(table_name, metadata, autoload_with=engine)
        
        # Get all table columns except ID
        table_columns = [c.name for c in table.columns if c.name != 'id']

        # Ensure all table columns (except ID) exist in DataFrame
        for col in table_columns:
            if col not in df.columns:
                df[col] = None
        
        # Type conversion based on actual column types in the database
        type_converters = {
            Integer: lambda x: pd.to_numeric(x, errors='coerce'),
            Float: lambda x: pd.to_numeric(x, errors='coerce'),
            String: lambda x: x.astype(str).replace({'nan': None, 'None': None}),
            Text: lambda x: x.astype(str).replace({'nan': None, 'None': None}),
            Date: lambda x: pd.to_datetime(x, errors='coerce').dt.date
        }
        
        # Convert columns based on table schema (excluding ID)
        for column in table.columns:
            if column.name == 'id':
                continue  # Skip ID column
                
            if column.name in df.columns:
                col_type = type(column.type)
                convert = type_converters.get(col_type, lambda x: x)
                df[column.name] = convert(df[column.name])
        
        # Return only the columns that exist in the table (excluding ID)
        return df[table_columns].replace({pd.NA: None, 'nan': None, '': None})
    
    except Exception as e:
        print(f"Data cleaning error: {str(e)}")
        raise e



from sqlalchemy import cast, Float, String, Date, Numeric, Integer

def handle_times_ooh_upsert(df):
    temp_table_name = f"temp_{uuid.uuid4().hex}"
    engine = db.get_engine()
    
    try:
        # Create temporary table with explicit data types
        df.to_sql(
            temp_table_name,
            engine,
            index=False,
            if_exists='replace',
            method='multi',
            chunksize=1000,
            dtype={
                'no_of_sites': Integer(),
                'width': Float(),
                'width_feet': Float(),
                'width_inches': Float(),
                'height': Float(),
                'height_feet': Float(),
                'height_inches': Float(),
                'area': Float(),
                'rate_card': Float(),
                'remaining_days': Float(),
                'client_code': Float(),
                "announcement_date": Date(),
                "expiration_date": Date(),
            }
        )

        metadata = MetaData()
        metadata.reflect(bind=engine)
        main_table = metadata.tables['media_property_occupancy_status']
        temp_table = metadata.tables[temp_table_name]

        # Get column names directly from the main table without manual quoting
        target_columns = [c.name for c in main_table.columns if c.name != 'id']
        
        # Get column types from the main table to handle casting
        column_types = {c.name: type(c.type) for c in main_table.columns}

        # Apply casting to ensure proper data types
        source_columns = [
            cast(temp_table.c[c], Float).label(c) if column_types.get(c) in [Float, Numeric] else
            cast(temp_table.c[c], String).label(c) if column_types.get(c) in [String, Text] else
            cast(temp_table.c[c], Date).label(c) if column_types.get(c) == Date else
            temp_table.c[c]
            for c in target_columns
        ]

        # Create insert statement with explicit column mapping
        insert_stmt = insert(main_table).from_select(
            target_columns, 
            db.select(*source_columns)
        )

        # Create update dictionary for upsert
        update_dict = {
            c: insert_stmt.excluded[c]
            for c in target_columns
            if c != 'site'
        }

        # Execute upsert statement
        upsert_stmt = insert_stmt.on_conflict_do_update(
            index_elements=['site'],
            set_=update_dict
        )

        with engine.begin() as conn:
            conn.execute(upsert_stmt)
    except Exception as e:
        print(f"Times_test upsert error: {str(e)}")
        raise e
    finally:
        with engine.begin() as conn:
            conn.execute(text(f'DROP TABLE IF EXISTS {temp_table_name}'))



def handle_report_insert(df):
    engine = db.get_engine()
    # with engine.connect() as conn:
    #     # Delete existing records
    #     conn.execute(text("TRUNCATE TABLE media_property_occupancy_report"))
    #     conn.commit()
    
    # Insert new data
    df.to_sql(
        'media_property_occupancy_report',
        engine,
        index=False,
        if_exists='append',
        method='multi',
        chunksize=1000
    )


def get_file_encoding(file_path, sample_size=10096):
    with open(file_path, "rb") as file:
        raw_data = file.read(sample_size)
    result = chardet.detect(raw_data)
    print("result of file_encoding: ", result)
    encoding = result["encoding"]

    # Handle incorrect ASCII detection
    if encoding is None or encoding.lower() == "ascii":
        encoding = "utf-8"  # Try UTF-8 first

    return encoding


def insert_into_uploaded_file_record(file_path, target_table):
    existing_record = uploaded_file_records.query.filter_by(file_name=os.path.basename(file_path)).first()
    if existing_record:
        existing_record.file_path = file_path
        existing_record.table_name = target_table
        existing_record.uploaded_at = datetime.now()
        existing_record.ip_address = request.remote_addr
    else:
        new_record = uploaded_file_records(
            file_name=os.path.basename(file_path),
            file_path=file_path,
            table_name=target_table,
            uploaded_at=datetime.now(),
            ip_address=request.remote_addr
        )
        db.session.add(new_record)

    return {
        "file_name": os.path.basename(file_path),
        "file_path": file_path,
        "uploaded_at": (datetime.now() + timedelta(hours=5, minutes=30)).strftime("%d/%m/%Y, %H:%M:%S")
    }


def get_tables_starting_position(file_path):
    raw_df = pd.read_excel(file_path, header=None)
    header_row_index = None

    # Loop through rows to find the first row with enough non-null entries (e.g., >5)
    for i, row in raw_df.iterrows():
        non_null_count = row.notnull().sum()
        if non_null_count > 10:  # adjust threshold as needed
            header_row_index = i
            break

    return header_row_index


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        print("\n===== get hit =====\n")
        user_files = request.files.getlist("user_files")
        print("user_files: ", user_files)

        if not user_files:
            # return jsonify({"error": "No files uploaded"}), 400
            return redirect(url_for('index', error='No file received'))

        saved_files = []
        try:
            # Save all files first
            for file in user_files:
                if file.filename == '':
                    continue

                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(file_path)
                saved_files.append(file_path)
        
            # Process saved files
            processed_files_details = []
            for file_path in saved_files:
                file_encoding = get_file_encoding(file_path)
                print("file_encoding: ", file_encoding)
                try:
                    if file_path.endswith('.csv'):
                        try:
                            df = pd.read_csv(file_path, on_bad_lines='skip', encoding=file_encoding)
                        except UnicodeDecodeError:
                            print(f"Error with encoding {file_encoding}, falling back to 'latin-1'")
                            df = pd.read_csv(file_path, on_bad_lines='skip', encoding="latin-1")

                    else:
                        header_start = get_tables_starting_position(file_path)
                        if header_start is not None:
                            print(f"Header row found at index {header_start + 1}")
                            df = pd.read_excel(file_path, header=header_start, engine='openpyxl')
                        else:
                            print(f"Error: Unable to determine header row for file '{file_path}'")
                            continue;

                    df = process_dataframe(df)
                    target_table = determine_target_table(df)
                    
                    # Handle site column
                    if target_table == 'media_property_occupancy_status':
                        site_col = next((col for col in df.columns if col in {'site', 'site_code'}), None)
                        if site_col and site_col != 'site':
                            df.rename(columns={site_col: 'site'}, inplace=True)
                    
                    check_and_add_columns(df, target_table)
                    df = clean_data(df, target_table)
                    
                    if target_table == 'media_property_occupancy_status':
                        handle_times_ooh_upsert(df)
                    else:
                        handle_report_insert(df)
                    
                    record = insert_into_uploaded_file_record(file_path, target_table)
                    processed_files_details.append(record)
                    
                except Exception as e:
                    print(f"Error processing file '{file_path}': {str(e)[0:1000]}")
                    raise e
        
            db.session.commit()
            # return jsonify({'message': f'{len(saved_files)} files processed successfully'}), 200
            return jsonify({'redirect': url_for('chat'), "processed_files_details": processed_files_details}), 200
            
            
        except Exception as e:
            if flask_request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({"error": str(e)}), 500
            # return render_template('index.html', request='POST', error=f"Error: {str(e)}")
            return jsonify({'error': str(e)[0:1000]})
        
    return render_template('chat.html')


@app.route('/uploaded-files', methods=['GET'])
def uploaded_files():
    records = uploaded_file_records.query.all()
    return jsonify([{
        "id": record.id,
        "file_name": record.file_name,
        "file_path": record.file_path,
        "uploaded_at": (record.uploaded_at + timedelta(hours=5, minutes=30)).strftime("%d/%m/%Y, %H:%M:%S") if record.uploaded_at else None,
    } for record in records])
