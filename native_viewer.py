import tkinter as tk
from tkinter import scrolledtext
from bs4 import BeautifulSoup

class NativeEpubViewer(tk.Frame):
    """
    A custom widget to display EPUB content using a native Tkinter Text widget.
    It parses a subset of HTML and applies formatting.
    """
    def __init__(self, master, selection_callback=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self._selection_callback = selection_callback

        self.text = scrolledtext.ScrolledText(self, wrap=tk.WORD, padx=10, pady=10, borderwidth=0, highlightthickness=0)
        self.text.pack(fill=tk.BOTH, expand=True)
        
        # Make the widget read-only by intercepting key presses, but allow selection
        self.text.bind("<Key>", lambda e: "break")
        self.text.bind("<ButtonRelease-1>", self._on_selection_end)

        self._configure_tags()
        self._link_callback = None

    def _on_selection_end(self, event):
        """
        Called when the user releases the mouse button. If text is selected,
        it triggers the selection callback.
        """
        selected_text = self.get_selected_text()
        if selected_text and self._selection_callback:
            self._selection_callback(selected_text)

    def _configure_tags(self):
        """Defines the text styles for various HTML tags."""
        self.text.tag_configure("p", spacing3=10)
        self.text.tag_configure("h1", font=("Arial", 20, "bold"), spacing3=15)
        self.text.tag_configure("h2", font=("Arial", 16, "bold"), spacing3=12)
        self.text.tag_configure("h3", font=("Arial", 14, "bold"), spacing3=10)
        self.text.tag_configure("i", font=("Arial", 12, "italic"))
        self.text.tag_configure("b", font=("Arial", 12, "bold"))
        self.text.tag_configure("blockquote", lmargin1=20, lmargin2=20, spacing3=10)
        self.text.tag_configure("li", lmargin1=20, lmargin2=20)
        
        # Hyperlink style and binding
        self.text.tag_configure("a", foreground="blue", underline=True)
        self.text.tag_bind("a", "<Button-1>", self._on_link_click)
        self.text.tag_bind("a", "<Enter>", self._on_enter_link)
        self.text.tag_bind("a", "<Leave>", self._on_leave_link)

    def _on_enter_link(self, event):
        self.text.config(cursor="hand2")

    def _on_leave_link(self, event):
        self.text.config(cursor="")

    def _on_link_click(self, event):
        # Get the index of the character under the mouse pointer
        index = self.text.index(f"@{event.x},{event.y}")
        
        # Find all tags at the clicked position
        tags = self.text.tag_names(index)
        
        # Find the href tag
        for tag in tags:
            if tag.startswith("href_"):
                url = tag[5:] # Get the URL part after "href_"
                if self._link_callback:
                    self._link_callback(url)
                break

    def render_chapter(self, html_content, link_callback):
        """
        Clears the widget and renders new HTML content.
        """
        self._link_callback = link_callback
        self.text.config(state=tk.NORMAL)
        self.text.delete("1.0", tk.END)

        soup = BeautifulSoup(html_content, 'html.parser')
        self._parse_node(soup.body)

    def get_selected_text(self):
        """
        Returns the currently selected text in the widget.
        """
        try:
            return self.text.get(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            # This error occurs if no text is selected
            return ""

    def _parse_node(self, node):
        """
        Recursively parses a BeautifulSoup node and inserts its content
        into the Text widget with the appropriate tags.
        """
        if node is None:
            return

        # Mapping of HTML tags to Tkinter tags
        tag_map = {
            'p': 'p', 'i': 'i', 'em': 'i', 'b': 'b', 'strong': 'b',
            'h1': 'h1', 'h2': 'h2', 'h3': 'h3', 'blockquote': 'blockquote',
            'a': 'a', 'ul': 'p', 'ol': 'p', 'div': 'p'
        }

        if isinstance(node, str):
            self.text.insert(tk.END, node)
        else:
            # Handle list items specifically
            if node.name == 'li':
                start = self.text.index(tk.END)
                self.text.insert(tk.END, f"\u2022 {node.get_text().strip()}\n")
                self.text.tag_add('li', start, self.text.index(tk.END))
                return # Stop further parsing for this node

            start_index = self.text.index(tk.END)
            
            # Apply a newline after block-level elements for spacing
            is_block = node.name in ['p', 'h1', 'h2', 'h3', 'blockquote', 'div']

            # Recursively parse child nodes
            for child in node.children:
                self._parse_node(child)

            end_index = self.text.index(tk.END)

            # Apply the corresponding tag to the inserted content
            tk_tag = tag_map.get(node.name)
            if tk_tag:
                self.text.tag_add(tk_tag, start_index, end_index)
            
            # For hyperlinks, add a specific tag with the href
            if node.name == 'a' and node.has_attr('href'):
                href_tag = f"href_{node['href']}"
                self.text.tag_add(href_tag, start_index, end_index)

            if is_block:
                self.text.insert(tk.END, "\n")