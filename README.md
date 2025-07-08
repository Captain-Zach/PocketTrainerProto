# TrainerBase

**TrainerBase** is a human-in-the-loop training application designed to simultaneously train a human user and create high-quality instructional data for fine-tuning Large Language Models (LLMs). The ultimate goal is to produce QLoRA/LoRA adapters that functionally add new, modular skills and knowledge to any AI Agent built on the same base model.

## Features

-   **Dual-Format Book Viewer:** Load and read both PDF and EPUB files.
-   **Native EPUB Rendering:** A custom Tkinter-based viewer for clean EPUB presentation.
-   **PDF Highlighting:** Select and highlight text in PDF documents.
-   **Integrated LLM Chat:** Interact with a local Gemma model via a chat interface.
-   **Context Inspector:** A dedicated window to view and modify the context being sent to the LLM.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd TrainerBase
    ```

2.  **Create and activate a virtual environment:**
    On Windows:
    ```powershell
    python -m venv .venv
    .venv\Scripts\Activate.ps1
    ```
    On macOS/Linux:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Download the Model:**
    The application is configured to use a local model from the `local_models/` directory. Make sure you have downloaded the model files (e.g., `gemma-3n-E2B-it`) and placed them in `local_models/gemma-3n-E2B-it`.
    *Note: The `local_models` directory is ignored by Git.*

## Running the Application

To run the TrainerBase GUI, execute the following command from the project's root directory:

```bash
python main.py
```