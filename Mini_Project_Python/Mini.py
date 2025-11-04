import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

class StudentResultAnalyzer:
    """
    Student Result Analyzer with colorful UI and delete feature.
    """

    def __init__(self, root):
        self.root = root
        self.root.title("Student Result Analyzer")
        self.root.geometry("1200x750")
        self.root.config(bg="#eef2f3")  # soft light gray background

        self.subjects = ['Physics', 'Chemistry', 'Maths', 'English', 'Computer']
        self.csv_file = 'students.csv'
        self.df = None
        self.load_data()
        self.create_widgets()
        self.view_records()

    # -----------------------------------------------------------------
    def create_widgets(self):
        """Creates and arranges all GUI widgets."""
        # --- Main Frames ---
        left_frame = tk.Frame(self.root, width=400, bd=2, relief=tk.RIDGE, bg="#ffffff")
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        left_frame.pack_propagate(False)

        right_frame = tk.Frame(self.root, bg="#eef2f3")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        title_label = tk.Label(left_frame, text="🎓 Student Result Analyzer", font=("Arial", 16, "bold"),
                               bg="#4285f4", fg="white", pady=10)
        title_label.pack(fill=tk.X)

        # --- Input Section ---
        input_frame = ttk.LabelFrame(left_frame, text="Add New Record", padding=15)
        input_frame.pack(fill=tk.X, pady=10, padx=10)
        self.entries = {}

        ttk.Label(input_frame, text="Roll No:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.entries['Roll No'] = ttk.Entry(input_frame, width=30)
        self.entries['Roll No'].grid(row=0, column=1, pady=5)

        ttk.Label(input_frame, text="Name:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.entries['Name'] = ttk.Entry(input_frame, width=30)
        self.entries['Name'].grid(row=1, column=1, pady=5)

        for i, subject in enumerate(self.subjects):
            ttk.Label(input_frame, text=f"{subject} Marks:").grid(row=i + 2, column=0, sticky=tk.W, pady=5)
            self.entries[subject] = ttk.Entry(input_frame, width=30)
            self.entries[subject].grid(row=i + 2, column=1, pady=5)

        # --- Control Buttons (Colorful) ---
        control_frame = tk.Frame(left_frame, bg="#ffffff")
        control_frame.pack(fill=tk.X, pady=10, padx=10, side=tk.BOTTOM)

        button_style = {"font": ("Arial", 11, "bold"), "bd": 0, "relief": "flat", "width": 20, "pady": 6}

        tk.Button(control_frame, text="➕ Add Record", bg="#34a853", fg="white",
                  activebackground="#2c8c47", command=self.add_record, **button_style).pack(pady=5)

        tk.Button(control_frame, text="💾 Save Data", bg="#fbbc04", fg="black",
                  activebackground="#e0a800", command=self.save_data, **button_style).pack(pady=5)

        tk.Button(control_frame, text="🗑 Delete Record", bg="#ea4335", fg="white",
                  activebackground="#c5221f", command=self.delete_record, **button_style).pack(pady=5)

        tk.Button(control_frame, text="❌ Exit", bg="#5f6368", fg="white",
                  activebackground="#3c4043", command=self.root.quit, **button_style).pack(pady=5)

        # --- Right Frame: Tabs ---
        display_notebook = ttk.Notebook(right_frame)
        display_notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Records Table
        table_frame = ttk.Frame(display_notebook, padding=10)
        display_notebook.add(table_frame, text='Student Records')

        ttk.Button(table_frame, text="🔄 Refresh/View Records", command=self.view_records).pack(pady=10)

        scroll_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        columns = ['Roll No', 'Name'] + self.subjects + ['Total', 'Average', 'Grade']

        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings',
                                 yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        for col in columns:
            self.tree.heading(col, text=col, command=lambda _col=col: self.sort_treeview(_col, False))
            self.tree.column(col, anchor=tk.CENTER, width=120)

        self.tree.pack(fill=tk.BOTH, expand=True)

        # Tab 2: Graphs
        plot_frame = ttk.Frame(display_notebook, padding=10)
        display_notebook.add(plot_frame, text='Data Visualization')

        plot_control_frame = ttk.Frame(plot_frame)
        plot_control_frame.pack(fill=tk.X, pady=10)

        ttk.Button(plot_control_frame, text="📊 Subject Marks Graph", command=self.show_subject_graph).pack(side=tk.LEFT, padx=10)
        ttk.Button(plot_control_frame, text="🧩 Grade Distribution", command=self.show_grade_distribution).pack(side=tk.LEFT, padx=10)

        self.plot_canvas_frame = ttk.Frame(plot_frame)
        self.plot_canvas_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        self.current_canvas = None

    # -----------------------------------------------------------------
    def load_data(self):
        columns = ['Roll No', 'Name'] + self.subjects + ['Total', 'Average', 'Grade']
        if os.path.exists(self.csv_file):
            try:
                self.df = pd.read_csv(self.csv_file)
            except Exception:
                self.df = pd.DataFrame(columns=columns)
        else:
            self.df = pd.DataFrame(columns=columns)

    def save_data(self):
        if self.df is None or self.df.empty:
            messagebox.showwarning("No Data", "There is no data to save.")
            return
        self.df.to_csv(self.csv_file, index=False)
        messagebox.showinfo("Success", "Data saved successfully!")

    def add_record(self):
        record = {}
        try:
            roll_no = self.entries['Roll No'].get().strip()
            name = self.entries['Name'].get().strip()
            if not roll_no or not name:
                raise ValueError("Roll No and Name cannot be empty.")
            if not self.df.empty and roll_no in self.df['Roll No'].astype(str).values:
                raise ValueError("Roll No already exists.")

            marks = [float(self.entries[sub].get()) for sub in self.subjects]
            total = sum(marks)
            avg = total / len(marks)
            grade = self.calculate_grade(avg, marks)

            record = {'Roll No': roll_no, 'Name': name, **dict(zip(self.subjects, marks)),
                      'Total': total, 'Average': round(avg, 2), 'Grade': grade}

            self.df = pd.concat([self.df, pd.DataFrame([record])], ignore_index=True)
            messagebox.showinfo("Success", "Record added successfully.")
            self.clear_entries()
            self.view_records()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a record to delete.")
            return

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this record?")
        if confirm:
            roll_no = self.tree.item(selected[0])['values'][0]
            self.df = self.df[self.df['Roll No'].astype(str) != str(roll_no)]
            self.view_records()
            messagebox.showinfo("Deleted", f"Record with Roll No {roll_no} deleted.")

    def calculate_grade(self, avg, marks_list=None):
        if marks_list and any(m < 33 for m in marks_list):
            return 'Fail'
        if avg >= 90:
            return 'A'
        elif avg >= 75:
            return 'B'
        elif avg >= 50:
            return 'C'
        else:
            return 'Fail'

    def clear_entries(self):
        for e in self.entries.values():
            e.delete(0, tk.END)

    def view_records(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        if self.df is not None and not self.df.empty:
            for _, row in self.df.iterrows():
                self.tree.insert("", tk.END, values=list(row))

    def sort_treeview(self, col, reverse):
        data = [(self.tree.set(item, col), item) for item in self.tree.get_children('')]
        try:
            data.sort(key=lambda t: float(t[0]) if t[0].replace('.', '', 1).isdigit() else t[0], reverse=reverse)
        except:
            data.sort(reverse=reverse)
        for index, (_, item) in enumerate(data):
            self.tree.move(item, '', index)
        self.tree.heading(col, command=lambda: self.sort_treeview(col, not reverse))

    def clear_plot_canvas(self):
        if self.current_canvas:
            self.current_canvas.get_tk_widget().destroy()
            self.current_canvas = None

    def show_subject_graph(self):
        self.clear_plot_canvas()
        if self.df.empty:
            messagebox.showwarning("No Data", "No records to plot.")
            return

        roll_no = simpledialog.askstring("Input", "Enter Roll No:")
        if not roll_no:
            return

        student = self.df[self.df['Roll No'].astype(str) == str(roll_no)]
        if student.empty:
            messagebox.showerror("Not Found", "Roll No not found.")
            return

        marks = student[self.subjects].iloc[0].astype(float)
        fig, ax = plt.subplots(figsize=(8, 5))
        bars = ax.bar(self.subjects, marks, color="#4285f4")
        ax.bar_label(bars, fmt="%.0f")
        ax.set_ylim(0, 100)
        ax.set_title(f"Marks for {student['Name'].values[0]}")
        self.current_canvas = FigureCanvasTkAgg(fig, master=self.plot_canvas_frame)
        self.current_canvas.draw()
        self.current_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def show_grade_distribution(self):
        self.clear_plot_canvas()
        if self.df.empty:
            messagebox.showwarning("No Data", "No grades to plot.")
            return
        grades = self.df['Grade'].value_counts()
        fig, ax = plt.subplots(figsize=(6, 5))
        ax.pie(grades, labels=grades.index, autopct='%1.1f%%', startangle=90, colors=plt.cm.Pastel1.colors)
        ax.set_title("Class Grade Distribution")
        self.current_canvas = FigureCanvasTkAgg(fig, master=self.plot_canvas_frame)
        self.current_canvas.draw()
        self.current_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# -----------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style(root)
    try:
        style.theme_use('clam')
    except tk.TclError:
        pass
    app = StudentResultAnalyzer(root)
    root.mainloop()
