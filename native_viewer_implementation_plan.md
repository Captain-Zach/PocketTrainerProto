# Native EPUB Viewer: Implementation Plan

This document details the plan to replace the `tkhtmlview`-based EPUB viewer with a custom solution built on Tkinter's native `Text` widget and the `BeautifulSoup` library. This approach will provide the stability and control required for our application.

---

## Phase 1: Foundational Setup

This phase focuses on creating the basic structure of the new viewer.

1.  **Create a New Viewer Class:**
    *   In a new file, `native_viewer.py`, create a class `NativeEpubViewer` that inherits from `tk.Frame`.
    *   This class will encapsulate all the logic for the new viewer.
    *   The `__init__` method will create a `tk.Text` widget and a `tk.Scrollbar`.

2.  **Integrate into `main.py`:**
    *   In `main.py`, replace the creation of the `epub_viewer_frame` and its contents with an instance of our new `NativeEpubViewer`.
    *   The `open_epub` method will now pass the book content to a method in our new viewer class.

---

## Phase 2: HTML Parsing and Rendering

This is the core of the implementation. We will parse the HTML of a chapter and render it in the `Text` widget.

1.  **Configure `Text` Widget Tags:**
    *   In the `NativeEpubViewer`'s `__init__`, we will define Tkinter `Text` tags to correspond to the most common HTML tags we found.
    *   We will start with the highest-frequency tags:
        *   `p`: Standard paragraph formatting.
        *   `a`: Blue, underlined text.
        *   `i`: Italic font style.
        *   `h1`, `h2`: Larger, bold fonts.
        *   `blockquote`: Indentation and italic style.
        *   `b`: Bold font style.
        *   `li`: A bullet point (`\u2022`) and indentation.

2.  **Create the `render_chapter` Method:**
    *   This method will take the HTML content of a chapter as input.
    *   It will first clear any existing content from the `Text` widget.
    *   It will use `BeautifulSoup` to parse the HTML: `soup = BeautifulSoup(html_content, 'html.parser')`.
    *   It will then recursively traverse the `soup` object. For each HTML tag, it will insert the text into the `Text` widget and apply the corresponding pre-configured Tkinter tag.

3.  **Implement Recursive Traversal:**
    *   Create a helper function, `_parse_node(node)`, that takes a `BeautifulSoup` node as input.
    *   If the node is a simple string, insert it into the `Text` widget.
    *   If the node is a tag (e.g., `<p>`, `<i>`), get the name of the tag.
        *   Insert the tag's content by recursively calling `_parse_node` on its children.
        *   Apply the corresponding Tkinter tag to the range of text just inserted.
    *   This recursive approach can handle nested formatting (e.g., a bold link inside an italic paragraph).

---

## Phase 3: Hyperlink and Selection Handling

This phase makes the viewer interactive.

1.  **Hyperlink Binding:**
    *   When rendering an `<a>` tag, in addition to applying the "hyperlink" style, we will also apply a unique tag that contains the `href` URL, e.g., `hyperlink_href_chapter2.xhtml`.
    *   We will then use `self.text_widget.tag_bind` to make this unique tag respond to clicks.
    *   The bound function will extract the URL from the tag name and call the main app's navigation logic.

2.  **Programmatic Highlighting Method:**
    *   Create a public method, `highlight_text(start, end, tag_name)`.
    *   This method will allow the main application (and eventually the LLM) to apply a custom tag (e.g., "llm_highlight") to a specific range of text in the `Text` widget.
    *   The `start` and `end` parameters will use the `Text` widget's index format (e.g., "1.0").

---

## Summary of Benefits

By completing these phases, we will have a highly robust and controllable EPUB viewer. It will be immune to the issues we faced with `tkhtmlview`, and it will provide the essential foundation for the advanced LLM-based features planned for the future.
