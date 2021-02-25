from tkinter import *
from tkinter import ttk
from tkinter import simpledialog
from datetime import datetime, timedelta
import csv
import os
import sys


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def date_format(x): return str(x.strftime("%d/%m/%Y"))


def delete_popup():
    win = Toplevel()
    win.wm_title("New CSV")
    win.iconbitmap(resource_path('checkbox.ico'))
    label = Label(win, text="Are you sure you want to overwrite the CSV file?", padx=10, pady=20)
    label.pack(side='top')
    okay = Button(win, text="Okay", command=delete_csv, padx=10)
    okay.pack(side='left', padx=20, pady=10)
    cancel = Button(win, text="Cancel", command=win.destroy, padx=10)
    cancel.pack(side='left', padx=50, pady=10)


def delete_csv():
    with open('commitments.csv', 'w', newline='') as f:
        csv_writer = csv.DictWriter(f, fieldnames=['date'])
        csv_writer.writeheader()
        csv_writer.writerow({
            'date': now
        })
    root.destroy()


class App(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(bg='white smoke')
        self.canvas = Canvas(self, borderwidth=0, bg='white smoke', width=550, height=350)
        self.grid_frame = Frame(self.canvas, bg='seashell3')
        self.vsb = Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.hsb = Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)
        self.button_frame = Frame(self, bg='white smoke')
        self.add = Button(self.button_frame, text='Add', width=3, padx=15, command=self.add_commit)
        self.delete = Button(self.button_frame, text='Delete', width=3, padx=15, command=self.del_commit)
        self.log = Button(self.button_frame, text='Log', width=3, padx=15, command=self.log_window)
        self.new = Button(self.button_frame, text='New CSV', width=3, padx=15, command=delete_popup)
        self.separator = ttk.Separator(self, orient='horizontal')
        self.item_list, self.commitments = self.get_data()
        self.append_csv(self.commitments)
        self.compile()

    def add_commit(self):
        user = simpledialog.askstring(title="Add Commitment", prompt="Type name of commitment:")
        if user and not user.isnumeric() and not user.lower() in [i.lower() for i in self.commitments]:
            self.item_list[0].append(self.get_label(user, 'orchid3'))
            self.item_list[-1].append(self.get_label('-'))
            self.commitments.append(user)
            self.append_csv(self.commitments)
            self.grid_all()

    def del_commit(self):
        if len(self.commitments) > 0:
            user = simpledialog.askstring(title="Delete Commitment", prompt="Type name or column of commitment:")
            if user is None:
                return
            elif (user and user.lower() in [i.lower() for i in self.commitments]) \
                    or (user.isnumeric() and 0 < int(user) <= len(self.commitments)):
                self.forget_all()
                if user.isnumeric():
                    index = int(user)
                    self.commitments.pop(index - 1)
                else:
                    index = self.commitments.index(user.lower()) + 1
                    self.commitments.remove(user)
                for row in self.item_list:
                    row.pop(index)
                self.append_csv(self.commitments)
                self.grid_all()

    def log_window(self):
        if len(self.commitments) > 0:
            win = Toplevel()
            win.wm_title("Log")
            win.iconbitmap(resource_path('checkbox.ico'))
            win.geometry('250x150')
            label = Label(win, text="""Type name or column of commitment 
            and select log type.""", padx=10, pady=20)
            label.pack(side='top')
            entry = Entry(win)
            entry.pack()
            achieved = Button(win, text="Achieved", command=lambda: self.log_commit(entry.get(), True), padx=10, justify='center', anchor='e')
            achieved.pack(side='left', padx=5, pady=10, anchor='e')
            failed = Button(win, text="Failed", command=lambda: self.log_commit(entry.get(), False), padx=10, justify='center', anchor='e')
            failed.pack(side='left', padx=5, pady=10, anchor='e')
            back = Button(win, text="Back", command=win.destroy, padx=5, justify='center', anchor='e')
            back.pack(side='left', padx=15, pady=10, anchor='e')

    def log_commit(self, commitment, achieve):
        if (commitment and commitment.lower() in [i.lower() for i in self.commitments]) or \
                (commitment.isnumeric() and 0 < int(commitment) <= len(self.commitments)):
            if commitment.isnumeric():
                index = int(commitment)
            else:
                index = self.commitments.index(commitment.lower()) + 1
            self.item_list[-1][index]['bg'] = 'spring green' if achieve else 'tomato'
            self.item_list[-1][index]['text'] = ''
            self.append_csv(self.commitments)

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def get_data(self):
        commit_data = []
        dates = []
        try:
            with open('commitments.csv', 'r') as f:
                csv_reader = csv.DictReader(f)
                commitments = [i for i in csv_reader.fieldnames if i != 'date']
                for line in csv_reader:
                    dates.append(line['date'])
                    commits = []
                    for commitment in commitments:
                        commits.append(line.get(commitment) if line.get(commitment) else None)
                    commit_data.append(commits)
            if dates[-1] != now:
                updated_date = dates[-1]
                while updated_date != now:
                    updated_date = date_format(datetime.strptime(updated_date, "%d/%m/%Y") + timedelta(days=1))
                    dates.append(updated_date)
                    commit_data.append(['0' if updated_date != now else '-' for c in commitments])

        except FileNotFoundError:
            commitments = []
            commit_data.append([])
            dates.append(now)
            delete_csv()
        item_list = [[self.get_label('dates/commitments', 'orchid3')]]
        for commitment in commitments:
            item_list[0].append(self.get_label(commitment, 'orchid3'))
        for i, date in enumerate(dates):
            item_list.append([self.get_label(date, 'orchid3')])
            if commit_data[i]:
                item_list[i + 1].extend(None if j is None else self.get_label(j if date == now or j == '1' else '0') for j in commit_data[i])
        return item_list, commitments

    def get_label(self, x, colour='white', button=False):
        if x == '0':
            return Label(self.grid_frame, bg='tomato')
        elif x == '1':
            return Label(self.grid_frame, bg='spring green')
        else:
            return Label(self.grid_frame, text=x, bg=colour)

    def append_csv(self, commitments):
        with open('commitments.csv', 'w', newline='') as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow(['date'] + commitments)
            for row in self.item_list[1:]:
                new_row = []
                for item in row:
                    if item is None:
                        new_row.append(None)
                    else:
                        new_row.append(item['text'] if item['text'] else '0' if item['bg'] == 'tomato' else '1')
                csv_writer.writerow(new_row)

    def compile(self):
        self.pack()
        self.button_frame.pack(side='top', padx=15, pady=10, fill='x', expand=True)
        self.add.pack(side='left', anchor='w')
        self.delete.pack(side='left', padx=20, anchor='w')
        self.log.pack(side='left', padx=5, anchor='w')
        self.new.pack(side='left', padx=15, anchor='w')
        self.separator.pack(side='top', fill='x', expand=True)
        self.vsb.pack(side="right", fill="y")
        self.hsb.pack(side='bottom', fill='x')
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((0, 0), window=self.grid_frame, anchor="nw",
                                  tags="self.frame")
        self.grid_frame.bind("<Configure>", self.on_frame_configure)
        self.grid_all()

    def grid_all(self):
        for i, row in enumerate(self.item_list):
            for j, item in enumerate(row):
                if item is not None:
                    item.grid(row=i, column=j, padx=2, pady=2, ipadx=2, ipady=2, sticky=NSEW)

    def forget_all(self):
        for row in self.item_list:
            for item in row:
                if item is not None:
                    item.grid_forget()


if __name__ == '__main__':
    now = date_format(datetime.now())
    root = Tk()
    root.title('commitments')
    root.resizable(False, False)
    root.iconbitmap(resource_path('checkbox.ico'))
    app = App(root)
    mainloop()
