import ebooklib
from ebooklib import epub
import os
from io import StringIO
import sys
from bs4 import BeautifulSoup
from collections import Counter

def analyze_html_tags(book):
    """
    Analyzes the HTML tags in an EPUB book and returns a frequency count.
    """
    tag_counter = Counter()
    
    # Iterate through all document items in the book
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        content = item.get_content()
        soup = BeautifulSoup(content, 'html.parser')
        
        # Find all tags and update the counter
        for tag in soup.find_all(True):
            tag_counter[tag.name] += 1
            
    return tag_counter

def analyze_epub(file_path, include_html_analysis=False):
    """
    Analyzes the structure of an EPUB file and returns the analysis as a string.
    Optionally includes an analysis of HTML tag frequency.
    """
    if not os.path.exists(file_path):
        return f"Error: File not found at '{file_path}'"

    # Redirect stdout to capture print statements
    old_stdout = sys.stdout
    sys.stdout = captured_output = StringIO()

    try:
        book = epub.read_epub(file_path)

        print("--- EPUB Analysis ---")
        print(f"File: {os.path.basename(file_path)}")
        print(f"Title: {book.get_metadata('DC', 'title')}")
        print(f"Identifier: {book.get_metadata('DC', 'identifier')}")
        print("-" * 25)

        print("\n--- Spine (Reading Order) ---")
        if book.spine:
            for i, item_id in enumerate(book.spine):
                actual_id = item_id[0] if isinstance(item_id, tuple) else item_id
                item = book.get_item_with_id(actual_id)
                if item:
                    print(f"{i+1:02d}: ID='{actual_id}', File='{item.file_name}'")
                else:
                    print(f"{i+1:02d}: ID='{actual_id}' (Item not found in manifest!)")
        else:
            print("No spine found.")
        print("-" * 25)

        if include_html_analysis:
            print("\n--- HTML Tag Frequency ---")
            tag_counts = analyze_html_tags(book)
            if tag_counts:
                # Sort by frequency, descending
                for tag, count in tag_counts.most_common():
                    print(f"{tag:<10}: {count}")
            else:
                print("No HTML tags found.")
            print("-" * 25)

        print("\n--- All Document Items in Manifest ---")
        doc_items = book.get_items_of_type(ebooklib.ITEM_DOCUMENT)
        if doc_items:
            for item in doc_items:
                print(f"ID='{item.id}', File='{item.file_name}', Media Type='{item.media_type}'")
        else:
            print("No items with type ITEM_DOCUMENT found.")
        print("-" * 25)

    finally:
        # Restore stdout
        sys.stdout = old_stdout

    return captured_output.getvalue()

if __name__ == '__main__':
    # This allows the script to be run directly for testing
    if len(sys.argv) > 1:
        file_to_analyze = sys.argv[1]
        # Add a flag to include HTML analysis when run from command line
        do_html_analysis = "--html" in sys.argv
        print(analyze_epub(file_to_analyze, include_html_analysis=do_html_analysis))
    else:
        print("Usage: python epub_analyzer.py <path_to_epub_file> [--html]")
