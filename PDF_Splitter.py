import tkinter as tk
from tkinter import filedialog, simpledialog
from PIL import Image, ImageTk
import fitz  # PyMuPDF
import os

class PDFSplitterApp:
    def __init__(self, master):
        self.master = master
        self.master.title("PDF Splitter")

        self.file_path = None
        self.current_page = 0

        self.file_path_label = tk.Label(master, text="Select PDF file:")
        self.file_path_label.pack(pady=10)

        self.select_button = tk.Button(master, text="Select File", command=self.select_file)
        self.select_button.pack()

        self.preview_canvas = tk.Canvas(master, width=400, height=600)
        self.preview_canvas.pack()

        self.page_label = tk.Label(master, text="Page: 1")
        self.page_label.pack()

        self.previous_button = tk.Button(master, text="Previous", command=self.show_previous_page, state=tk.DISABLED)
        self.previous_button.pack(side=tk.LEFT, padx=10)

        self.next_button = tk.Button(master, text="Next", command=self.show_next_page, state=tk.DISABLED)
        self.next_button.pack(side=tk.RIGHT, padx=10)

        self.split_button = tk.Button(master, text="Split PDF", command=self.split_pdf, state=tk.DISABLED)
        self.split_button.pack(pady=10)

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            self.file_path = file_path
            self.file_path_label.config(text=f"Selected file: {file_path}")
            self.current_page = 0
            self.update_navigation_buttons()
            self.display_pdf_preview()
            self.split_button.config(state=tk.NORMAL)

    def display_pdf_preview(self):
        if self.file_path:
            pdf_document = fitz.open(self.file_path)

            if 0 <= self.current_page < pdf_document.page_count:
                page = pdf_document[self.current_page]
                image = page.get_pixmap()
                img = Image.frombytes("RGB", (image.width, image.height), image.samples)
                img = ImageTk.PhotoImage(img)

                self.preview_canvas.config(width=image.width, height=image.height)
                self.preview_canvas.create_image(0, 0, anchor=tk.NW, image=img)
                self.preview_canvas.image = img

                # Update the page label
                self.page_label.config(text=f"Page: {self.current_page + 1}")

            pdf_document.close()
        else:
            # Clear the preview canvas if file_path is None
            self.preview_canvas.config(width=0, height=0)
            self.preview_canvas.delete("all")

    def show_previous_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_navigation_buttons()
            self.display_pdf_preview()

    def show_next_page(self):
        pdf_document = fitz.open(self.file_path)
        if 0 <= self.current_page < pdf_document.page_count - 1:
            self.current_page += 1
            self.update_navigation_buttons()
            self.display_pdf_preview()
        pdf_document.close()

    def update_navigation_buttons(self):
        self.previous_button.config(state=tk.NORMAL if self.current_page > 0 else tk.DISABLED)
        self.next_button.config(state=tk.NORMAL if self.current_page < self.get_max_page() else tk.DISABLED)

    def get_max_page(self):
        if self.file_path:
            pdf_document = fitz.open(self.file_path)
            max_page = pdf_document.page_count - 1
            pdf_document.close()
            return max_page
        return 0

    def split_pdf(self):
        if not self.file_path:
            tk.messagebox.showerror("Error", "Please select a PDF file.")
            return

        page_range = self.ask_for_page_range()
        if not page_range:
            return  # User canceled the page range selection

        output_directory = filedialog.askdirectory(title="Select Output Directory")
        if not output_directory:
            return  # User canceled the directory selection

        start_page, end_page = page_range
        if start_page > end_page or not (0 <= start_page < self.get_max_page()) or not (0 <= end_page < self.get_max_page()):
            tk.messagebox.showerror("Error", "Invalid page range.")
            return

        pdf_document = fitz.open(self.file_path)
        base_name = os.path.splitext(os.path.basename(self.file_path))[0]

        pdf_writer = fitz.open()
        for page_num in range(start_page, end_page + 1):
            pdf_writer.insert_pdf(pdf_document, from_page=page_num, to_page=page_num)

        output_file_path = f"{output_directory}/{base_name}_pages_{start_page + 1}_{end_page + 1}.pdf"
        pdf_writer.save(output_file_path)
        pdf_writer.close()

        pdf_document.close()

        tk.messagebox.showinfo("Success", "PDF successfully split into specified pages!")

        # Update the preview after splitting
        self.current_page = start_page
        self.display_pdf_preview()

    def ask_for_page_range(self):
        result = simpledialog.askstring("Page Range", "Enter the page range (e.g., 1-3):")
        if result:
            try:
                start, end = map(int, result.split('-'))
                return start - 1, end - 1  # Convert to 0-based indexing
            except ValueError:
                tk.messagebox.showerror("Error", "Invalid input. Please enter a valid page range.")
        return None

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFSplitterApp(root)
    root.mainloop()
