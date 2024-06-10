import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkcalendar import DateEntry
from ics import Calendar as ICS_Calendar, Event
import datetime

class TaskManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Task Manager")  # Setează titlul ferestrei
        self.geometry("900x700")  # Setează dimensiunile ferestrei

        # Structuri de date pentru sarcini și elemente GUI
        self.tasks = {"To Do": [], "In Progress": [], "Done": []}  # Dicționar pentru sarcini organizate pe stadii
        self.frames = {}  # Dicționar pentru cadrele din interfață
        self.lists = {}  # Dicționar pentru listele de sarcini
        self.priorities = {'Low': '#ADD8E6', 'Medium': '#FFD700', 'High': '#FF6347'}  # Culori pentru priorități

        # Culori de fundal și text pentru diferitele stadii ale sarcinilor
        background_colors = {"To Do": "#FFD580", "In Progress": "#FFFF99", "Done": "#D0F0C0"}
        text_colors = {"To Do": "#000080", "In Progress": "#FF8C00", "Done": "#006400"}

        main_frame = tk.Frame(self)  # Cadru principal pentru listele de sarcini
        main_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=5, pady=5)

        # Crearea cadrelor pentru fiecare categorie de sarcini
        for i, (status, bg_color) in enumerate(background_colors.items()):
            frame = tk.Frame(main_frame, bd=2, relief=tk.RAISED, bg=bg_color)
            frame.pack(fill=tk.BOTH, expand=True, side=tk.TOP, padx=5, pady=5)
            tk.Label(frame, text=status, bg=bg_color, font=('Arial', 12, 'bold'), fg='black').pack(fill=tk.X)
            listbox = tk.Listbox(frame, fg=text_colors[status], bg=bg_color, selectmode=tk.SINGLE, font=('Arial', 10))
            listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            self.lists[status] = listbox

        # Cadru pentru introducerea și adăugarea sarcinilor
        entry_frame = tk.Frame(self, bg='white')
        entry_frame.pack(fill=tk.Y, side=tk.RIGHT, padx=5, pady=5, anchor='n')

        tk.Label(entry_frame, text="Task:").pack(side=tk.TOP, anchor='w', padx=5, pady=2)
        self.task_entry = tk.Entry(entry_frame)
        self.task_entry.pack(side=tk.TOP, fill=tk.X, expand=True, padx=5, pady=2)

        tk.Label(entry_frame, text="Priority:").pack(side=tk.TOP, anchor='w', padx=5, pady=2)
        self.priority_var = tk.StringVar(value='Medium')
        for key in self.priorities:
            ttk.Radiobutton(entry_frame, text=key, value=key, variable=self.priority_var).pack(anchor='w', padx=5)

        tk.Label(entry_frame, text="Due Date:").pack(side=tk.TOP, anchor='w', padx=5, pady=2)
        self.date_entry = DateEntry(entry_frame, width=16, background='darkblue', foreground='white', borderwidth=2)
        self.date_entry.pack(side=tk.TOP, fill=tk.X, expand=True, padx=5, pady=2)

        tk.Label(entry_frame, text="Due Time (HH:MM):").pack(side=tk.TOP, anchor='w', padx=5, pady=2)
        self.time_entry = tk.Entry(entry_frame)
        self.time_entry.pack(side=tk.TOP, fill=tk.X, expand=True, padx=5, pady=2)

        add_button = tk.Button(entry_frame, text="Add Task", command=self.add_task)
        add_button.pack(side=tk.TOP, pady=5)

        # Buton pentru exportul sarcinilor într-un fișier de calendar
        tk.Button(self, text="Export Tasks to Calendar", command=self.export_tasks_to_calendar).pack(side=tk.BOTTOM, pady=5)

    def add_task(self):
        # Extrage și validează informațiile introduse de utilizator
        task_text = self.task_entry.get().strip()
        priority = self.priority_var.get()
        due_date = self.date_entry.get_date()
        due_time = self.time_entry.get().strip()
        try:
            # Încercare de conversie a timpului într-un obiect datetime.time
            due_time_obj = datetime.datetime.strptime(due_time, "%H:%M").time()
        except ValueError:
            # Afișează un mesaj de eroare dacă timpul nu este în formatul corect
            messagebox.showerror("Invalid time format", "Please enter the time in HH:MM format.")
            return

        # Combinează data și timpul într-un singur obiect datetime
        due_datetime = datetime.datetime.combine(due_date, due_time_obj)
        
        # Verifică dacă textul sarcinii nu este gol
        if task_text:
            # Crează un tuplu pentru sarcină și îl adaugă la lista de "To Do"
            task = (task_text, priority, due_datetime)
            self.tasks["To Do"].append(task)
            # Setează culoarea de fundal în funcție de prioritate
            color = self.priorities[priority]
            # Adaugă sarcina în listbox și aplică culoarea corespunzătoare
            index = self.lists["To Do"].size()
            self.lists["To Do"].insert(tk.END, f"{task_text} [{priority}] Due: {due_datetime}")
            self.lists["To Do"].itemconfig(index, {'bg': color})
            # Curăță câmpurile de introducere după adăugare
            self.task_entry.delete(0, tk.END)
            self.time_entry.delete(0, tk.END)

    def move_task(self, status):
        # Obține statusul actual al sarcinii selectate
        from_status = next((s for s in self.tasks if self.lists[s].curselection()), None)
        if from_status and from_status != status:
            selected_index = self.lists[from_status].curselection()[0]
            # Extrage sarcina selectată
            task = self.tasks[from_status][selected_index]
            # Șterge sarcina din lista și dicționarul actual
            self.lists[from_status].delete(selected_index)
            self.tasks[from_status].remove(task)
            # Adaugă sarcina la noua categorie și actualizează vizualizarea
            self.tasks[status].append(task)
            self.lists[status].insert(tk.END, f"{task[0]} [{task[1]}] Due: {task[2]}")
            self.lists[status].itemconfig(self.lists[status].size() - 1, {'bg': self.priorities[task[1]]})

    def export_tasks_to_calendar(self):
        # Deschide un dialog pentru salvarea fișierului
        file_path = filedialog.asksaveasfilename(defaultextension=".ics", filetypes=[("iCalendar files", "*.ics")])
        if file_path:
            cal = ICS_Calendar()
            # Adaugă evenimente pentru fiecare sarcină din dicționar
            for status, tasks in self.tasks.items():
                for task in tasks:
                    event = Event()
                    event.name = task[0]
                    event.begin = task[2].strftime("%Y-%m-%d %H:%M:%S")
                    event.description = f"Priority: {task[1]}, Status: {status}"
                    cal.events.add(event)
            # Scrie evenimentele în fișierul specificat
            with open(file_path, "w") as file:
                file.writelines(cal)
            # Afișează un mesaj de succes
            messagebox.showinfo("Export Successful", "Tasks have been successfully exported to your calendar.")

if __name__ == "__main__":
    app = TaskManager()
    app.mainloop()
