# import modules
from tkinter import *
from tkinter import ttk
import datetime as dt
from Expense_db import *
from tkinter import messagebox

# ---------- UI STYLES ----------
FONT_LABEL = ('Segoe UI', 12)
FONT_ENTRY = ('Segoe UI', 11)
FONT_BUTTON = ('Segoe UI', 11, 'bold')

PRIMARY = "#4B5CC4"
SECONDARY = "#6C7AE0"
SUCCESS = "#3A8F7A"
DANGER = "#C94C4C"
WHITE = "white"

#object for database
data = Database(db='myexpense.db')

#global variables
count = 0
selected_rowid = 0

def saveRecord():
    global data
    data.insertRecord(item_name=item_name.get(),item_price=item_amt.get(),purchase_date=transaction_date.get())

    refreshData()    
    clearEntries()

def setDate():
    date = dt.datetime.now()
    dopvar.set(f'{date:%Y-%m-%d}')
    

def clearEntries():
    item_name.delete(0, 'end')
    item_amt.delete(0,'end')
    transaction_date.delete(0, 'end')

def fetch_records():
    f = data.fetchRecord('select rowid, * from expense_record')
    global count
    for rec in f:
        tv.insert(parent='',index='0',iid=count,values=(rec[0], rec[1], rec[2], rec[3]))
        count += 1

def select_record(event):
    global selected_rowid
    selected = tv.focus()
    val = tv.item(selected, 'values')

    try:
        selected_rowid = val[0]
        d = val[3]
        namevar.set(val[1])
        amtvar.set(val[2])
        dopvar.set(str(d))
    except Exception as ep:
        pass

def update_record():
    global selected_rowid
    selected = tv.focus()
    #Update record
    try:
        data.updateRecord(namevar.get() , amtvar.get() , dopvar.get(), selected_rowid)
        tv.item(
            selected,
            values=(selected_rowid, namevar.get(), amtvar.get(), dopvar.get())
        )

    except Exception as ep:
        messagebox.showerror('Error', ep)

    #Clear entry boxes
    item_name.delete(0, END)
    item_amt.delete(0,END)
    transaction_date.delete(0, END)
    tv.after(400, refreshData)

def totalBalance():
    # get total expense
    f = data.fetchRecord("SELECT SUM(item_price) FROM expense_record")
    total_expense = f[0][0] if f[0][0] else 0

    # get budget from database
    budget = data.getBudget()

    if budget == 0:
        messagebox.showwarning("Warning", "Please set your budget first")
        return

    remaining = budget - total_expense

    messagebox.showinfo(
        'Current Balance',
        f"Total Budget: {budget}\n"
        f"Total Expense: {total_expense}\n"
        f"Balance Remaining: {remaining}"
    )


def refreshData():
    for item in tv.get_children():
        tv.delete(item)
    fetch_records()

def setBudget():
    budget = budget_var.get()
    if budget <= 0:
        messagebox.showerror("Error", "Enter valid budget")
        return
    data.setBudget(budget)
    messagebox.showinfo("Success", f"Budget set to {budget}")


def deleteRow():
    global selected_rowid
    data.removeRecord(selected_rowid)
    refreshData()

def openReportWindow():
    report_ws = Toplevel(ws)
    report_ws.title("Date Wise Report")
    report_ws.geometry("700x500")
    report_ws.resizable(False, False)

    Label(report_ws, text="From Date (YYYY-MM-DD)").pack(pady=5)
    from_date = Entry(report_ws, width=30)
    from_date.pack()

    Label(report_ws, text="To Date (YYYY-MM-DD)").pack(pady=5)
    to_date = Entry(report_ws, width=30)
    to_date.pack()

    report_tv = ttk.Treeview(
        report_ws,
        columns=(1,2,3),
        show='headings',
        height=8
    )
    report_tv.pack(pady=10)

    report_tv.heading(1, text="Item Name")
    report_tv.heading(2, text="Item Price")
    report_tv.heading(3, text="Purchase Date")

    total_label = Label(report_ws, text="Total Expense: 0", font=('Arial',12,'bold'))
    total_label.pack()

    Button(
        report_ws,
        text="Generate",
        bg="#4BA0E5",
        fg="white",
        command=lambda: generateReport(
            from_date.get(),
            to_date.get(),
            report_tv,
            total_label
        )
    ).pack(pady=5)

def generateReport(from_date, to_date, report_tv, total_label):

    if from_date == "" or to_date == "":
        messagebox.showerror("Error", "Please enter both dates")
        return

    for item in report_tv.get_children():
        report_tv.delete(item)

    query = """
    SELECT item_name, item_price, purchase_date
    FROM expense_record
    WHERE purchase_date BETWEEN ? AND ?
    """

    records = data.fetchRecord(query, (from_date, to_date))

    total = 0
    for row in records:
        report_tv.insert('', END, values=row)
        total += row[1]

    total_label.config(text=f"Total Expense: {total}")


ws = Tk()
ws.title('Daily Expenses')

f = ('Times New Roman' , 14)
namevar = StringVar()
amtvar = DoubleVar()
dopvar = StringVar()
budget_var = DoubleVar()


# Frame Widget
f2 = Frame(ws)
f2.pack()

f1 = Frame(
    ws,
    padx=10,
    pady=10
)
f1.pack(expand=True, fill=BOTH)
f1.grid_columnconfigure(1, weight=1)
f1.grid_columnconfigure(2, weight=1)
f1.grid_columnconfigure(3, weight=1)

#Label widget
Label(f1, text='SET BUDGET', font=FONT_LABEL).grid(row=0, column=0, sticky=W)
Label(f1,text='ITEM NAME',font=FONT_LABEL).grid(row=1, column=0, sticky=W)
Label(f1,text='ITEM PRICE',font=FONT_LABEL).grid(row=2, column=0, sticky=W)
Label(f1,text='Purchase Date',font=FONT_LABEL).grid(row=3, column=0, sticky=W)


#Entry widget
budget_entry = Entry(f1, font=FONT_ENTRY, textvariable=budget_var)
item_name = Entry(f1, font=FONT_ENTRY,textvariable=namevar)
item_amt = Entry(f1, font=FONT_ENTRY,textvariable=amtvar)
transaction_date = Entry(f1, font=FONT_ENTRY,textvariable=dopvar)
dopvar.set("YYYY-MM-DD")


budget_entry.grid(row=0,column=1,sticky=EW,padx=(10,0))
item_name.grid(row=1,column=1,sticky=EW,padx=(10,0))
item_amt.grid(row=2,column=1,sticky=EW,padx=(10,0))
transaction_date.grid(row=3,column=1,sticky=EW,padx=(10,0))


#action Buttons
cur_date = Button(
    f1,
    text='Current Date',
    font=FONT_BUTTON,
    bg=PRIMARY, 
    fg=WHITE,
    width=15,
    relief=FLAT,
    command=setDate,
    )

budget_btn = Button(
    f1,
    text='Set Budget',
    font=FONT_BUTTON,
    bg=SUCCESS, 
    fg=WHITE,
    width=15,
    relief=FLAT,
    command=setBudget
)

submit_btn = Button(
    f1,
    text='Save Record',
    font=FONT_BUTTON,
    bg=PRIMARY,
    fg=WHITE,
    width=15,
    relief=FLAT,
    command=saveRecord
)


clr_btn = Button(
    f1,
    text='Clear Entry',
    font=FONT_BUTTON,
    bg=PRIMARY,
    fg='white',
    width=15,
    relief=FLAT,
    command=clearEntries
)

quit_btn = Button(
    f1,
    text='Exit',
    font=FONT_BUTTON,
    bg=DANGER, 
    fg=WHITE,
    width=15,
    relief=FLAT,
    command=lambda:ws.destroy()
)

total_bal = Button(
    f1,
    text='Total Balance',
    font=f,
    bg=SECONDARY, 
    fg=WHITE,
    width=15,
    relief=FLAT,
    command=totalBalance
)

update_btn = Button(
    f1,
    text='Update',
    font=FONT_BUTTON,
    bg=SECONDARY, 
    fg=WHITE,
    width=15,
    relief=FLAT,
    command=update_record
)

del_btn = Button(
    f1,
    text='Delete',
    font=FONT_BUTTON,
    bg=DANGER,
    fg=WHITE,
    width=15,
    relief=FLAT,
    command=deleteRow
)

report_btn = Button(
    f1,
    text='Generate Report',
    font=FONT_BUTTON,
    bg=PRIMARY, 
    fg=WHITE,
    width=15,
    relief=FLAT,
    command=openReportWindow
)


#grid placement
# Row 0
budget_btn.grid(row=0, column=2, sticky=EW, padx=10, pady=4)
total_bal.grid(row=0, column=3, sticky=EW, padx=10, pady=4)

# Row 1
submit_btn.grid(row=1, column=2, sticky=EW, padx=10, pady=4)
update_btn.grid(row=1, column=3, sticky=EW, padx=10, pady=4)

# Row 2
clr_btn.grid(row=2, column=2, sticky=EW, padx=10, pady=4)
del_btn.grid(row=2, column=3, sticky=EW, padx=10, pady=4)

# Row 3
quit_btn.grid(row=3, column=2, sticky=EW, padx=10, pady=4)
report_btn.grid(row=3, column=3, sticky=EW, padx=10, pady=4)

# Utility button under entries
cur_date.grid(row=4, column=1, sticky=EW, padx=10, pady=6)


#TreeView
tv = ttk.Treeview(f2, columns=(1,2,3,4), show='headings',height=8)
tv.pack(side="left")

#add heading
tv.column(1,anchor=CENTER, stretch=NO, width=70)
tv.column(2, anchor=CENTER)
tv.column(3, anchor=CENTER)
tv.column(4, anchor=CENTER)
tv.heading(1,text="Serial no")
tv.heading(2, text="Item Name")
tv.heading(3, text="Item Price")
tv.heading(4,text="Purchase Date")

#binding treeview
tv.bind("<ButtonRelease-1>",select_record)

#style for treeview
style = ttk.Style()
style.theme_use("clam")
style.configure(
    "Treeview",
    font=('Segoe UI', 10),
    rowheight=28
)
style.configure(
    "Treeview.Heading",
    font=('Segoe UI', 11, 'bold')
)


#Vertical Scrollbar
scrollbar = Scrollbar(f2, orient='vertical')
scrollbar.configure(command=tv.yview)
scrollbar.pack(side="right",fill="y")
tv.config(yscrollcommand=scrollbar.set)

#calline function
fetch_records()

#infinite loop
ws.mainloop()