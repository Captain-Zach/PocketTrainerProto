# TrainerBase: Concept and Vision

## High-Level Concept

**TrainerBase** is a human-in-the-loop training application designed to simultaneously train a human user and create high-quality instructional data for fine-tuning Large Language Models (LLMs).

The ultimate goal is to produce QLoRA/LoRA adapters that functionally add new, modular skills and knowledge to any AI Agent built on the same base model.

## The Evolving Vision

The project began with a simple idea: a Python-based game where a user and an AI "Study Buddy" would learn together from a programming book. The initial focus was on collaborative learning, using methods like "Teach-Back" and Socratic questioning to generate question-and-answer pairs for later use.

The concept quickly evolved from a human-led learning tool to a semi-automated process driven by an AI "TutorBot." In this model, the AI takes the lead in introducing concepts, checking the user's understanding, and guiding them through exercises, managing the entire learning session.

This led to the current, more ambitious vision: a system that doesn't just educate a human, but uses that interactive process to generate the precise data needed to train and create modular, transferable skills for an AI.

## Core Workflow

The core workflow involves a human operator and a local LLM working together to review source material (initially books in PDF or EPUB format) page by page. As they explore the content, they collaboratively generate training data, complete exercises, and refine the model's understanding of the material.

The application serves as the primary interface for this interaction, providing the necessary tools for both the human and the AI to view, analyze, and manipulate the source content.

---

## Core Functionality (Current Implementation)

The application is built in Python using the Tkinter framework for the GUI.

### Key Features:

1.  **Dual-Format Book Viewer:**
    -   Loads and displays both PDF (using PyMuPDF) and EPUB files (using a native Tkinter viewer).
    -   The viewer dynamically resizes to fit the content of the loaded document.

2.  **PDF Interaction:**
    -   **Page Navigation:** Users can navigate through PDF documents page by page.
    -   **Highlighting:** The viewer supports adding and removing highlights on PDF documents (functionality to be added for EPUBs).

3.  **LLM Integration:**
    -   **Local Model:** Integrates a local LLM (Gemma) using the `transformers` library.
    -   **Chat Interface:** Provides a basic chat panel for interacting with the LLM.

---

## Future Vision (Systematizing the Training)

The current feature set provides the foundation for the primary goal: creating a systematic process for generating LoRA adapters. Future development will focus on:

-   **Context Framing:** Building a dedicated UI to structure and send context (eg., selected text, user notes, previous conversation) to the LLM.
-   **Programmatic Highlighting:** Allowing the LLM to programmatically highlight text on the PDF/EPUB to draw the user's attention to specific passages.
-   **Structured Data Export:** Moving beyond simple Q&A pairs to a structured format suitable for QLoRA/LoRA fine-tuning.
-   **Saving and Exporting:** Saving annotations and exporting the curated training data.