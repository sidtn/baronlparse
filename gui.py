import tkinter
from tkinter import ttk
from get_lists import get_lists

root = tkinter.Tk()
root.geometry('260x300')


selections = [key for key in get_lists()[3]]

ttk.Label(text='Выберите раздел').grid(row=1, column=1, columnspan=2, padx=80, pady=5, sticky='w')
ttk.Label(text='Выберите подраздел').grid(row=3, column=1, columnspan=2, padx=80, pady=5, sticky='w')

menu_selections = ttk.Combobox(root, width=37, value=(selections))
menu_selections.grid(row=2, column=1, columnspan=2, padx=10, pady=5, sticky='w')

def callback(event):
    abc = event.widget.get()
    selection = menu_selections.get()
    menu_subselections.config(values=get_lists()[3][selection])

menu_subselections = ttk.Combobox(root, width=37)
menu_subselections.grid(row=4, column=1, columnspan=2, padx=10, pady=5, sticky='w')
menu_subselections.bind('<Button-1>', callback)

def press(event):
    inp = menu_subselections.get()
    print(inp)


button = ttk.Button(root, text='Парсить')
button.grid(row=5, column=1, columnspan=2, padx=90, pady=20, sticky='w')
button.bind('<Button-1>', press)


root.mainloop()