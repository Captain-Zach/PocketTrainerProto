# Manual Testing Plan

This document outlines the manual testing steps to perform to ensure the application is working as expected.

## I. Application Startup and File Loading

- [ ] **1.1: Initial State:**
  - [ ] Launch the application (`python main.py`).
  - [ ] Verify the main window appears.
  - [ ] Verify the chat panel shows "Initializing LLM..." followed by "LLM Initialized successfully."
  - [ ] Verify the `chroma_storage` directory is created in the project root.

- [ ] **1.2: Load a New PDF:**
  - [ ] Click "Choose Book" and select a PDF file that has **not** been loaded before.
  - [ ] Verify the chat panel shows an "Indexing..." message.
  - [ ] Verify a new subdirectory for the book is created in `chroma_storage`.
  - [ ] Verify the chat panel shows a "Successfully indexed..." message with a high number of chunks.
  - [ ] Verify the first page of the PDF is displayed correctly.

- [ ] **1.3: Load an Existing PDF:**
  - [ ] Close and relaunch the application.
  - [ ] Click "Choose Book" and select the **same** PDF from step 1.2.
  - [ ] Verify the chat panel shows a "Found existing database... Skipping indexing" message.
  - [ ] Verify the PDF loads much faster this time.

- [ ] **1.4: Load an EPUB:**
  - [ ] Click "Choose Book" and select an EPUB file.
  - [ ] Verify the indexing process completes successfully.
  - [ ] Verify the first chapter of the EPUB is displayed correctly.

## II. Document Interaction and Context Selection

- [ ] **2.1: PDF Highlighting:**
  - [ ] With a PDF loaded, click and drag to select a block of text.
  - [ ] Verify a yellow highlight appears on the page after releasing the mouse.
  - [ ] Verify a confirmation message is printed to the **console**.
  - [ ] Right-click the highlight and verify it is removed.

- [ ] **2.2: EPUB Selection:**
  - [ ] With an EPUB loaded, click and drag to select a block of text.
  - [ ] Verify a confirmation message is printed to the **console** after releasing the mouse.

## III. RAG and Chat Functionality

- [ ] **3.1: Basic Chat:**
  - [ ] Without selecting any text, type "Hello" into the chat and press Enter.
  - [ ] Verify your message and the LLM's response appear in the chat window.

- [ ] **3.2: Context-Aware Chat:**
  - [ ] Select a piece of text from any document (PDF or EPUB).
  - [ ] Ask a question about the selected text (e.g., "Summarize this").
  - [ ] Verify the LLM's response is relevant to the text you selected.

- [ ] **3.3: Knowledge Capture:**
  - [ ] After the LLM responds (step 3.2), check the console.
  - [ ] Verify a "Captured insight for document ID..." message appears.
  - [ ] (Optional) Use a database viewer to confirm that a new entry was added to the `already_covered_db` and `current_chapter_insights_db` for the book.

- [ ] **3.4: Context Inspector:**
  - [ ] Click the "Inspect Context" button.
  - [ ] Verify the pop-up window appears.
  - [ ] Verify the "User-Selected Text" box contains the text you highlighted in step 3.2.
  - [ ] Add a note to the "User Notes" box.
  - [ ] Click "Send to LLM".
  - [ ] Verify the window closes and the LLM responds in the main chat window.
  - [ ] Verify the console shows the master prompt, including your user note.
