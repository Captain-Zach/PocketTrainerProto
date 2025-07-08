import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import fitz  # PyMuPDF
from PIL import Image, ImageTk
from ebooklib import epub, ITEM_DOCUMENT
import os
import sys
from Scripts.epub_analyzer import analyze_epub
from native_viewer import NativeEpubViewer
import re
from bs4 import BeautifulSoup
from llm_handler import LLMHandler
from db_handler import DBHandler

class TrainerBaseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TrainerBase (Test Version - Native Viewer)")
        self.root.geometry("800x600")

        # Document state
        self.doc = None
        self.epub_book = None
        self.epub_book_path = None
        self.page_num = 0
        self.pdf_image = None
        self.epub_chapters = []
        self.epub_chapter_index = 0
        self.href_map = {}

        # LLM and DB Handlers
        self.llm_handler = None
        self.db_handler = None # Will be initialized when a book is chosen

        # LLM Context State
        self.system_prompt = "You are an expert AI Tutor. Your goal is to guide the user through the provided document context..."
        self.user_selected_text = ""
        self.conversation_history = []
        self.user_notes = ""
        self.task_prompt = "Based on all the context above, continue the tutoring session..."

        # Highlighting state
        self.selection_start = None
        self.selection_rect = None

        # Viewer frames
        self.pdf_viewer_frame = None
        self.epub_viewer_frame = None
        
        # --- GUI Setup ---
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left column (info panel)
        self.left_frame = tk.Frame(main_frame, width=250)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False)
        self.left_frame.pack_propagate(False)

        tk.Label(self.left_frame, text="TrainerBase GUI").pack(pady=10)

        # Info panel
        self.info_text = tk.StringVar()
        info_label = tk.Label(self.left_frame, textvariable=self.info_text, justify='left', anchor='w', font=("Segoe UI", 12), bg="#f0f0f0", relief=tk.SUNKEN, wraplength=240)
        info_label.pack(pady=5, fill=tk.X)
        self.update_info_panel("No book loaded", "N/A", "N/A")

        # Buttons
        button_frame = tk.Frame(self.left_frame)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="Choose Book", command=self.choose_book).pack(side=tk.LEFT, padx=5)
        
        self.prev_button = tk.Button(button_frame, text="Previous", command=self.previous_page, state=tk.DISABLED)
        self.prev_button.pack(side=tk.LEFT, padx=5)
        
        self.next_button = tk.Button(button_frame, text="Next", command=self.next_page, state=tk.DISABLED)
        self.next_button.pack(side=tk.LEFT, padx=5)

        # Analysis button
        self.analyze_button = tk.Button(self.left_frame, text="Analyze EPUB", command=self.run_analysis, state=tk.DISABLED)
        self.analyze_button.pack(pady=5)

        # --- LLM Chat Section ---
        llm_frame = tk.LabelFrame(self.left_frame, text="Chat with LLM", padx=5, pady=5)
        llm_frame.pack(pady=10, fill=tk.X, expand=False)

        self.chat_display = scrolledtext.ScrolledText(llm_frame, wrap=tk.WORD, height=15, state=tk.DISABLED)
        self.chat_display.pack(pady=5, fill=tk.X)

        self.chat_input = tk.Entry(llm_frame, width=30)
        self.chat_input.pack(pady=5, fill=tk.X)
        self.chat_input.bind("<Return>", self.ask_llm)

        self.ask_button = tk.Button(llm_frame, text="Ask", command=self.ask_llm)
        self.ask_button.pack(pady=5)

        # --- Bottom Buttons ---
        bottom_frame = tk.Frame(self.left_frame)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        self.inspect_button = tk.Button(bottom_frame, text="Inspect Context", command=self.open_context_inspector)
        self.inspect_button.pack(side=tk.LEFT, padx=5)

        tk.Button(bottom_frame, text="Exit", command=self.root.destroy).pack(side=tk.RIGHT, padx=5)


        # Right column (book viewer)
        self.right_frame = tk.Frame(main_frame)
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20, 0))

        # Initialize the LLM
        self.initialize_llm()

    def open_context_inspector(self):
        """
        Opens a new window to inspect and edit the context that will be sent to the LLM.
        """
        inspector_window = tk.Toplevel(self.root)
        inspector_window.title("Context Inspector")
        inspector_window.geometry("700x900")

        main_pane = tk.PanedWindow(inspector_window, orient=tk.VERTICAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- System Prompt Frame ---
        system_frame = tk.LabelFrame(main_pane, text="System Prompt (The AI's Role & Goal)", padx=5, pady=5)
        main_pane.add(system_frame, height=150)
        
        system_prompt_text = scrolledtext.ScrolledText(system_frame, wrap=tk.WORD, height=5)
        system_prompt_text.pack(fill=tk.BOTH, expand=True)
        system_prompt_text.insert(tk.END, self.system_prompt)

        # --- Context Block Frame ---
        context_frame = tk.LabelFrame(main_pane, text="Context Block (The Knowledge Base)", padx=5, pady=5)
        main_pane.add(context_frame)

        context_pane = tk.PanedWindow(context_frame, orient=tk.VERTICAL)
        context_pane.pack(fill=tk.BOTH, expand=True)

        # Selected Text
        selected_text_frame = tk.LabelFrame(context_pane, text="User-Selected Text", padx=5, pady=5)
        context_pane.add(selected_text_frame, height=150)
        selected_text = scrolledtext.ScrolledText(selected_text_frame, wrap=tk.WORD, height=5, state=tk.DISABLED)
        selected_text.pack(fill=tk.BOTH, expand=True)
        selected_text.config(state=tk.NORMAL)
        selected_text.insert(tk.END, self.user_selected_text or "No text selected.")
        selected_text.config(state=tk.DISABLED)


        # Conversation History
        history_frame = tk.LabelFrame(context_pane, text="Conversation History", padx=5, pady=5)
        context_pane.add(history_frame, height=150)
        history_text = scrolledtext.ScrolledText(history_frame, wrap=tk.WORD, height=5, state=tk.DISABLED)
        history_text.pack(fill=tk.BOTH, expand=True)
        history_text.config(state=tk.NORMAL)
        history_str = "\n".join(self.conversation_history)
        history_text.insert(tk.END, history_str or "No history yet.")
        history_text.config(state=tk.DISABLED)

        # User Notes
        notes_frame = tk.LabelFrame(context_pane, text="User Notes (Add specific instructions for the next turn)", padx=5, pady=5)
        context_pane.add(notes_frame, height=100)
        user_notes_text = scrolledtext.ScrolledText(notes_frame, wrap=tk.WORD, height=4)
        user_notes_text.pack(fill=tk.BOTH, expand=True)
        user_notes_text.insert(tk.END, self.user_notes)

        # --- Task Frame ---
        task_frame = tk.LabelFrame(main_pane, text="Task (The Immediate Action)", padx=5, pady=5)
        main_pane.add(task_frame, height=100)
        
        task_text = scrolledtext.ScrolledText(task_frame, wrap=tk.WORD, height=3)
        task_text.pack(fill=tk.BOTH, expand=True)
        task_text.insert(tk.END, self.task_prompt)
        task_text.config(state=tk.DISABLED)

        # --- Bottom Buttons ---
        button_frame = tk.Frame(inspector_window)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Button(button_frame, text="Send to LLM", command=lambda: self.ask_llm_from_inspector(
            inspector_window,
            system_prompt_text.get("1.0", tk.END),
            user_notes_text.get("1.0", tk.END)
        )).pack(side=tk.RIGHT, padx=5)
        tk.Button(button_frame, text="Close", command=inspector_window.destroy).pack(side=tk.RIGHT)

        inspector_window.transient(self.root)
        inspector_window.grab_set()
        self.root.wait_window(inspector_window)

    def _truncate_text(self, text, tokenizer, max_tokens):
        """Truncates text to a maximum number of tokens."""
        tokens = tokenizer.encode(text)
        if len(tokens) > max_tokens:
            truncated_tokens = tokens[:max_tokens]
            return tokenizer.decode(truncated_tokens, skip_special_tokens=True) + "..."
        return text

    def _build_master_prompt(self, user_input, tokenizer):
        """Builds the complete prompt string from all context sources, managing token limits."""
        
        # Define the token budget
        CONTEXT_BUDGET = 7680 # 8192 total, with a 512 buffer for the response
        
        # --- 1. Calculate Fixed Costs ---
        # These are the parts of the prompt that are always included.
        fixed_template = f"""# SYSTEM PROMPT
{self.system_prompt}
---
# CONTEXT BLOCK
## [Relevant Prior Knowledge (from already_covered_db)]
{{retrieved_doc_context}}
## [User-Selected Text]
{{user_selected_text}}
## [Relevant Current Insights (from current_chapter_insights_db)]
{{current_chapter_insights}}
## [Conversation History]
{{history_str}}
## [User Notes]
{{user_notes}}
---
# TASK BLOCK
{self.task_prompt}
## [User Message]
{user_input}
"""
        base_tokens = len(tokenizer.encode(fixed_template))
        remaining_budget = CONTEXT_BUDGET - base_tokens

        # --- 2. Allocate Budget to Dynamic Content ---
        # Start with the most important context and work down.
        
        # User-Selected Text (High Priority)
        user_selected_text_tokens = int(remaining_budget * 0.4) # 40% of remaining budget
        truncated_selected_text = self._truncate_text(self.user_selected_text, tokenizer, user_selected_text_tokens)
        remaining_budget -= len(tokenizer.encode(truncated_selected_text))

        # Conversation History (Medium Priority)
        history_tokens = int(remaining_budget * 0.5) # 50% of what's left
        
        # Truncate history from the beginning
        truncated_history = self.conversation_history[:]
        while len(tokenizer.encode("\n".join(truncated_history))) > history_tokens:
            if not truncated_history: break
            truncated_history.pop(0)
        history_str = "\n".join(truncated_history) or "N/A"
        remaining_budget -= len(tokenizer.encode(history_str))

        # Retrieved Context (Low Priority) - Split remaining budget between the two DBs
        db_context_tokens = int(remaining_budget * 0.45) # Use 45% of what's left for each DB query

        query_text = user_input or self.user_selected_text
        
        retrieved_docs = self.db_handler.query_collection(self.db_handler.already_covered_db, [query_text], n_results=2)
        retrieved_doc_context = "\n".join(retrieved_docs['documents'][0]) if retrieved_docs and retrieved_docs['documents'] else "N/A"
        truncated_retrieved_docs = self._truncate_text(retrieved_doc_context, tokenizer, db_context_tokens)

        insights = self.db_handler.query_collection(self.db_handler.current_chapter_insights_db, [query_text], n_results=2)
        current_chapter_insights = "\n".join(insights['documents'][0]) if insights and insights['documents'] else "N/A"
        truncated_insights = self._truncate_text(current_chapter_insights, tokenizer, db_context_tokens)

        # --- 3. Assemble the Final Prompt ---
        final_prompt = fixed_template.format(
            retrieved_doc_context=truncated_retrieved_docs,
            user_selected_text=truncated_selected_text or "N/A",
            current_chapter_insights=truncated_insights,
            history_str=history_str,
            user_notes=self.user_notes or "N/A"
        )

        return final_prompt

    def ask_llm_from_inspector(self, window, system_prompt, user_notes):
        """Gathers context from the inspector window and sends it to the LLM."""
        # Update the main app's state from the inspector's text boxes
        self.system_prompt = system_prompt.strip()
        self.user_notes = user_notes.strip()
        
        user_input = "[Prompt sent from Inspector]"
        self.add_to_chat(user_input)
        self.conversation_history.append(user_input)

        # Build the full prompt using the (potentially edited) context
        final_prompt = self._build_master_prompt(user_input, self.llm_handler.tokenizer)
        
        print("--- MASTER PROMPT (Inspector) ---")
        print(final_prompt)
        print("---------------------------------")

        # Generate response
        response = self.llm_handler.generate_response(final_prompt)
        
        llm_message = f"LLM: {response}"
        self.add_to_chat(llm_message)
        self.conversation_history.append(llm_message)
        
        self._capture_insight(response)
        window.destroy()

    def initialize_llm(self):
        self.add_to_chat("Initializing LLM... This may take a moment.")
        self.root.update_idletasks() # Update UI to show message
        
        local_model_dir = os.path.join(os.path.dirname(__file__), "local_models", "gemma-3n-E2B-it")
        self.llm_handler = LLMHandler(model_path=local_model_dir)
        
        if self.llm_handler and self.llm_handler.model:
            self.add_to_chat("LLM Initialized successfully.")
        else:
            self.add_to_chat("Error: LLM failed to initialize. Check console for details.")

    def add_to_chat(self, message):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, message + "\n\n")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)

    def ask_llm(self, event=None):
        if not self.llm_handler or not self.llm_handler.model:
            self.add_to_chat("LLM is not ready.")
            return

        user_prompt = self.chat_input.get()
        if not user_prompt:
            return

        user_message = f"You: {user_prompt}"
        self.add_to_chat(user_message)
        self.conversation_history.append(user_message)
        self.chat_input.delete(0, tk.END)
        
        self.chat_input.config(state=tk.DISABLED)
        self.ask_button.config(state=tk.DISABLED)
        self.root.update_idletasks()

        # Build the master prompt
        final_prompt = self._build_master_prompt(user_prompt, self.llm_handler.tokenizer)

        # Generate response
        response = self.llm_handler.generate_response(final_prompt)
        
        llm_message = f"LLM: {response}"
        self.add_to_chat(llm_message)
        self.conversation_history.append(llm_message)

        self._capture_insight(response)

        self.chat_input.config(state=tk.NORMAL)
        self.ask_button.config(state=tk.NORMAL)

    def _capture_insight(self, insight_text):
        """Adds the last selected text and the new insight to the databases."""
        if not self.db_handler or not self.user_selected_text:
            return

        # Use a hash of the selected text as a simple, unique ID
        doc_id = f"doc_{hash(self.user_selected_text)}"
        insight_id = f"insight_{hash(self.user_selected_text)}"

        # Add the original text to the 'already_covered' DB
        self.db_handler.add_to_collection(
            self.db_handler.already_covered_db,
            documents=[self.user_selected_text],
            metadatas=[{"source": "user_selection"}],
            ids=[doc_id]
        )

        # Add the LLM's response to the 'insights' DB
        self.db_handler.add_to_collection(
            self.db_handler.current_chapter_insights_db,
            documents=[insight_text],
            metadatas=[{"source_doc_id": doc_id}],
            ids=[insight_id]
        )

        print(f"Captured insight for document ID: {doc_id}")
        # Clear the selected text after processing to avoid re-capturing
        self.user_selected_text = ""

    def update_info_panel(self, book, skill, section):
        self.info_text.set(f"Current Book: {book}\nTargeted Skill: {skill}\nCurrent Section: {section}")

    def choose_book(self, event=None):
        # Set the initial directory to the 'DocSource' folder
        initial_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "DocSource")

        file_path = filedialog.askopenfilename(
            initialdir=initial_dir,
            title="Select Book",
            filetypes=[
                ("Supported Files", "*.epub *.pdf"),
                ("EPUB files", "*.epub"), 
                ("PDF files", "*.pdf")
            ]
        )
        if file_path:
            # Reset state before opening a new book
            self.doc = None
            self.epub_book = None
            self.epub_book_path = None
            self.epub_chapters = []
            self.href_map = {}
            self.page_num = 0
            self.epub_chapter_index = 0
            
            # Create a book-specific ID
            book_id = os.path.splitext(os.path.basename(file_path))[0]
            
            # Initialize the DB Handler for this specific book
            self.db_handler = DBHandler(book_id=book_id)

            # Check if the book is already indexed
            if self.db_handler.full_text_source.count() == 0:
                self._process_and_index_document(file_path, book_id)
            else:
                self.add_to_chat(f"Found existing database for {book_id}. Skipping indexing.")

            if file_path.lower().endswith('.pdf'):
                self.open_pdf(file_path)
            elif file_path.lower().endswith('.epub'):
                self.open_epub(file_path)

    def _process_and_index_document(self, file_path, book_id):
        """Extracts text from a document, chunks it, and indexes it in the DB."""
        self.add_to_chat(f"Indexing {os.path.basename(file_path)}... Please wait.")
        self.root.update_idletasks()

        documents, metadatas, ids = [], [], []
        
        try:
            if file_path.lower().endswith('.pdf'):
                with fitz.open(file_path) as doc:
                    for i, page in enumerate(doc):
                        # Use get_text("blocks") to approximate paragraphs
                        blocks = page.get_text("blocks")
                        for j, block in enumerate(blocks):
                            text = block[4].strip()
                            if text: # Ensure block is not just whitespace
                                documents.append(text)
                                metadatas.append({"source": book_id, "page_num": i, "block_num": j})
                                ids.append(f"{book_id}_page_{i}_block_{j}")

            elif file_path.lower().endswith('.epub'):
                book = epub.read_epub(file_path)
                for i, item in enumerate(book.get_items_of_type(ITEM_DOCUMENT)):
                    soup = BeautifulSoup(item.get_content(), 'html.parser')
                    text = soup.get_text()
                    if text.strip():
                        # Chunk by paragraph for EPUB sections
                        chunks = [chunk.strip() for chunk in text.split('\n\n') if chunk.strip()]
                        for j, chunk in enumerate(chunks):
                            documents.append(chunk)
                            metadatas.append({"source": book_id, "item_num": i, "chunk_num": j})
                            ids.append(f"{book_id}_item_{i}_chunk_{j}")
        
        except Exception as e:
            self.add_to_chat(f"Error processing document: {e}")
            return

        if not documents:
            self.add_to_chat("Could not extract any text chunks from the document.")
            return

        # Add new data to the full_text_source collection
        self.db_handler.add_to_collection(
            self.db_handler.full_text_source,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        self.add_to_chat(f"Successfully indexed {len(documents)} text chunks.")

    def open_pdf(self, file_path):
        if self.epub_viewer_frame:
            self.epub_viewer_frame.pack_forget()
            self.epub_viewer_frame = None
        
        if not self.pdf_viewer_frame:
            self.pdf_viewer_frame = tk.Frame(self.right_frame)
            self.pdf_viewer_frame.pack(fill=tk.BOTH, expand=True)
            self.canvas = tk.Canvas(self.pdf_viewer_frame)
            self.canvas.pack(fill=tk.BOTH, expand=True)
            # Bind mouse events for highlighting
            self.canvas.bind("<ButtonPress-1>", self.start_selection)
            self.canvas.bind("<B1-Motion>", self.update_selection)
            self.canvas.bind("<ButtonRelease-1>", self.end_selection)
            self.canvas.bind("<Button-3>", self.remove_highlight) # Right-click
        
        self.pdf_viewer_frame.pack(fill=tk.BOTH, expand=True)

        try:
            self.doc = fitz.open(file_path)
            self.page_num = 0
            self.display_page()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open PDF: {e}")
            self.doc = None
        
        self.update_navigation_buttons()

    def display_page(self):
        if not self.doc:
            return

        page = self.doc.load_page(self.page_num)
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        self.pdf_image = ImageTk.PhotoImage(image=img)
        
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor='nw', image=self.pdf_image)
        
        self.root.update_idletasks()
        left_panel_width = self.left_frame.winfo_width()
        window_width = pix.width + left_panel_width + 40
        window_height = pix.height + 40
        self.root.geometry(f"{window_width}x{window_height}")
        self.canvas.config(width=pix.width, height=pix.height)
        
        self.update_info_panel(os.path.basename(self.doc.name), "Reading", f"Page {self.page_num + 1} of {self.doc.page_count}")
        self.update_navigation_buttons()

    def start_selection(self, event):
        self.selection_start = (event.x, event.y)
        self.selection_rect = self.canvas.create_rectangle(event.x, event.y, event.x, event.y, outline='red', width=1, dash=(4, 4))

    def update_selection(self, event):
        if self.selection_rect:
            x0, y0 = self.selection_start
            x1, y1 = event.x, event.y
            self.canvas.coords(self.selection_rect, x0, y0, x1, y1)

    def end_selection(self, event):
        if self.selection_start:
            x0, y0 = self.selection_start
            x1, y1 = event.x, event.y
            self.selection_start = None
            if self.selection_rect:
                self.canvas.delete(self.selection_rect)
                self.selection_rect = None

            rect_coords = (min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))
            
            if self.doc:
                page = self.doc.load_page(self.page_num)
                fitz_rect = fitz.Rect(rect_coords)
                
                # Extract text and update context variable
                extracted_text = page.get_text("text", clip=fitz_rect).strip()
                if extracted_text:
                    self.user_selected_text = extracted_text
                    print(f"Context Updated: Selected text of {len(extracted_text)} chars.")
                
                # Add the visual highlight to the page
                page.add_highlight_annot(fitz_rect)
                self.display_page() # Redraw the page to show the new highlight

    def remove_highlight(self, event):
        if not self.doc:
            return
        click_point = fitz.Point(event.x, event.y)
        page = self.doc.load_page(self.page_num)
        annots = page.annots()
        if annots:
            for annot in annots:
                if click_point in annot.rect:
                    page.delete_annot(annot)
                    self.display_page() # Redraw the page to remove the highlight
                    break

    def next_page(self):
        if self.doc: # PDF navigation
            if self.page_num < self.doc.page_count - 1:
                self.page_num += 1
                self.display_page()
        elif self.epub_book: # EPUB navigation
            if self.epub_chapter_index < len(self.epub_chapters) - 1:
                self.epub_chapter_index += 1
                self.display_epub_chapter(self.epub_chapter_index)

    def previous_page(self):
        if self.doc: # PDF navigation
            if self.page_num > 0:
                self.page_num -= 1
                self.display_page()
        elif self.epub_book: # EPUB navigation
            if self.epub_chapter_index > 0:
                self.epub_chapter_index -= 1
                self.display_epub_chapter(self.epub_chapter_index)

    def update_navigation_buttons(self):
        self.analyze_button.config(state=tk.NORMAL if self.epub_book else tk.DISABLED)
        if self.doc:
            self.prev_button.config(state=tk.NORMAL if self.page_num > 0 else tk.DISABLED)
            self.next_button.config(state=tk.NORMAL if self.page_num < self.doc.page_count - 1 else tk.DISABLED)
        elif self.epub_book:
            self.prev_button.config(state=tk.NORMAL if self.epub_chapter_index > 0 else tk.DISABLED)
            self.next_button.config(state=tk.NORMAL if self.epub_chapter_index < len(self.epub_chapters) - 1 else tk.DISABLED)
        else:
            self.prev_button.config(state=tk.DISABLED)
            self.next_button.config(state=tk.DISABLED)

    def open_epub(self, file_path):
        if self.pdf_viewer_frame:
            self.pdf_viewer_frame.pack_forget()
            self.pdf_viewer_frame = None

        if not self.epub_viewer_frame:
            self.epub_viewer_frame = NativeEpubViewer(
                self.right_frame, 
                selection_callback=self.update_epub_selection_context
            )
            self.epub_viewer_frame.pack(fill=tk.BOTH, expand=True)
        
        try:
            self.epub_book_path = file_path
            self.epub_book = epub.read_epub(file_path)
            
            spine_ids = []
            for item_id in self.epub_book.spine:
                actual_id = item_id[0] if isinstance(item_id, tuple) else item_id
                spine_ids.append(actual_id)

            all_items = {item.id: item for item in self.epub_book.get_items()}
            
            self.epub_chapters = []
            for item_id in spine_ids:
                item = all_items.get(item_id)
                if item and item.get_type() == ITEM_DOCUMENT:
                    if 'toc' not in item.file_name.lower() and 'cover' not in item.file_name.lower():
                        self.epub_chapters.append(item)
            
            self.href_map = {item.file_name: i for i, item in enumerate(self.epub_chapters)}

            if self.epub_chapters:
                self.epub_chapter_index = 0
                self.display_epub_chapter(self.epub_chapter_index)
            else:
                messagebox.showinfo("Info", "No content chapters found in this EPUB.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to open EPUB: {e}")
            self.epub_book = None
        
        self.update_navigation_buttons()

    def update_epub_selection_context(self, selected_text):
        """
        Callback function for the NativeEpubViewer to update the selected text context.
        """
        self.user_selected_text = selected_text
        print(f"Context Updated: Selected EPUB text of {len(selected_text)} chars.")

    def display_epub_chapter(self, chapter_index):
        if not self.epub_chapters:
            return
            
        self.epub_chapter_index = chapter_index
        item = self.epub_chapters[chapter_index]
        html_content = item.get_content()
        
        self.epub_viewer_frame.render_chapter(html_content, self.epub_link_clicked)

        book_name = os.path.basename(self.epub_book_path)
        self.update_info_panel(book_name, "Reading", f"Chapter {chapter_index + 1} of {len(self.epub_chapters)}")
        
        self.update_navigation_buttons()

    def epub_link_clicked(self, url):
        if not self.epub_book:
            return

        target_filename = os.path.basename(url.split('#')[0])
        target_index = self.href_map.get(target_filename)

        if target_index is not None:
            self.display_epub_chapter(target_index)
        else:
            print(f"Could not find chapter for href: {target_filename}")

    def run_analysis(self):
        if not self.epub_book_path:
            messagebox.showinfo("Info", "No EPUB file is currently loaded.")
            return
        
        analysis_text = analyze_epub(self.epub_book_path, include_html_analysis=True)
        
        analysis_window = tk.Toplevel(self.root)
        analysis_window.title("EPUB Analysis")
        analysis_window.geometry("600x700")
        
        text_area = scrolledtext.ScrolledText(analysis_window, wrap=tk.WORD, width=80, height=40)
        text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        text_area.insert(tk.INSERT, analysis_text)
        text_area.config(state=tk.DISABLED)

def main():
    """Main function to run the app or CLI."""
    # This version does not support CLI arguments
    root = tk.Tk()
    app = TrainerBaseApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
