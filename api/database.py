from pymongo.mongo_client import MongoClient

class DataBase:
    def __init__(self, URI, server_api):
        self.URI = URI      
        self.server_api = server_api  
        self.db_client = MongoClient(self.URI, server_api=self.server_api)        

    def check_connection(self):
        try:
            self.db_client.admin.command("ping")
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(e)
