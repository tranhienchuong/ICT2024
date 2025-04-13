# pw8/main.py
import curses
import sys
import time
import math
import numpy as np
import os
import pickle
import gzip
import threading # <-- Import threading module
import copy      # <-- Import copy module for deep copies (safer for threading)

# Import classes and functions from our modules
from .domains import Student, Course
from . import input as data_input
from . import output as ui

SAVE_FILE = "student_data.pkl.gz" # Keep the same filename

class Application:
    def __init__(self):
        self.students = []
        self.courses = []
        self.marks = {}
        # Loading still happens synchronously at the start
        self._load_data_pickle()
        # Thread handle for saving, initially None
        self.save_thread = None

    # --- Loading Method (Remains Synchronous) ---
    def _load_data_pickle(self, stdscr=None):
        # ... (Keep the existing _load_data_pickle method from pw6 exactly as is) ...
        # ... (It handles os.path.exists, gzip.open, pickle.load, error checking) ...
        if os.path.exists(SAVE_FILE):
            try:
                # Optional: Display loading message via UI if stdscr is available
                # if stdscr: ui.display_message(stdscr, f"Loading data from {SAVE_FILE}...", wait=False)
                # else: print(f"Loading data from {SAVE_FILE}...") # Fallback

                with gzip.open(SAVE_FILE, 'rb') as f:
                    loaded_data = pickle.load(f)
                self.students = loaded_data.get('students', [])
                self.courses = loaded_data.get('courses', [])
                self.marks = loaded_data.get('marks', {})
                self._invalidate_gpas()

                # Optional: Display success message
                # if stdscr: ui.display_message(stdscr, "Data loaded successfully. Press key.", wait=True)

            except Exception as e: # Catch broader exceptions during load
                 # Optionally display error via UI
                 # if stdscr: ui.display_message(stdscr, f"Error loading data: {e}. Starting fresh.", color_pair=2, wait=True)
                 # else: print(f"Error loading data: {e}. Starting fresh.")
                 # If loading fails, ensure we start with empty lists/dict
                 self.students, self.courses, self.marks = [], [], {}
        else:
             # Optional: Display starting fresh message via UI
             # if stdscr: ui.display_message(stdscr, f"Save file {SAVE_FILE} not found. Starting fresh.", color_pair=3, wait=True)
             pass # Silently start fresh if no file


    # --- NEW Background Saving Logic ---

    def _save_thread_target(self, data_to_save):
        """This function runs in the background thread to save data."""
        # This contains the core saving logic from pw6's _save_data_pickle
        thread_name = threading.current_thread().name
        print(f"\n[{thread_name}] Starting background save to {SAVE_FILE}...") # Print from thread
        try:
            with gzip.open(SAVE_FILE, 'wb') as f:
                pickle.dump(data_to_save, f, pickle.HIGHEST_PROTOCOL)
            print(f"[{thread_name}] Background save completed.") # Print from thread

        except Exception as e:
            # Error handling in background thread is tricky. Printing is simplest.
            print(f"\n[{thread_name}] ERROR during background save: {e}", file=sys.stderr)

    def save_in_background(self):
        """Initiates the saving process in a background daemon thread."""
        # Prevent starting multiple save threads if one is already running
        if self.save_thread and self.save_thread.is_alive():
            print("Note: Previous save operation still in progress.")
            # Optionally provide feedback via UI if stdscr is available
            return

        print("\nInitiating background save...") # Message in main thread

        # Create DEEP copies of the data to avoid race conditions
        # If the main thread modified lists/dicts while the background thread reads them,
        # errors can occur. Deepcopy is safest.
        try:
             data_copy = {
                 'students': copy.deepcopy(self.students),
                 'courses': copy.deepcopy(self.courses),
                 'marks': copy.deepcopy(self.marks)
             }
        except Exception as e:
             print(f"\nError creating deep copy for saving: {e}", file=sys.stderr)
             # Optionally provide feedback via UI
             return # Don't start thread if copy fails

        # Create and configure the thread
        self.save_thread = threading.Thread(
            target=self._save_thread_target,
            args=(data_copy,), # Pass the copied data to the thread function
            name="SaveThread",
            daemon=True # Set as daemon thread
        )
        # Start the thread
        self.save_thread.start()
        print("Background save process started. Program can now exit.")
        # Optional: display message via UI

    # --- Helper Methods (Unchanged) ---
    # ... (find_student_by_id, find_course_by_id, get_student_ids, get_course_ids) ...
    def find_student_by_id(self, student_id):
        for student in self.students:
            if student.id == student_id:
                return student
        return None

    def find_course_by_id(self, course_id):
        for course in self.courses:
            if course.id == course_id:
                return course
        return None

    def get_student_ids(self):
         return {s.id for s in self.students}

    def get_course_ids(self):
         return {c.id for c in self.courses}

    # --- Data Manipulation Methods (Unchanged from pw6) ---
    # ... (add_student, add_course, add_mark) ...
    def add_student(self, student_id, name, dob):
        if not self.find_student_by_id(student_id):
             self.students.append(Student(student_id, name, dob))
             self._invalidate_gpas()
             return True
        return False

    def add_course(self, course_id, name, credits):
         if not self.find_course_by_id(course_id):
              self.courses.append(Course(course_id, name, credits))
              self._invalidate_gpas()
              return True
         return False

    def add_mark(self, course_id, student_id, mark):
         if course_id not in self.marks:
              self.marks[course_id] = {}
         self.marks[course_id][student_id] = mark
         self._invalidate_gpas()

    # --- GPA and Sorting (Unchanged) ---
    # ... (_invalidate_gpas, calculate_student_gpa, calculate_all_gpas, get_sorted_students_by_gpa) ...
    def _invalidate_gpas(self):
         for student in self.students:
              student.gpa = None

    def calculate_student_gpa(self, student_id):
        student = self.find_student_by_id(student_id)
        if not student: return 0.0 # Or None
        student_marks_values = []; corresponding_credits = []
        for course_id, marks_dict in self.marks.items():
            if student_id in marks_dict:
                course = self.find_course_by_id(course_id)
                if course:
                    student_marks_values.append(marks_dict[student_id])
                    corresponding_credits.append(course.credits)
        if not student_marks_values: student.gpa = 0.0; return 0.0
        marks_arr = np.array(student_marks_values); credits_arr = np.array(corresponding_credits)
        total_credits = np.sum(credits_arr)
        if total_credits == 0: student.gpa = 0.0; return 0.0
        gpa = np.sum(marks_arr * credits_arr) / total_credits; student.gpa = gpa; return gpa

    def calculate_all_gpas(self):
         if not self.students: return
         for student in self.students: self.calculate_student_gpa(student.id)

    def get_sorted_students_by_gpa(self):
         self.calculate_all_gpas()
         return sorted(self.students, key=lambda s: s.gpa if s.gpa is not None else -1, reverse=True)

    # --- Curses Interaction Methods (Unchanged from pw6) ---
    # ... (run_input_students, run_input_courses, run_input_marks - they no longer call save directly) ...
    def run_input_students(self, stdscr):
        # ... (keep existing input loop logic from pw6/main.py) ...
        num_students_str = ui.get_input(stdscr, "Enter number of students: ", 2, 1)
        num_students = data_input.validate_positive_integer(num_students_str)
        if num_students is None: ui.display_message(stdscr, "Invalid number. Press key.", wait=True, color_pair=2); return
        existing_ids = self.get_student_ids(); added_count = 0
        for i in range(num_students):
             while True: # Loop for getting valid details for one student
                stdscr.clear(); ui.display_message(stdscr, f"Enter details for student {i+1}/{num_students}", y_offset=8)
                s_id = ui.get_input(stdscr, "  Student ID: ", 3, 1)
                is_valid_id, id_err = data_input.validate_student_id(s_id, existing_ids)
                if not is_valid_id: ui.display_message(stdscr, id_err + " Press any key.", wait=True, color_pair=2); continue
                s_name = ui.get_input(stdscr, "  Student Name: ", 4, 1)
                if not s_name: ui.display_message(stdscr, "Name cannot be empty. Press key.", wait=True, color_pair=2); continue
                s_dob = ui.get_input(stdscr, "  Student DoB (dd/mm/yyyy): ", 5, 1)
                if not s_dob: ui.display_message(stdscr, "DoB cannot be empty. Press key.", wait=True, color_pair=2); continue
                if self.add_student(s_id, s_name, s_dob): existing_ids.add(s_id); added_count += 1
                else: ui.display_message(stdscr, f"Failed to add student {s_id}. Might already exist.", wait=True, color_pair=2)
                break # Move to next student
        if added_count > 0: ui.display_message(stdscr, f"{added_count} student(s) added. Data will be saved on exit.", wait=True)

    def run_input_courses(self, stdscr):
        # ... (keep existing input loop logic from pw6/main.py) ...
        num_courses_str = ui.get_input(stdscr, "Enter number of courses: ", 2, 1)
        num_courses = data_input.validate_positive_integer(num_courses_str)
        if num_courses is None: ui.display_message(stdscr, "Invalid number. Press key.", wait=True, color_pair=2); return
        existing_ids = self.get_course_ids(); added_count = 0
        for i in range(num_courses):
            while True: # Loop for getting valid details for one course
                stdscr.clear(); ui.display_message(stdscr, f"Enter details for course {i+1}/{num_courses}", y_offset=8)
                c_id = ui.get_input(stdscr, "  Course ID: ", 3, 1)
                is_valid_id, id_err = data_input.validate_course_id(c_id, existing_ids)
                if not is_valid_id: ui.display_message(stdscr, id_err + " Press any key.", wait=True, color_pair=2); continue
                c_name = ui.get_input(stdscr, "  Course Name: ", 4, 1)
                if not c_name: ui.display_message(stdscr, "Name cannot be empty. Press key.", wait=True, color_pair=2); continue
                c_credits_str = ui.get_input(stdscr, "  Course Credits: ", 5, 1)
                c_credits = data_input.validate_credits(c_credits_str)
                if c_credits is None: ui.display_message(stdscr, "Invalid credits (must be positive integer). Press key.", wait=True, color_pair=2); continue
                if self.add_course(c_id, c_name, c_credits): existing_ids.add(c_id); added_count += 1
                else: ui.display_message(stdscr, f"Failed to add course {c_id}. Might already exist.", wait=True, color_pair=2)
                break # Move to next course
        if added_count > 0: ui.display_message(stdscr, f"{added_count} course(s) added. Data will be saved on exit.", wait=True)

    def run_input_marks(self, stdscr):
         # ... (keep existing logic from pw6/main.py) ...
         selected_course = ui.select_item(stdscr, self.courses, "Course", lambda c: c.get_display_info())
         if selected_course is None: return
         if not self.students: ui.display_message(stdscr, "No students available. Press key.", wait=True, color_pair=2); return
         stdscr.clear(); h, w = stdscr.getmaxyx()
         title = f"--- Input Marks for {selected_course.name} ({selected_course.id}) ---"
         ui.display_message(stdscr, title, y_offset=len(self.students) + 5 if len(self.students) + 5 < h else 3)
         y_pos = 2; marks_entered = False
         for student in self.students:
              while True:
                   prompt = f"  Mark for {student.name} ({student.id}): "
                   stdscr.move(y_pos, 1); stdscr.clrtoeol()
                   mark_str = ui.get_input(stdscr, prompt, y_pos, 1)
                   mark, err_msg = data_input.validate_mark(mark_str)
                   if err_msg: ui.display_message(stdscr, err_msg + " Try again.", y_offset=1, color_pair=2, wait=False)
                   else:
                       self.add_mark(selected_course.id, student.id, mark); marks_entered = True
                       stdscr.move(h - 1, 1); stdscr.clrtoeol(); y_pos += 1; break
              if y_pos >= h - 2: ui.display_message(stdscr, "Screen full... Press key.", wait=True); stdscr.clear(); ui.display_message(stdscr, title, y_offset=5); y_pos = 2
         if marks_entered: ui.display_message(stdscr, f"Marks input complete for {selected_course.id}. Data will be saved on exit.", wait=True)
         else: ui.display_message(stdscr, f"No marks entered for {selected_course.id}. Press key.", wait=True)


    # --- Main Application Loop using Curses ---
    # Modified exit logic
    def main(self, stdscr):
        # Curses setup
        curses.curs_set(0); curses.noecho(); stdscr.keypad(True)
        curses.start_color(); curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK); curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)

        # --- LOAD DATA AT START ( Happens in __init__ ) ---
        if not self.students or not self.courses:
             ui.display_message(stdscr,"No data loaded. Consider inputting initial students and courses.", wait=True, color_pair=3)

        # Menu definition (Update Exit option text if needed)
        menu_options = [
            "1. Input Students", "2. Input Courses", "3. Input Marks for a Course",
            "4. List All Students", "5. List All Courses", "6. Show Mark Sheet for a Course",
            "7. List Students Sorted by GPA", "0. Save & Exit (Background)"
        ]
        current_row = 0

        while True:
            ui.display_menu(stdscr, menu_options, current_row)
            key = stdscr.getch()

            if key == curses.KEY_UP and current_row > 0: current_row -= 1
            elif key == curses.KEY_DOWN and current_row < len(menu_options) - 1: current_row += 1
            elif key == curses.KEY_ENTER or key in [10, 13]:
                action_row = current_row

                # --- Menu actions 1-7 remain the same ---
                if action_row == 0: self.run_input_students(stdscr)
                elif action_row == 1: self.run_input_courses(stdscr)
                elif action_row == 2: self.run_input_marks(stdscr)
                elif action_row == 3: # List Students
                     self.calculate_all_gpas()
                     ui.display_list(stdscr, "Student List", f"{'ID':<10} {'Name':<25} {'DoB':<15} {'GPA':<5}", self.students, lambda s: s.get_display_info(show_gpa=True))
                elif action_row == 4: # List Courses
                     ui.display_list(stdscr, "Course List", f"{'ID':<10} {'Name':<25} {'Credits':<8}", self.courses, lambda c: c.get_display_info())
                elif action_row == 5: # Show Mark Sheet
                      selected_course = ui.select_item(stdscr, self.courses, "Course", lambda c: c.get_display_info())
                      if selected_course: ui.display_marks_table(stdscr, selected_course, self.students, self.marks)
                elif action_row == 6: # List Sorted Students
                      sorted_students = self.get_sorted_students_by_gpa()
                      ui.display_list(stdscr, "Students Sorted by GPA", f"{'ID':<10} {'Name':<25} {'DoB':<15} {'GPA':<5}", sorted_students, lambda s: s.get_display_info(show_gpa=True))

                # --- NEW EXIT LOGIC ---
                elif action_row == len(menu_options) - 1: # Exit
                    # Initiate save in background thread
                    self.save_in_background()
                    # Display message and exit main thread
                    # Note: Curses screen needs to be cleaned up by wrapper.
                    # We might need a slight delay for the user to see the message.
                    ui.display_message(stdscr, "Save initiated in background. Exiting...", wait=False)
                    stdscr.refresh()
                    time.sleep(2.0) # Give user time to see message & save thread to start
                    break # Exit the while loop (curses wrapper will handle cleanup)

        # This part is reached after the loop breaks
        # Final message might be tricky if curses cleans up immediately.
        # The 'Exiting' message is shown just before break now.

# --- Script Execution ---
if __name__ == "__main__":
    # ... (Dependency checks remain the same) ...
    try: import numpy; import curses; import curses.panel
    except ImportError as e: print(f"Dependency Error: {e}"); sys.exit(1)

    app = Application()
    curses.wrapper(app.main)
    # After wrapper finishes (program exits), Python might wait for non-daemon threads.
    # Since our save thread IS a daemon, Python should exit promptly.
    print("\nMain program finished.") # This might print after curses screen closes