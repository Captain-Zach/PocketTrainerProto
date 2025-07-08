import pytest
import os
import shutil
from db_handler import DBHandler

# Pytest fixture to create a temporary directory for testing
@pytest.fixture
def temp_db_path(tmp_path):
    """Create a temporary directory for the test database."""
    return tmp_path / "test_chroma_db"

def test_db_handler_initialization(temp_db_path):
    """
    Tests if the DBHandler initializes correctly and creates its collections.
    """
    # Ensure the temp directory is clean before the test
    if os.path.exists(temp_db_path):
        shutil.rmtree(temp_db_path)

    book_id = "test_book"
    db_handler = DBHandler(book_id=book_id)

    # Check if the correct directory was created
    sanitized_id = "test_book"
    expected_path = os.path.join("./chroma_storage", sanitized_id)
    assert os.path.basename(db_handler.db_path) == sanitized_id

    # Check if collections are created
    collection_names = [col.name for col in db_handler.client.list_collections()]
    assert "full_text_source" in collection_names
    assert "already_covered_db" in collection_names
    assert "current_chapter_insights_db" in collection_names

def test_add_and_query_collection(temp_db_path):
    """
    Tests adding data to a collection and querying it.
    """
    book_id = "test_add_query_book"
    db_handler = DBHandler(book_id=book_id)
    
    # Use one of the collections for the test
    test_collection = db_handler.current_chapter_insights_db

    # Add a test document
    docs = ["This is a test document about pytest."]
    metadatas = [{"source": "test"}]
    ids = ["test_id_1"]
    
    db_handler.add_to_collection(test_collection, docs, metadatas, ids)
    
    # Verify the document was added
    assert test_collection.count() == 1
    
    # Query the collection
    query_results = db_handler.query_collection(test_collection, ["What is this document about?"])
    
    assert query_results is not None
    assert len(query_results['documents'][0]) == 1
    assert query_results['documents'][0][0] == "This is a test document about pytest."

def test_clear_collection(temp_db_path):
    """
    Tests the functionality of clearing a collection.
    """
    book_id = "test_clear_book"
    db_handler = DBHandler(book_id=book_id)
    
    collection_to_clear = db_handler.current_chapter_insights_db
    collection_name = collection_to_clear.name

    # Add some data
    db_handler.add_to_collection(
        collection_to_clear,
        documents=["doc1", "doc2"],
        metadatas=[{"s": "1"}, {"s": "2"}],
        ids=["id1", "id2"]
    )
    assert collection_to_clear.count() == 2

    # Clear the collection
    db_handler.current_chapter_insights_db = db_handler.clear_collection(collection_name)
    
    # Verify it's empty
    assert db_handler.current_chapter_insights_db.count() == 0
