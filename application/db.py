from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from flask import current_app as app

class db:
    def __init__(self, MONGODB_URI, MONGODB_NAME):
        '''
        Get the database connection and the video requests collection
        '''

        self.client = MongoClient(app.config['MONGODB_URI'], server_api=ServerApi('1'))
        self.db = self.client[app.config['MONGODB_NAME']]
        self.video_requests_collection = self.db[app.config['MONGODB_COLLECTION']]
