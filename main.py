import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import fitz  # PyMuPDF
from PIL import Image, ImageTk
from ebooklib import epub, ITEM_DOCUMENT
import os
import sys
from Scripts.epub_analyzer import analyze_epub
from native_viewer import NativeEpubViewer
from llm_handler import LLMHandler

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

        # LLM Handler
        self.llm_handler = None

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


        tk.Button(self.left_frame, text="Exit", command=self.root.destroy).pack(side=tk.BOTTOM, pady=20)


        # Right column (book viewer)
        self.right_frame = tk.Frame(main_frame)
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20, 0))

        # Initialize the LLM
        self.initialize_llm()

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
        
        self.add_to_chat(f"You: {user_prompt}")
        self.chat_input.delete(0, tk.END)
        
        # Disable input while generating
        self.chat_input.config(state=tk.DISABLED)
        self.ask_button.config(state=tk.DISABLED)
        self.root.update_idletasks()

        # Reworked prompt for conversational chat
        chat_prompt = (
            "You are a friendly and helpful chat assistant. "
            "Please provide a conversational response to the user's message.\n\n"
            f"User: {user_prompt}\n"
            "Assistant:"
        )

        # Generate response
        response = self.llm_handler.generate_response(chat_prompt)
        self.add_to_chat(f"LLM: {response}")

        # Re-enable input
        self.chat_input.config(state=tk.NORMAL)
        self.ask_button.config(state=tk.NORMAL)

    def update_info_panel(self, book, skill, section):
        self.info_text.set(f"Current Book: {book}\nTargeted Skill: {skill}\nCurrent Section: {section}")

    def choose_book(self):
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

            if file_path.lower().endswith('.pdf'):
                self.open_pdf(file_path)
            elif file_path.lower().endswith('.epub'):
                self.open_epub(file_path)

    def open_pdf(self, file_path):
        if self.epub_viewer_frame:
            self.epub_viewer_frame.pack_forget()
            self.epub_viewer_frame = None
        
        if not self.pdf_viewer_frame:
            self.pdf_viewer_frame = tk.Frame(self.right_frame)
            self.pdf_viewer_frame.pack(fill=tk.BOTH, expand=True)
            self.canvas = tk.Canvas(self.pdf_viewer_frame)
            self.canvas.pack(fill=tk.BOTH, expand=True)
        
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
            self.epub_viewer_frame = NativeEpubViewer(self.right_frame)
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
