import tkinter as tk
from tkinter import ttk, messagebox
import os

FILE = "problems.txt"

class SplashScreen(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.overrideredirect(True)
        self.geometry("450x220+550+320")
        self.configure(bg="#6a0dad")
        self.label = tk.Label(self, text="🔐 Loading PurplePass Manager", 
                              font=("Segoe UI Semibold", 20), fg="white", bg="#6a0dad")
        self.label.pack(expand=True)
        self.dots = 0
        self.animate()

    def animate(self):
        self.dots = (self.dots + 1) % 4
        self.label.config(text="🔐 Loading PurplePass Manager" + "." * self.dots)
        self.after(400, self.animate)

class PlaceholderEntry(ttk.Entry):
    def __init__(self, master=None, placeholder="", **kwargs):
        super().__init__(master, **kwargs)
        self.placeholder = placeholder
        self.default_fg = "#4b0082"
        self.placeholder_fg = "#aaa"
        self.insert("0", self.placeholder)
        self.config(foreground=self.placeholder_fg)
        self.bind("<FocusIn>", self.clear_placeholder)
        self.bind("<FocusOut>", self.add_placeholder)

    def clear_placeholder(self, e=None):
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self.config(foreground=self.default_fg)

    def add_placeholder(self, e=None):
        if not self.get():
            self.insert(0, self.placeholder)
            self.config(foreground=self.placeholder_fg)

class PasswordManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🔐 PurplePass Manager")
        self.geometry("820x530")
        self.configure(bg="white")
        self.resizable(False, False)
        self.setup_style()
        self.setup_ui()
        self.load_entries()

    def setup_style(self):
        style = ttk.Style(self)
        style.theme_use('clam')

        style.configure("TLabel", background="white", foreground="#4b0082", font=("Segoe UI", 11))
        style.configure("TButton", font=("Segoe UI Semibold", 11), background="#4b0082", foreground="white", padding=10)
        style.map("TButton",
                  background=[('active', '#5e00b4')])
        style.configure("Treeview", font=("Segoe UI", 11), rowheight=28, background="white", fieldbackground="white", foreground="#222")
        style.configure("Treeview.Heading", font=("Segoe UI Semibold", 12), foreground="#4b0082")
        style.layout("TButton", [('Button.background', {'children': [('Button.padding', {'children': [('Button.label', {'sticky': 'nswe'})], 'sticky': 'nswe'})], 'sticky': 'nswe'})])

    def setup_ui(self):
        # Header
        header = tk.Label(self, text="PurplePass Manager", 
                          font=("Segoe UI Semibold", 28), bg="white", fg="#4b0082")
        header.pack(pady=(25, 15))

        # Main frame with padding
        main_frame = tk.Frame(self, bg="white")
        main_frame.pack(fill='both', expand=True, padx=25)

        # Input and buttons frame
        input_frame = tk.Frame(main_frame, bg="white")
        input_frame.pack(fill='x')

        # Website
        self.website_entry = PlaceholderEntry(input_frame, placeholder="Website (e.g., example.com)", width=30)
        self.website_entry.grid(row=0, column=0, padx=(0, 15), pady=10, sticky='ew')

        # Username
        self.username_entry = PlaceholderEntry(input_frame, placeholder="Username or Email", width=30)
        self.username_entry.grid(row=0, column=1, padx=(0, 15), pady=10, sticky='ew')

        # Password with toggle
        self.password_var = tk.StringVar()
        self.password_entry = PlaceholderEntry(input_frame, placeholder="Password", width=30, textvariable=self.password_var, show="")
        self.password_entry.grid(row=0, column=2, padx=(0, 0), pady=10, sticky='ew')

        # Show/hide password toggle button
        self.show_password = False
        self.toggle_btn = ttk.Button(input_frame, text="👁️", width=3, command=self.toggle_password)
        self.toggle_btn.grid(row=0, column=3, padx=(5,0), pady=10)

        input_frame.grid_columnconfigure(0, weight=1)
        input_frame.grid_columnconfigure(1, weight=1)
        input_frame.grid_columnconfigure(2, weight=1)

        # Buttons Frame
        btn_frame = tk.Frame(main_frame, bg="white")
        btn_frame.pack(fill='x', pady=(0, 20))

        self.add_btn = ttk.Button(btn_frame, text="➕ Add", command=self.add_password)
        self.add_btn.pack(side='left', padx=10)

        self.update_btn = ttk.Button(btn_frame, text="✏️ Update", command=self.update_entry)
        self.update_btn.pack(side='left', padx=10)

        self.delete_btn = ttk.Button(btn_frame, text="🗑️ Delete", command=self.delete_entry)
        self.delete_btn.pack(side='left', padx=10)

        # Search bar right aligned
        search_frame = tk.Frame(main_frame, bg="white")
        search_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(search_frame, text="Search:").pack(side='left', padx=(0, 8))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *a: self.filter_entries())
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=45)
        self.search_entry.pack(side='left', fill='x', expand=True)

        # Treeview Frame
        tree_frame = tk.Frame(main_frame, bg="white")
        tree_frame.pack(fill='both', expand=True)

        columns = ("website", "username", "password")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', selectmode="browse")
        for col, width in zip(columns, (280, 280, 280)):
            self.tree.heading(col, text=col.title(), anchor="w")
            self.tree.column(col, width=width, anchor="w", stretch=True)
        self.tree.pack(side='left', fill='both', expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

        self.tree.bind("<Double-1>", self.on_tree_double_click)

    def toggle_password(self):
        if self.show_password:
            self.password_entry.config(show="*")
            self.show_password = False
            self.toggle_btn.config(text="👁️")
        else:
            self.password_entry.config(show="")
            self.show_password = True
            self.toggle_btn.config(text="🙈")

    def add_password(self):
        w = self.website_entry.get().strip()
        u = self.username_entry.get().strip()
        p = self.password_entry.get().strip()
        if (w == "" or w == "Website (e.g., example.com)" or
            u == "" or u == "Username or Email" or
            p == "" or p == "Password"):
            messagebox.showwarning("Input Error", "Please fill all fields.", parent=self)
            return
        with open(FILE, "a") as f:
            f.write(f"{w} | {u} | {p}\n")
        messagebox.showinfo("Success", "Password added successfully!", parent=self)
        self.clear_inputs()
        self.load_entries()

    def load_entries(self):
        self.tree.delete(*self.tree.get_children())
        if os.path.exists(FILE):
            with open(FILE, "r") as f:
                for line in f:
                    parts = line.strip().split(" | ")
                    if len(parts) == 3:
                        self.tree.insert("", tk.END, values=parts)
        self.filter_entries()

    def filter_entries(self):
        query = self.search_var.get().lower()
        for item in self.tree.get_children():
            site = self.tree.item(item)["values"][0].lower()
            visible = query in site
            self.tree.item(item, tags=() if visible else ("hidden",))
        self.tree.tag_configure("hidden", foreground="white")

    def on_tree_double_click(self, _):
        sel = self.tree.focus()
        if sel:
            w, u, p = self.tree.item(sel, "values")
            self.website_entry.delete(0, tk.END)
            self.website_entry.insert(0, w)
            self.username_entry.delete(0, tk.END)
            self.username_entry.insert(0, u)
            self.password_entry.delete(0, tk.END)
            self.password_entry.insert(0, p)
            self.password_entry.config(show="*")
            self.show_password = False
            self.toggle_btn.config(text="👁️")

    def clear_inputs(self):
        for entry, placeholder in [(self.website_entry, "Website (e.g., example.com)"),
                                   (self.username_entry, "Username or Email"),
                                   (self.password_entry, "Password")]:
            entry.delete(0, tk.END)
            entry.insert(0, placeholder)
            entry.config(foreground="#aaa")
        self.password_entry.config(show="")
        self.show_password = False
        self.toggle_btn.config(text="👁️")

    def update_entry(self):
        sel = self.tree.focus()
        if not sel:
            messagebox.showwarning("Select", "Please select an entry first.", parent=self)
            return
        w = self.website_entry.get().strip()
        u = self.username_entry.get().strip()
        p = self.password_entry.get().strip()
        if (w == "" or w == "Website (e.g., example.com)" or
            u == "" or u == "Username or Email" or
            p == "" or p == "Password"):
            messagebox.showwarning("Input Error", "Please fill all fields.", parent=self)
            return
        if not messagebox.askyesno("Confirm Update", "Update selected entry?", parent=self):
            return
        with open(FILE, "r") as f:
            lines = f.readlines()
        vals = self.tree.item(sel, "values")
        for i, line in enumerate(lines):
            if line.strip() == " | ".join(vals):
                lines[i] = f"{w} | {u} | {p}\n"
                break
        with open(FILE, "w") as f:
            f.writelines(lines)
        messagebox.showinfo("Updated", "Entry updated successfully!", parent=self)
        self.clear_inputs()
        self.load_entries()

    def delete_entry(self):
        sel = self.tree.focus()
        if not sel:
            messagebox.showwarning("Select", "Please select an entry first.", parent=self)
            return
        if not messagebox.askyesno("Confirm Delete", "Delete selected entry?", parent=self):
            return
        vals = self.tree.item(sel, "values")
        with open(FILE, "r") as f:
            lines = f.readlines()
        lines = [l for l in lines if l.strip() != " | ".join(vals)]
        with open(FILE, "w") as f:
            f.writelines(lines)
        messagebox.showinfo("Deleted", "Entry deleted successfully!", parent=self)
        self.clear_inputs()
        self.load_entries()

def main():
    root = PasswordManager()
    root.withdraw()
    splash = SplashScreen(root)
    root.after(3000, lambda: (splash.destroy(), root.deiconify()))
    root.mainloop()

if __name__ == "__main__":
    main()
