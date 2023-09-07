# Importing NumPy as "np"
import pymongo
from urllib.parse import quote_plus


class MongoClient:

    @staticmethod
    def insert():
        print("Entered");
        # Replace the placeholders with your MongoDB Atlas connection details
        username = "prasanth-007"
        password = "Aws@143"
        cluster_url = "cluster0.vn5aqd9.mongodb.net"
        database_name = "db1"

        # Encode the username and password
        encoded_username = quote_plus(username)
        encoded_password = quote_plus(password)

        # Create the MongoDB URI with encoded credentials
        mongo_uri = f"mongodb+srv://{encoded_username}:{encoded_password}@{cluster_url}/{database_name}?retryWrites=true&w=majority&ssl=true"

        # Create a MongoDB client
        client = pymongo.MongoClient(mongo_uri)

        print(client)

        # Specify the database and collection where you want to insert the document
        db = client.get_database(database_name)
        collection = db.get_collection("col1")

        print(collection)

        # Create the document
        document = {
            "name": "John Doe",
            "email": "johndoe@example.com",
            "age": 30
        }

        try:
            # Attempt to insert the document into the collection
            result = collection.insert_one(document)

            # Check if the insertion was successful
            if result.acknowledged:
                print("Document inserted successfully. Inserted ID:", result.inserted_id)
            else:
                print("Document insertion failed.")
        except Exception as e:
            print("An error occurred:", str(e))
        finally:
            # Close the MongoDB client
            client.close()
