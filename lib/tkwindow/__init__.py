from multiprocessing import Process
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from ttkthemes import themed_tk

from lib.bot import DiscussionBot

def place_window_top_left(root, width, height):
    # get screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # calculate position x and y coordinates
    x = (screen_width/2.5) - width
    y = (screen_height/3) - height
    root.geometry('%dx%d+%d+%d' % (width, height, x, y))

def place_left_of_window(window, root, width, height):
    x = window.winfo_x()/3
    y = window.winfo_y() - (window.winfo_y()/2)
    root.geometry('%dx%d+%d+%d' % (width, height, x, y))

class ProcWindow(themed_tk.ThemedTk, Toplevel):
    def __init__(self, theme):
        super().__init__(theme=theme, themebg=True)
        s = ttk.Style()
        s.configure('.', font=('Arial', 11))

        self.rows_map = {}
        self.active_processes = []

        self.theme = theme
        self.title('Active processes')
        self.row_count = 1

        bgcolor = self.config('background')[4] # Current background color
        self.window_title_label = Label(
            self, text='Active grading processes',
            fg='#22a6b5',
            bg=bgcolor,
            font=('Arial', 15),
            wraplength=230
        )

        self.window_title_label.grid(row=0, column=0)

    def terminate_all_processes(self):
        for proc in self.active_processes:
            proc.terminate()
        self.active_processes.clear()

    def terminate_process(self, proc, row_number):
        proc.terminate()
        x = self.rows_map[row_number]
        x[0].after(1000, x[0].destroy())
        x[1].destroy()

        try: self.active_processes.remove(proc)
        except: pass

    def add_process(self, proc, proc_name):
        self.row_count += 1
        proc_label = Label(self, justify=LEFT, text=proc_name)
        proc_button = Button(
            self, text='Kill', 
            bg='#c82333',
            fg='#ffffff',
            command=lambda: self.terminate_process(proc, self.row_count),
        )
        self.rows_map[self.row_count] = [proc_label, proc_button]
        proc_label.grid(sticky=W+E, row=self.row_count, column=0)
        proc_button.grid(sticky=W+E, row=self.row_count, column=1)
        self.columnconfigure(0, weight=2)
        self.columnconfigure(0, weight=1)

        self.active_processes.append(proc)

class DiscussionWindow(themed_tk.ThemedTk):
    def __init__(self, theme, email, courses_list, discussions_list):
        super().__init__(theme=theme, themebg=True)

        s = ttk.Style()
        s.configure('.', font=('Arial', 14))

        self.theme = theme
        self.email = email
        self.courses_opts = courses_list
        self.discussions_opts = discussions_list

        self.title('CSCI-1100 Discussion Auto-grade Bot')
        self.title_large = 'CSCI-1100 Discussion Bot'
        w = 508; h = 364
        self.minsize(w, h)
        #place_window_top_left(self, w, h)

        self.init_components()
        self.init_labels()
        self.add_to_window()

        p = ProcWindow(self.theme)
        p.grab_set()
        place_left_of_window(self, p, 250, 300)
        self.proc_window = p

        mainloop()

    def destroy_windows(self):
        self.proc_window.terminate_all_processes()
        self.proc_window.destroy()
        self.destroy()

    def init_discussion_bot_instance(self):
        course_name = self.course_name_field.get()
        discussion_name = self.discussion_name_field.get()
        args = (
            self.theme,
            self.email_field.get(),
            self.password_field.get(),
            course_name,
            discussion_name,
            int(self.min_word_count_box.get()),
        )
        p = Process(
            target=DiscussionBot,
            args=args
        )
        p.start()
        pname = course_name[-3:] + '-' + discussion_name[:25]
        self.proc_window.add_process(p, proc_name=pname)

    def init_components(self):
        # Not using clear button; may implement, may not.
        self.clear_button = ttk.Button(
            self, text='Clear',
            command=None
        )

        self.start_button = ttk.Button(
            self, text='Start',
            command=self.init_discussion_bot_instance
        )

        self.exit_button = ttk.Button(
            self, text='Exit',
            command=self.destroy_windows
        )

        self.email_field = ttk.Entry(self, width=41)
        self.email_field.insert(0, self.email)

        self.password_field = ttk.Entry(self, show="•", width=41)
        
        self.course_name_field = StringVar(self)

        self.course_name_optmenu = ttk.OptionMenu(
            self, self.course_name_field,
            self.courses_opts[0],
            *self.courses_opts
        )

        self.discussion_name_field = StringVar(self)

        self.discussion_name_optmenu = ttk.OptionMenu(
            self, self.discussion_name_field,
            self.discussions_opts[0],
            *self.discussions_opts
        )

        self.min_word_count_box = ttk.Spinbox(
            self, from_=10, to=30,
            foreground='#000000'
        )
        self.min_word_count_box.insert(0, 14)

    def init_labels(self):
        bgcolor = self.config('background')[4] # Current background color
        self.window_title_label = Label(
            self, text=self.title_large,
            fg='#22a6b5',
            bg=bgcolor,
            font=('Arial', 20),
            wraplength=350
        )

        self.email_label = ttk.Label(text='Email:')
        self.password_label = ttk.Label(text='Password:')
        self.course_name_label = ttk.Label(text='Course:')
        self.discussion_name_label = ttk.Label(text='Discussion:')
        self.min_word_count_label = ttk.Label(text='Min Word Count:')
    
    def add_to_window(self):
        self.window_title_label.place(x=76, y=16)

        self.email_label.place(x=32, y=92)
        self.email_field.place(x=180, y=92)

        self.password_label.place(x=32, y=120)
        self.password_field.place(x=180, y=120)

        self.course_name_label.place(x=32, y=156)
        self.course_name_optmenu.place(x=180, y=156)

        self.discussion_name_label.place(x=32, y=196)
        self.discussion_name_optmenu.place(x=180, y=196)

        self.min_word_count_label.place(x=32, y=252)
        self.min_word_count_box.place(x=180, y=252)

        self.start_button.place(x=180, y=308)
        self.exit_button.place(x=310, y=308)
