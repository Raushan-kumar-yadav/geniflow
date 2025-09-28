import tkinter as tk
from tkinter import filedialog, messagebox
import json

class FacebookPageManager:
    def __init__(self, root):  # Corrected from _init_ to __init__
        self.root = root
        self.root.title("Facebook Page Manager")

        # Facebook ID Entry
        self.fb_id_label = tk.Label(root, text="Facebook ID:")
        self.fb_id_label.pack(pady=5)
        self.fb_id_entry = tk.Entry(root, width=50)
        self.fb_id_entry.pack(pady=5)

        # Page Listbox
        self.page_listbox = tk.Listbox(root, width=50, height=10)
        self.page_listbox.pack(pady=5)

        # Entry for new page
        self.new_page_entry = tk.Entry(root, width=50)
        self.new_page_entry.pack(pady=5)

        # Buttons
        self.add_page_button = tk.Button(root, text="Add Page", command=self.add_page)
        self.add_page_button.pack(pady=5)

        self.save_button = tk.Button(root, text="Save", command=self.save_data)
        self.save_button.pack(pady=5)

        self.load_button = tk.Button(root, text="Load", command=self.load_data)
        self.load_button.pack(pady=5)

    def add_page(self):
        page = self.new_page_entry.get()
        if page:
            self.page_listbox.insert(tk.END, page)
            self.new_page_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Input Error", "Please enter a page name.")

    def save_data(self):
        fb_id = self.fb_id_entry.get()
        pages = self.page_listbox.get(0, tk.END)
        if not fb_id or not pages:
            messagebox.showwarning("Input Error", "Facebook ID and pages cannot be empty.")
            return

        data = {
            'facebook_id': fb_id,
            'pages': list(pages)
        }

        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            with open(file_path, 'w') as file:
                json.dump(data, file)
            messagebox.showinfo("Success", "Data saved successfully.")

    def load_data(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            with open(file_path, 'r') as file:
                data = json.load(file)
            self.fb_id_entry.delete(0, tk.END)
            self.fb_id_entry.insert(0, data.get('facebook_id', ''))
            self.page_listbox.delete(0, tk.END)
            for page in data.get('pages', []):
                self.page_listbox.insert(tk.END, page)
            messagebox.showinfo("Success", "Data loaded successfully.")

if __name__ == "__main__":
    root = tk.Tk()
    app = FacebookPageManager(root)
    root.mainloop()