# Session Planning: Local LLM Integration

This document outlines the next steps for integrating a local Large Language Model (LLM) into the TrainerBase application.

## Phase 1: Core LLM Setup

*   **Model Selection:** We will be using Gemma 3n (gemma-3n-E2B-it found at -> https://huggingface.co/google/gemma-3n-E2B-it). 
*   **Inference Library:** We will use the Hugging Face `transformers` library. This approach is best for our goal of packaging the application into a single executable, as it allows the model and inference logic to be bundled directly with our Python code, avoiding external dependencies like Ollama or complex C++ bindings like llama.cpp.
*   **API Wrapper:** Create a Python class to abstract the communication with the LLM's API. This will handle sending prompts and receiving responses.

## Phase 2: Infrastructure and UI Integration

*   **Chat Interface:** Develop a simple chat interface within the existing `test_main.py` GUI.
*   **Prompt Engineering:** Design and test initial prompts for interacting with the LLM in the context of the document viewer.
*   **Context Management:** Implement a mechanism to pass relevant text selections from the document viewer to the LLM as context.

## Phase 3: Advanced Features

*   **Vector Database:** Integrate a vector database (User choses ChromaDB) for Retrieval Augmented Generation (RAG).
*   **Document Indexing:** Create a process to chunk, embed, and index the content of the documents in the `DocSource` directory.
*   **RAG-powered Chat:** Enhance the chat functionality to use the vector database to retrieve relevant document chunks and inject them into the LLM prompt, providing more contextually aware answers.

## Targets of Opportunity

*   Make the model path configurable instead of being hardcoded.
*   Investigate GPU acceleration options with the `transformers` library.
*   Fix left panel layout to ensure bottom buttons are always visible.
*   Implement token counting and context truncation to manage the 8192 token limit.
*   Include licensing information in the title screen or home page
