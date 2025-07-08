import chromadb
import os
import re

class DBHandler:
    def __init__(self, book_id):
        """
        Initializes the database handler for a specific book.
        """
        # Sanitize book_id to be a valid directory name
        safe_book_id = re.sub(r'[^a-zA-Z0-9_-]', '_', book_id)
        self.db_path = os.path.join("./chroma_storage", safe_book_id)
        
        # Ensure the database directory exists
        os.makedirs(self.db_path, exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=self.db_path)
        
        # The three databases (collections in ChromaDB terms)
        self.full_text_source = self.client.get_or_create_collection(
            name="full_text_source"
        )
        self.already_covered_db = self.client.get_or_create_collection(
            name="already_covered_db"
        )
        self.current_chapter_insights_db = self.client.get_or_create_collection(
            name="current_chapter_insights_db"
        )
        
        print(f"Database handler initialized for book '{book_id}' at {self.db_path}")
        print(f"Collections: {self.client.list_collections()}")

    def add_to_collection(self, collection, documents, metadatas, ids):
        """
        Adds documents to a specified collection.
        
        Args:
            collection: The ChromaDB collection object.
            documents (list): A list of document strings to add.
            metadatas (list): A list of metadata dictionaries.
            ids (list): A list of unique string IDs for each document.
        """
        if not documents:
            return
        
        try:
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            print(f"Added {len(documents)} documents to '{collection.name}'.")
        except Exception as e:
            print(f"Error adding to collection '{collection.name}': {e}")

    def query_collection(self, collection, query_texts, n_results=3):
        """
        Queries a collection to find the most relevant documents.
        
        Args:
            collection: The ChromaDB collection object.
            query_texts (list): The text(s) to search for.
            n_results (int): The number of results to return.
            
        Returns:
            A dictionary containing the query results.
        """
        if not query_texts or collection.count() == 0:
            return None
            
        try:
            results = collection.query(
                query_texts=query_texts,
                n_results=min(n_results, collection.count()) # Ensure n_results is not > items in collection
            )
            return results
        except Exception as e:
            print(f"Error querying collection '{collection.name}': {e}")
            return None

    def clear_collection(self, collection_name):
        """
        Deletes and recreates a collection to clear its contents.
        """
        try:
            self.client.delete_collection(name=collection_name)
            new_collection = self.client.create_collection(name=collection_name)
            print(f"Successfully cleared and recreated collection: {collection_name}")
            return new_collection
        except Exception as e:
            print(f"Error clearing collection '{collection_name}': {e}")
            # If deletion fails, try to get the collection anyway
            return self.client.get_or_create_collection(name=collection_name)

if __name__ == '__main__':
    # Test the DBHandler
    print("Testing DBHandler...")
    test_book_id = "test_book_1"
    db_handler = DBHandler(book_id=test_book_id)
    
    # Clear for a fresh run
    db_handler.current_chapter_insights_db = db_handler.clear_collection("current_chapter_insights_db")

    # Add a test insight
    db_handler.add_to_collection(
        collection=db_handler.current_chapter_insights_db,
        documents=["This is a test insight about Python classes."],
        metadatas=[{"source": "chapter_1_section_1"}],
        ids=["test_id_1"]
    )
    
    # Query for the insight
    results = db_handler.query_collection(
        collection=db_handler.current_chapter_insights_db,
        query_texts=["What do I know about classes?"]
    )
    
    print("\nQuery Results:")
    if results and results.get('documents'):
        print(results['documents'][0])
    else:
        print("No results found.")

    print("\nDBHandler test complete.")