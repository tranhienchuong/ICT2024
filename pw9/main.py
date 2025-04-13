# pw9/main.py
import tkinter as tk
from tkinter import ttk  # Themed widgets
from tkinter import messagebox, simpledialog, Frame, Label, Button, Listbox, Scrollbar, Toplevel, Entry

# Import the separated application logic
from .app_logic import AppLogic
# Import data classes (needed for type hints or checks if desired)
# from .domains import Student, Course

# --- Input Dialogs (Example using Toplevel) ---

class AddStudentDialog(Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Add New Student")
        self.geometry("300x150")
        self.transient(parent) # Associate with parent window
        self.grab_set() # Modal behavior

        self.result = None # To store the entered data

        Label(self, text="Student ID:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.id_entry = Entry(self)
        self.id_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        Label(self, text="Name:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.name_entry = Entry(self)
        self.name_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        Label(self, text="Date of Birth (DoB):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.dob_entry = Entry(self)
        self.dob_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        button_frame = Frame(self)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)

        Button(button_frame, text="Add", command=self.on_add).pack(side="left", padx=5)
        Button(button_frame, text="Cancel", command=self.destroy).pack(side="left", padx=5)

        self.columnconfigure(1, weight=1) # Make entry column expandable

        # Wait for the dialog to close
        self.wait_window(self)

    def on_add(self):
        s_id = self.id_entry.get().strip()
        s_name = self.name_entry.get().strip()
        s_dob = self.dob_entry.get().strip()

        if not s_id or not s_name or not s_dob:
            messagebox.showwarning("Input Error", "All fields are required.", parent=self)
            return

        self.result = (s_id, s_name, s_dob)
        self.destroy() # Close the dialog

# --- Main GUI Application ---

class StudentAppGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Student Management System")
        self.geometry("800x600") # Adjust size as needed

        # Initialize the application logic handler
        self.logic = AppLogic()

        # Set up protocol for closing the window
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Create main UI components
        self.create_widgets()

        # Load initial data and populate lists
        self.refresh_student_list()
        self.refresh_course_list()

    def create_widgets(self):
        # Use themed widgets for a better look
        style = ttk.Style(self)
        style.theme_use('clam') # Or 'alt', 'default', 'vista', etc.

        # Main frame
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill="both", expand=True)

        # --- Control Frame (Buttons) ---
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(pady=10, fill="x")

        ttk.Button(control_frame, text="Add Student", command=self.open_add_student_dialog).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Add Course", command=self.open_add_course_dialog).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Input Marks", command=self.open_input_marks_dialog).pack(side="left", padx=5)
        ttk.Button(control_frame, text="List Sorted by GPA", command=self.list_students_sorted).pack(side="left", padx=5)

        # --- Display Area (using PanedWindow for resizing) ---
        paned_window = tk.PanedWindow(main_frame, orient="horizontal", sashrelief="raised")
        paned_window.pack(fill="both", expand=True, pady=5)

        # --- Student List Frame ---
        student_frame = ttk.Frame(paned_window, padding=5)
        ttk.Label(student_frame, text="Students", font=('Arial', 12, 'bold')).pack(pady=5)
        student_cols = ('id', 'name', 'dob', 'gpa')
        self.student_tree = ttk.Treeview(student_frame, columns=student_cols, show='headings', selectmode='browse')
        self.student_tree.heading('id', text='ID')
        self.student_tree.heading('name', text='Name')
        self.student_tree.heading('dob', text='DoB')
        self.student_tree.heading('gpa', text='GPA')
        self.student_tree.column('id', width=80, anchor='w')
        self.student_tree.column('name', width=200, anchor='w')
        self.student_tree.column('dob', width=100, anchor='w')
        self.student_tree.column('gpa', width=50, anchor='e') # Align GPA right
        # Scrollbar for students
        student_scroll = ttk.Scrollbar(student_frame, orient="vertical", command=self.student_tree.yview)
        self.student_tree.configure(yscrollcommand=student_scroll.set)
        student_scroll.pack(side="right", fill="y")
        self.student_tree.pack(fill="both", expand=True)
        paned_window.add(student_frame) # Give students more initial space

        # --- Course List Frame ---
        course_frame = ttk.Frame(paned_window, padding=5)
        ttk.Label(course_frame, text="Courses", font=('Arial', 12, 'bold')).pack(pady=5)
        course_cols = ('id', 'name', 'credits')
        self.course_tree = ttk.Treeview(course_frame, columns=course_cols, show='headings', selectmode='browse')
        self.course_tree.heading('id', text='ID')
        self.course_tree.heading('name', text='Name')
        self.course_tree.heading('credits', text='Credits')
        self.course_tree.column('id', width=80, anchor='w')
        self.course_tree.column('name', width=200, anchor='w')
        self.course_tree.column('credits', width=60, anchor='e') # Align credits right
        # Scrollbar for courses
        course_scroll = ttk.Scrollbar(course_frame, orient="vertical", command=self.course_tree.yview)
        self.course_tree.configure(yscrollcommand=course_scroll.set)
        course_scroll.pack(side="right", fill="y")
        self.course_tree.pack(fill="both", expand=True)
        paned_window.add(course_frame) # Give courses less initial space

        # --- Marks Display (Could be another frame/treeview added when needed) ---
        # Placeholder or integrate with student/course selection

    # --- Refresh Methods ---
    def refresh_student_list(self, sorted_list=None):
        """Clears and repopulates the student Treeview."""
        # Clear existing items
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)
        # Get data (either sorted or default)
        students_to_display = sorted_list if sorted_list is not None else self.logic.get_students()
        # Populate with new data
        for student in students_to_display:
             gpa_str = f"{student.gpa:.2f}" if student.gpa is not None else "N/A"
             self.student_tree.insert('', 'end', values=(student.id, student.name, student.dob, gpa_str))

    def refresh_course_list(self):
        """Clears and repopulates the course Treeview."""
        for item in self.course_tree.get_children():
            self.course_tree.delete(item)
        for course in self.logic.get_courses():
            self.course_tree.insert('', 'end', values=(course.id, course.name, course.credits))


    # --- Callback Methods ---
    def open_add_student_dialog(self):
        dialog = AddStudentDialog(self) # Use the custom dialog
        if dialog.result: # If user clicked Add and data is valid
             s_id, s_name, s_dob = dialog.result
             if self.logic.add_student(s_id, s_name, s_dob):
                  messagebox.showinfo("Success", f"Student {s_id} added successfully.", parent=self)
                  self.refresh_student_list() # Update the list view
             else:
                  # More specific error needed from logic ideally
                  messagebox.showerror("Error", f"Failed to add student {s_id}. ID might already exist or invalid input.", parent=self)

    def open_add_course_dialog(self):
        # Simple dialogs for now, could use custom Toplevel like AddStudentDialog
        c_id = simpledialog.askstring("Add Course", "Enter Course ID:", parent=self)
        if not c_id: return
        c_name = simpledialog.askstring("Add Course", "Enter Course Name:", parent=self)
        if not c_name: return
        c_credits = simpledialog.askstring("Add Course", "Enter Course Credits:", parent=self)
        if not c_credits: return

        if self.logic.add_course(c_id.strip(), c_name.strip(), c_credits.strip()):
             messagebox.showinfo("Success", f"Course {c_id} added successfully.", parent=self)
             self.refresh_course_list()
        else:
             messagebox.showerror("Error", f"Failed to add course {c_id}. Check ID doesn't exist and credits are valid.", parent=self)

    def open_input_marks_dialog(self):
         # This needs a more complex dialog: select course, select student, enter mark
         # For simplicity, maybe start by selecting course from the Treeview first?
         # Or use a simpledialog loop - less user friendly
         selected_course_items = self.course_tree.selection()
         if not selected_course_items:
              messagebox.showwarning("Select Course", "Please select a course from the list first.", parent=self)
              return
         selected_iid = selected_course_items[0]
         course_id = self.course_tree.item(selected_iid, 'values')[0]
         course_name = self.course_tree.item(selected_iid, 'values')[1]

         if not self.logic.get_students():
             messagebox.showwarning("No Students", "Please add students before inputting marks.", parent=self)
             return

         # Loop through students (could be a custom dialog showing all students for this course)
         updated = False
         for student in self.logic.get_students():
             mark_str = simpledialog.askstring("Input Mark", f"Enter mark for {student.name} ({student.id})\nin Course: {course_name} ({course_id})", parent=self)
             if mark_str is None: continue # User cancelled for this student or closed dialog
             if self.logic.add_mark(course_id, student.id, mark_str.strip()):
                 updated = True
             else:
                 messagebox.showerror("Input Error", f"Invalid mark entered for {student.name}.", parent=self)
                 # Decide whether to continue or stop for this student
         if updated:
              messagebox.showinfo("Marks Input", f"Marks updated for course {course_name}. GPA needs recalculation.", parent=self)
              # Force GPA recalculation and update student list display
              self.logic.calculate_all_gpas()
              self.refresh_student_list()

    def list_students_sorted(self):
        """Calculates GPAs and displays students sorted by GPA."""
        sorted_list = self.logic.get_students_sorted_by_gpa()
        self.refresh_student_list(sorted_list=sorted_list)
        messagebox.showinfo("Students Sorted", "Student list refreshed and sorted by GPA (descending).", parent=self)


    def on_closing(self):
        # Ask for confirmation
        if messagebox.askokcancel("Quit", "Do you want to save data and quit?"):
            # Initiate background save
            if self.logic.save_in_background():
                 messagebox.showinfo("Saving", "Data save initiated in background.\nProgram will now exit.", parent=self)
            else:
                 messagebox.showwarning("Saving", "Could not start background save.\nCheck console for errors.\nExiting anyway.", parent=self)
            # Close the main window
            self.destroy()
        # If user clicks cancel, do nothing, window stays open


# --- Main Execution ---
if __name__ == "__main__":
    # Check dependencies (optional but good practice)
    try:
        import numpy
    except ImportError:
        print("Error: NumPy not found. Please install using: pip install numpy")
        sys.exit(1)

    # Create and run the GUI application
    app = StudentAppGUI()
    app.mainloop()