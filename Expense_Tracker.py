import datetime
import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

import matplotlib.pyplot as plt


# Database Setup
def init_db():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS expenses (
                      id INTEGER PRIMARY KEY, 
                      amount REAL, 
                      category TEXT, 
                      description TEXT, 
                      date TEXT)''')
    conn.commit()
    conn.close()

def clear_db():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses")
    conn.commit()
    conn.close()

def add_expense(amount, category, description, date):
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO expenses (amount, category, description, date) VALUES (?, ?, ?, ?)",
                   (amount, category, description, date))
    conn.commit()
    conn.close()
    update_expense_list()

def delete_expense():
    selected_item = tree.selection()
    if selected_item:
        expense_id = tree.item(selected_item)['values'][0]
        conn = sqlite3.connect("expenses.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        conn.commit()
        conn.close()
        tree.delete(selected_item)
    else:
        messagebox.showwarning("Warning", "Please select an expense to delete.")

def get_expenses():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_monthly_summary():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("SELECT category, SUM(amount) FROM expenses WHERE strftime('%Y-%m', date) = strftime('%Y-%m', 'now') GROUP BY category")
    rows = cursor.fetchall()
    conn.close()
    return rows

def show_summary():
    summary = get_monthly_summary()
    summary_text = "Monthly Summary:\n"
    for category, total in summary:
        summary_text += f"{category}: ${total:.2f}\n"
    messagebox.showinfo("Spending Summary", summary_text)

def show_insights():
    summary = get_monthly_summary()
    if summary:
        categories, amounts = zip(*summary)
        plt.figure(figsize=(6, 4))
        plt.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=140)
        plt.title("Spending Insights")
        plt.show()
    else:
        messagebox.showinfo("Info", "No expense data available for insights.")

# GUI Setup
def add_expense_gui():
    try:
        amount_text = amount_entry.get().strip()
        if not amount_text or not amount_text.replace('.', '', 1).isdigit():
            raise ValueError("Invalid amount")
        amount = float(amount_text)
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        category = category_var.get()
        description = description_entry.get().strip()
        date = date_entry.get().strip()
        if not date:
            date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        add_expense(amount, category, description, date)
        messagebox.showinfo("Success", "Expense Added Successfully!")
        update_expense_list()
    except ValueError as e:
        messagebox.showerror("Error", str(e))

def update_expense_list():
    for row in tree.get_children():
        tree.delete(row)
    for expense in get_expenses():
        tree.insert("", "end", values=expense)

# Main Window
root = tk.Tk()
root.title("Expense Tracker")
root.geometry("700x550")
root.resizable(False, False)

init_db()

frame = tk.Frame(root, padx=10, pady=10)
frame.pack(fill="x")

# Input Fields
tk.Label(frame, text="Amount:").grid(row=0, column=0, sticky="w", pady=2)
amount_entry = tk.Entry(frame)
amount_entry.grid(row=0, column=1, padx=5, pady=2)

tk.Label(frame, text="Category:").grid(row=1, column=0, sticky="w", pady=2)
category_var = tk.StringVar()
category_dropdown = ttk.Combobox(frame, textvariable=category_var, values=["Food", "Transport", "Shopping", "Entertainment", "Other"], state="readonly")
category_dropdown.grid(row=1, column=1, padx=5, pady=2)
category_dropdown.current(0)

tk.Label(frame, text="Description:").grid(row=2, column=0, sticky="w", pady=2)
description_entry = tk.Entry(frame)
description_entry.grid(row=2, column=1, padx=5, pady=2)

tk.Label(frame, text="Date (YYYY-MM-DD):").grid(row=3, column=0, sticky="w", pady=2)
date_entry = tk.Entry(frame)
date_entry.grid(row=3, column=1, padx=5, pady=2)

action_frame = tk.Frame(root)
action_frame.pack(fill="x", pady=5)

add_button = tk.Button(action_frame, text="Add Expense", command=add_expense_gui, bg="black", fg="white")
add_button.pack(side="left", padx=5)

delete_button = tk.Button(action_frame, text="Delete Expense", command=delete_expense, bg="black", fg="white")
delete_button.pack(side="left", padx=5)

summary_button = tk.Button(action_frame, text="Show Monthly Summary", command=show_summary, bg="black", fg="white")
summary_button.pack(side="right", padx=5)

insights_button = tk.Button(action_frame, text="Show Insights", command=show_insights, bg="black", fg="white")
insights_button.pack(side="right", padx=5)

# Expense List
tree_frame = tk.Frame(root)
tree_frame.pack(fill="both", expand=True, padx=10, pady=5)

tree = ttk.Treeview(tree_frame, columns=("ID", "Amount", "Category", "Description", "Date"), show="headings")

for col in ("ID", "Amount", "Category", "Description", "Date"):
    tree.heading(col, text=col)
    tree.column(col, anchor="center", width=120)

tree.pack(fill="both", expand=True)

update_expense_list()

root.protocol("WM_DELETE_WINDOW", lambda: [clear_db(), root.destroy()])

root.mainloop()
