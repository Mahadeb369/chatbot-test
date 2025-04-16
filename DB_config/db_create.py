from app import app, db
# from chatbot_api.model import Times_ooh, Report  # absolute import
from application.model import media_property_occupancy_status, media_property_occupancy_report, uploaded_file_records
from chatbot_api.model import user_ip_address

with app.app_context():
    db.create_all()
    print("Database tables created!")
