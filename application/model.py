from app import db
from datetime import datetime

class media_property_occupancy_status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    site = db.Column(db.String(300), unique=True, nullable=False)
    ## new columns
    ros_status = db.Column(db.String(50))
    site_details = db.Column(db.Text)
    level = db.Column(db.String(50))
    package_name = db.Column(db.String(500))
    site_type = db.Column(db.String(500))
    lighting_type = db.Column(db.String(500))
    sitetype_info = db.Column(db.String(500))
    media_type = db.Column(db.String(500))
    width_feet = db.Column(db.Numeric(10, 2), default=0.0)
    width_inches = db.Column(db.Numeric(10, 2), default=0.0)
    height_feet = db.Column(db.Numeric(10, 2), default=0.0)
    height_inches = db.Column(db.Numeric(10, 2), default=0.0)  
    color_bleed_area = db.Column(db.String(500))
    no_of_sites = db.Column(db.Integer, default=0)
    active = db.Column(db.String(50))
    announcement_date = db.Column(db.Date)
    expiration_date = db.Column(db.Date)
    ##
    remarks = db.Column(db.String(200))
    material_code = db.Column(db.String(50))
    rate_card = db.Column(db.Integer, default=0)
    type_of_display = db.Column(db.String(500))
    location = db.Column(db.String(500))
    sub_location = db.Column(db.String(500))
    landmark = db.Column(db.String(500))
    width = db.Column(db.Numeric(10, 2), default=0.0)
    height = db.Column(db.Numeric(10, 2), default=0.0)
    area = db.Column(db.Numeric(10, 2), default=0.0)
    towards = db.Column(db.String(500))
    property = db.Column(db.String(500))
    sales_manager = db.Column(db.String(500))
    offer_status = db.Column(db.String(50))
    offer_number = db.Column(db.String(50))
    status = db.Column(db.String(50))
    blocking_status = db.Column(db.String(50))
    advance_booking_status = db.Column(db.String(50))
    advance_book_start_date = db.Column(db.Date)
    advance_book_end_date = db.Column(db.Date)
    advance_book_client_name = db.Column(db.String(500))
    remaining_days = db.Column(db.Integer, default=0)
    agency = db.Column(db.String(500))
    client_code = db.Column(db.BigInteger)
    current_client = db.Column(db.String(500))
    category = db.Column(db.String(500))
    campaign_start_date = db.Column(db.Date)
    campaign_end_date = db.Column(db.Date)
    verification_comments = db.Column(db.Text)


    def __init__(self, **kwargs):
        super(media_property_occupancy_status, self).__init__(**kwargs)

    def __repr__(self):
        return f'<Site {self.site}>'


class media_property_occupancy_report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    agency_related_to = db.Column(db.String(50))
    created_date = db.Column(db.Date)
    offer_number = db.Column(db.String(50))
    property_name = db.Column(db.String(200))
    offer_vertical = db.Column(db.String(100))
    owner_new_vertical = db.Column(db.String(100))
    owner_full_name = db.Column(db.String(200))
    agency_or_direct = db.Column(db.String(200))
    agency_name = db.Column(db.String(500))
    brand_name = db.Column(db.String(500))
    client_name = db.Column(db.String(500))
    client_category = db.Column(db.String(100))
    is_gov = db.Column(db.String(20))
    finance_offer_type = db.Column(db.String(100))
    type_of_business = db.Column(db.String(100))
    start_date = db.Column(db.Date)
    po_date = db.Column(db.Date)

    def __init__(self, **kwargs):
        super(media_property_occupancy_report, self).__init__(**kwargs)

    def __repr__(self):
        return f'<Report {self.agency_related_to}>'


class uploaded_file_records(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(500), unique=True, nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    table_name = db.Column(db.String(500), nullable=False) # name of the table the file was uploaded to.
    uploaded_at = db.Column(db.DateTime)
    ip_address = db.Column(db.String(50))


class new_columns(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    table_name = db.Column(db.String(100), nullable=False, unique=True)
    column_name = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime)

    def __repr__(self):
        return f"new_columns_data('{self.table_name}', '{self.column_name}', '{self.created_at}')"