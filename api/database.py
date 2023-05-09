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
    
    def get_user(self, data_base: str, table_name: str, field: str, key: str):
        db = self.db_client[data_base]
        collection = db[table_name]
        result = collection.find_one({field: key})
        if(result):
            return result
        else:
            return False        
