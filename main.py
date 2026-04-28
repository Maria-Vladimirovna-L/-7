import tkinter as tk
from tkinter import ttk, messagebox, END
import json
import datetime

DATA_FILE = "expenses.json"
expenses = []
filtered_expenses = []

# --- Работа с JSON ---
def load_expenses():
    global expenses, filtered_expenses
    try:
        with open(DATA_FILE, "r") as f:
            expenses = json.load(f)
    except FileNotFoundError:
        expenses = []
    filtered_expenses = expenses.copy()
    update_table()
    update_total_label()

def save_expenses():
    with open(DATA_FILE, "w") as f:
        json.dump(expenses, f, indent=2)

# --- Валидация ---
def is_valid_date(date_str):
    try:
        datetime.datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def is_valid_amount(amount_str):
    try:
        amount = float(amount_str)
        return amount > 0
    except ValueError:
        return False

# --- Логика приложения ---
def add_expense():
    amount_str = entry_amount.get().strip()
    category = entry_category.get().strip()
    date = entry_date.get().strip()

    if not amount_str or not category or not date:
        messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
        return

    if not is_valid_amount(amount_str):
        messagebox.showerror("Ошибка", "Сумма должна быть положительным числом!")
        return

    if not is_valid_date(date):
        messagebox.showerror("Ошибка", "Дата должна быть в формате ГГГГ-ММ-ДД!")
        return

    expense = {
        "amount": float(amount_str),
        "category": category,
        "date": date
    }
    expenses.append(expense)
    save_expenses()
    load_expenses() # Обновляем данные и таблицу

    # Очищаем поля формы (оставляем дату для удобства)
    entry_amount.delete(0, END)
    entry_category.delete(0, END)
    entry_category.focus()

def filter_expenses():
    global filtered_expenses
    category_filter = entry_filter_category.get().lower()
    date_filter = entry_filter_date.get().lower()
    
    filtered_expenses = expenses.copy()
    
    if category_filter:
        filtered_expenses = [e for e in filtered_expenses if category_filter in e["category"].lower()]
    
    if date_filter:
        filtered_expenses = [e for e in filtered_expenses if date_filter in e["date"]]
    
    update_table()
    update_total_label()

def reset_filters():
    global filtered_expenses
    entry_filter_category.delete(0, END)
    entry_filter_date.delete(0, END)
    filtered_expenses = expenses.copy()
    update_table()
    update_total_label()

def calculate_total():
    total = sum(expense["amount"] for expense in filtered_expenses)
    messagebox.showinfo("Итоговая сумма", f"Общие расходы за период: {total:.2f} ₽")

def update_table():
    for i in treeview.get_children():
        treeview.delete(i)
    for expense in filtered_expenses:
        treeview.insert("", END, values=(expense["date"], expense["category"], f"{expense['amount']:.2f}"))

def update_total_label():
    total = sum(expense["amount"] for expense in filtered_expenses)
    label_total.config(text=f"Итоговая сумма (отфильтровано): {total:.2f} ₽")


# --- GUI ---
root = tk.Tk()
root.title("Expense Tracker")
root.geometry("900x600")
root.resizable(False, False)
root.configure(bg="#f0f0f5")

# --- Форма добавления ---
frame_form = tk.Frame(root, bg="#f0f0f5")
frame_form.pack(pady=10, padx=15, fill=tk.X)

tk.Label(frame_form, text="Сумма:", bg="#f0f0f5").grid(row=0, column=0, sticky="e", padx=5)
entry_amount = tk.Entry(frame_form, width=15)
entry_amount.grid(row=0, column=1, sticky="w", padx=5)

tk.Label(frame_form, text="Категория:", bg="#f0f0f5").grid(row=1, column=0, sticky="e", padx=5)
entry_category = tk.Entry(frame_form, width=35)
entry_category.grid(row=1, column=1, columnspan=2, sticky="w", padx=5)

tk.Label(frame_form, text="Дата (ГГГГ-ММ-ДД):", bg="#f0f0f5").grid(row=2, column=0, sticky="e", padx=5)
entry_date = tk.Entry(frame_form, width=15)
entry_date.grid(row=2, column=1, sticky="w", padx=5)
# Предзаполнение текущей датой для удобства пользователя
entry_date.insert(0, datetime.date.today().isoformat())

btn_add = tk.Button(frame_form, text="Добавить расход", command=add_expense)
btn_add.grid(row=2, column=2, pady=10)


# --- Фильтры ---
frame_filters = tk.Frame(root, bg="#f0f0f5")
frame_filters.pack(pady=10, padx=15, fill=tk.X)

tk.Label(frame_filters, text="Фильтр по категории:", bg="#f0f0f5").grid(row=0, column=0, sticky="e", padx=(5,2))
entry_filter_category = tk.Entry(frame_filters, width=25)
entry_filter_category.grid(row=0, column=1, sticky="w", padx=(2,15))

tk.Label(frame_filters, text="Фильтр по дате:", bg="#f0f0f5").grid(row=0, column=2, sticky="e", padx=(15,2))
entry_filter_date = tk.Entry(frame_filters, width=15)
entry_filter_date.grid(row=0, column=3, sticky="w", padx=(2,5))

btn_filter = tk.Button(frame_filters, text="Фильтровать", command=filter_expenses)
btn_filter.grid(row=1, columnspan=4, pady=5)
btn_reset = tk.Button(frame_filters, text="Сбросить фильтр", command=reset_filters)
btn_reset.grid(row=2, columnspan=4)


# --- Таблица и Итог ---
frame_bottom = tk.Frame(root)
frame_bottom.pack(pady=15, padx=15, fill='both', expand=True)

columns = ("Дата", "Категория", "Сумма")
treeview = ttk.Treeview(frame_bottom, columns=columns, show='headings')
for col in columns:
    treeview.heading(col, text=col)
treeview.column("Дата", width=180)
treeview.column("Категория", width=250)
treeview.column("Сумма", width=120)
treeview.pack(fill='both', expand=True)


# --- Кнопки итога и расчёта ---
frame_buttons = tk.Frame(root)
frame_buttons.pack(pady=5)
label_total = tk.Label(frame_buttons, text="Итоговая сумма: 0.00 ₽", font=('Arial', 12))
label_total.pack(side=tk.LEFT)
btn_calculate = tk.Button(frame_buttons, text="Подсчитать сумму", command=calculate_total)
btn_calculate.pack(side=tk.RIGHT)


# Запуск загрузки данных при старте приложения и запуск главного цикла
load_expenses()
root.mainloop()
