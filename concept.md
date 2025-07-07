# TrainerBase: Concept and Vision

## High-Level Concept

**TrainerBase** is a human-in-the-loop training application designed for curating high-quality instructional data for Large Language Models (LLMs).

The core workflow involves a human operator and a local LLM working together to review source material (initially books in PDF or EPUB format) page by page. As they explore the content, they collaboratively generate training data, complete exercises, and refine the model's understanding of the material.

The application serves as the primary interface for this interaction, providing the necessary tools for both the human and the AI to view, analyze, and manipulate the source content.

---

## Core Functionality (Current Implementation)

The application is built in Python using the Tkinter framework for the GUI and the PyMuPDF (fitz) library for robust PDF rendering and interaction.

### Key Features:

1.  **Dual-Format Book Viewer:**
    -   Loads and displays both PDF and EPUB files.
    -   The viewer dynamically resizes to fit the content of the loaded document.

2.  **PDF Interaction:**
    -   **Page Navigation:** Users can navigate through PDF documents page by page using "Next" and "Previous" buttons.
    -   **Mouse-Based Text Highlighting:** Users can click and drag the mouse to draw a selection rectangle over text. Upon release, the selected area is highlighted with a semi-transparent yellow overlay.
    -   **Highlight Removal:** Users can right-click on any highlighted area to instantly remove the highlight.

3.  **State Management:**
    -   The application is built within a class structure that properly manages the state of the loaded document, including page numbers and in-memory modifications like highlights.
    -   This robust structure prevents the caching and state-related issues often found in simpler Tkinter applications.

---

## Future Vision (LLM Integration)

The current feature set provides the foundation for the primary goal: LLM integration. Future development will focus on:

-   **Programmatic Highlighting:** Allowing the LLM to programmatically highlight text on the PDF page to draw the user's attention to specific passages.
-   **Text Extraction:** Feeding the text from user-selected or LLM-selected highlights into the language model as context.
-   **Interactive Q&A:** Creating a panel where the user and the LLM can discuss the content of the book.
-   **Saving and Exporting:** Saving the highlighted annotations directly to the PDF file and exporting the curated text pairs (e.g., "Question from book" + "Answer from LLM") as training data.
