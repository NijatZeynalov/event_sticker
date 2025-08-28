import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
SOURCE_MONGO_URI = 'mongodb://localhost:27017/'
SOURCE_DB_NAME = 'sticker'
DESTINATION_MONGO_URI = os.environ.get('MONGO_URI')
DESTINATION_DB_NAME = 'sticker' # Or a new name if you prefer

if not DESTINATION_MONGO_URI:
    print("Error: MONGO_URI not found in .env file.")
    exit(1)

def migrate_database():
    """
    Copies all collections and documents from a source MongoDB database to a destination database.
    """
    try:
        # --- Connect to both databases ---
        print("Connecting to source (local) MongoDB...")
        source_client = MongoClient(SOURCE_MONGO_URI)
        source_db = source_client[SOURCE_DB_NAME]
        print("Successfully connected to source.")

        print("\nConnecting to destination (Atlas) MongoDB...")
        destination_client = MongoClient(DESTINATION_MONGO_URI)
        destination_db = destination_client[DESTINATION_DB_NAME]
        print("Successfully connected to destination.")

        # --- Get list of collections from the source ---
        collections_to_migrate = source_db.list_collection_names()
        print(f"\nFound {len(collections_to_migrate)} collections to migrate: {collections_to_migrate}")

        # --- Migrate each collection ---
        for collection_name in collections_to_migrate:
            print(f"\n--- Migrating collection: '{collection_name}' ---")
            source_collection = source_db[collection_name]
            destination_collection = destination_db[collection_name]

            # Fetch all documents from the source collection
            documents = list(source_collection.find({}))
            
            if not documents:
                print(f"Collection '{collection_name}' is empty. Skipping.")
                continue

            print(f"Found {len(documents)} documents to migrate.")

            # For a clean copy, we drop the destination collection first
            print(f"Dropping destination collection '{collection_name}' to ensure a clean copy...")
            destination_db.drop_collection(collection_name)

            # Insert the documents into the destination collection
            print(f"Inserting documents into '{collection_name}' in the destination database...")
            destination_collection.insert_many(documents)
            print(f"Successfully migrated {len(documents)} documents to '{collection_name}'.")

        print("\n-----------------------------------------")
        print("Database migration completed successfully!")
        print("-----------------------------------------")

    except Exception as e:
        print(f"\nAn error occurred during migration: {e}")

    finally:
        # --- Close connections ---
        if 'source_client' in locals():
            source_client.close()
            print("Source connection closed.")
        if 'destination_client' in locals():
            destination_client.close()
            print("Destination connection closed.")

if __name__ == '__main__':
    migrate_database()
