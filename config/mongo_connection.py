from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

class MongoDB:
    def __init__(self, db_name="CP_Prep_Sys", collection_name="Activities"):
        """
        Initialize MongoDB connection and set up a default collection.
        :param db_name: The name of your MongoDB database
        :param collection_name: The name of your MongoDB collection
        """
        self.db_name = db_name
        self.collection_name = collection_name
        self.client = None
        self.db = None
        self.collection = None
        
        self.connect()

    def connect(self):
        """
        Establish connection to MongoDB.
        """
        try:
            # Connect to MongoDB server
            self.client = MongoClient("mongodb+srv://krupanadgir:WUIVqUtKFK0cr5Rw@cluster0.9rvrx.mongodb.net/")  # MongoDB connection URL (local)
            self.db = self.client[self.db_name]  # Select the database
            self.collection = self.db[self.collection_name]  # Select the collection
            print(f"Connected to MongoDB database: {self.db_name}, collection: {self.collection_name}")
        except ConnectionFailure as e:
            print(f"Could not connect to MongoDB: {e}")
            self.client = None

    def insert_data(self, data):
        """
        Insert a document into the MongoDB collection.
        :param data: A dictionary representing the document to insert.
        """
        if self.client:
            try:
                result = self.collection.insert_one(data)
                print(f"Inserted document with ID: {result.inserted_id}")
                return result.inserted_id
            except Exception as e:
                print(f"Error inserting data: {e}")
        else:
            print("No connection to MongoDB.")
        return None

    def find_data(self, query):
        """
        Find documents in the MongoDB collection matching a query.
        :param query: A dictionary representing the query.
        :return: A cursor for the documents found.
        """
        if self.client:
            try:
                return self.collection.find(query)
            except Exception as e:
                print(f"Error finding data: {e}")
        else:
            print("No connection to MongoDB.")
        return None

    def update_data(self, query, update):
        """
        Update a document in the MongoDB collection.
        :param query: A dictionary representing the query to find the document.
        :param update: A dictionary representing the update to apply.
        """
        if self.client:
            try:
                result = self.collection.update_one(query, {"$set": update})
                print(f"Matched {result.matched_count} and updated {result.modified_count} documents.")
                return result.modified_count
            except Exception as e:
                print(f"Error updating data: {e}")
        else:
            print("No connection to MongoDB.")
        return 0

    def delete_data(self, query):
        """
        Delete a document from the MongoDB collection.
        :param query: A dictionary representing the query to find the document.
        """
        if self.client:
            try:
                result = self.collection.delete_one(query)
                print(f"Deleted {result.deleted_count} document.")
                return result.deleted_count
            except Exception as e:
                print(f"Error deleting data: {e}")
        else:
            print("No connection to MongoDB.")
        return 0
