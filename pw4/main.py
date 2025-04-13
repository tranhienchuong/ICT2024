# Add these lines at the top of C:\pw4\main.py
import sys
import os
print("--- Running main.py ---")
print(f"CWD in main.py: {os.getcwd()}") # See CWD when running with -m
print("sys.path in main.py:")
for p in sys.path: print(f"  {p}")      # See Python's path when running with -m
print("--- End path debug ---\n")
# Original imports should follow below this block
# import curses
# import ...

# pw4/main.py
import curses
import sys
import time # For delays if needed
import math # For input validation needing math.floor
import numpy as np

# Import classes and functions from our modules
from .domains import Student, Course
from . import input as data_input # Alias to avoid conflicts with built-in input
from . import output as ui # Alias for clarity

class Application:
    def __init__(self):
        self.students = []
        self.courses = []
        self.marks = {} # {course_id: {student_id: mark}}

    # --- Data Manipulation Methods ---
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

    def add_student(self, student_id, name, dob):
        # Basic check here, though primary validation might happen during input phase
        if not self.find_student_by_id(student_id):
             self.students.append(Student(student_id, name, dob))
             self._invalidate_gpas() # Invalidate GPAs when student list changes
             return True
        return False

    def add_course(self, course_id, name, credits):
         if not self.find_course_by_id(course_id):
              self.courses.append(Course(course_id, name, credits))
              self._invalidate_gpas() # Invalidate if course credits change logic applied
              return True
         return False

    def add_mark(self, course_id, student_id, mark):
         if course_id not in self.marks:
              self.marks[course_id] = {}
         self.marks[course_id][student_id] = mark
         self._invalidate_gpas() # Marks changed, GPAs need recalculation

    def get_student_ids(self):
         return {s.id for s in self.students}

    def get_course_ids(self):
         return {c.id for c in self.courses}

    # --- GPA and Sorting ---
    def _invalidate_gpas(self):
         for student in self.students:
              student.gpa = None

    def calculate_student_gpa(self, student_id):
        student = self.find_student_by_id(student_id)
        if not student: return 0.0 # Or None

        student_marks_values = []
        corresponding_credits = []

        for course_id, marks_dict in self.marks.items():
            if student_id in marks_dict:
                course = self.find_course_by_id(course_id)
                if course:
                    student_marks_values.append(marks_dict[student_id])
                    corresponding_credits.append(course.credits)

        if not student_marks_values:
            student.gpa = 0.0
            return 0.0

        marks_arr = np.array(student_marks_values)
        credits_arr = np.array(corresponding_credits)
        total_credits = np.sum(credits_arr)

        if total_credits == 0:
            student.gpa = 0.0
            return 0.0

        gpa = np.sum(marks_arr * credits_arr) / total_credits
        student.gpa = gpa
        return gpa

    def calculate_all_gpas(self):
         if not self.students: return
         for student in self.students:
             self.calculate_student_gpa(student.id)

    def get_sorted_students_by_gpa(self):
         self.calculate_all_gpas()
         # Return a new sorted list, doesn't modify internal list directly unless intended
         return sorted(self.students, key=lambda s: s.gpa if s.gpa is not None else -1, reverse=True)


    # --- Curses Interaction Methods ---
    # These methods coordinate between getting input and displaying output via the ui module

    def run_input_students(self, stdscr):
        ui.display_message(stdscr, "--- Input Student Information ---", y_offset=5)
        num_students_str = ui.get_input(stdscr, "Enter number of students: ", 2, 1)
        num_students = data_input.validate_positive_integer(num_students_str)

        if num_students is None:
            ui.display_message(stdscr, "Invalid number. Press any key.", wait=True, color_pair=2)
            return

        existing_ids = self.get_student_ids()
        for i in range(num_students):
            while True: # Loop for getting valid details for one student
                stdscr.clear() # Clear screen for each student input
                ui.display_message(stdscr, f"Enter details for student {i+1}/{num_students}", y_offset=8)
                s_id = ui.get_input(stdscr, "  Student ID: ", 3, 1)
                is_valid_id, id_err = data_input.validate_student_id(s_id, existing_ids)
                if not is_valid_id:
                     ui.display_message(stdscr, id_err + " Press any key.", wait=True, color_pair=2)
                     continue # Ask for ID again

                s_name = ui.get_input(stdscr, "  Student Name: ", 4, 1)
                if not s_name: # Basic check
                    ui.display_message(stdscr, "Name cannot be empty. Press any key.", wait=True, color_pair=2)
                    continue

                s_dob = ui.get_input(stdscr, "  Student DoB (dd/mm/yyyy): ", 5, 1)
                if not s_dob: # Basic check
                     ui.display_message(stdscr, "DoB cannot be empty. Press any key.", wait=True, color_pair=2)
                     continue

                # If all details seem okay
                self.add_student(s_id, s_name, s_dob)
                existing_ids.add(s_id) # Update existing IDs for next check
                ui.display_message(stdscr, f"Student {s_id} added.", wait=True, color_pair=1)
                break # Move to next student


    def run_input_courses(self, stdscr):
        ui.display_message(stdscr, "--- Input Course Information ---", y_offset=5)
        num_courses_str = ui.get_input(stdscr, "Enter number of courses: ", 2, 1)
        num_courses = data_input.validate_positive_integer(num_courses_str)

        if num_courses is None:
            ui.display_message(stdscr, "Invalid number. Press any key.", wait=True, color_pair=2)
            return

        existing_ids = self.get_course_ids()
        for i in range(num_courses):
            while True: # Loop for getting valid details for one course
                stdscr.clear()
                ui.display_message(stdscr, f"Enter details for course {i+1}/{num_courses}", y_offset=8)
                c_id = ui.get_input(stdscr, "  Course ID: ", 3, 1)
                is_valid_id, id_err = data_input.validate_course_id(c_id, existing_ids)
                if not is_valid_id:
                    ui.display_message(stdscr, id_err + " Press any key.", wait=True, color_pair=2)
                    continue

                c_name = ui.get_input(stdscr, "  Course Name: ", 4, 1)
                if not c_name:
                    ui.display_message(stdscr, "Name cannot be empty. Press any key.", wait=True, color_pair=2)
                    continue

                c_credits_str = ui.get_input(stdscr, "  Course Credits: ", 5, 1)
                c_credits = data_input.validate_credits(c_credits_str)
                if c_credits is None:
                     ui.display_message(stdscr, "Invalid credits (must be positive integer). Press key.", wait=True, color_pair=2)
                     continue

                # If all details okay
                self.add_course(c_id, c_name, c_credits)
                existing_ids.add(c_id)
                ui.display_message(stdscr, f"Course {c_id} added.", wait=True, color_pair=1)
                break # Move to next course


    def run_input_marks(self, stdscr):
         selected_course = ui.select_item(stdscr, self.courses, "Course", lambda c: c.get_display_info())
         if selected_course is None:
              return # User cancelled or no courses

         if not self.students:
             ui.display_message(stdscr, "No students available to input marks for. Press key.", wait=True, color_pair=2)
             return

         stdscr.clear()
         title = f"--- Input Marks for {selected_course.name} ({selected_course.id}) ---"
         ui.display_message(stdscr, title, y_offset=len(self.students) + 5) # Adjust position

         y_pos = 2 # Start displaying prompts from row 2
         for student in self.students:
              while True:
                   prompt = f"  Mark for {student.name} ({student.id}): "
                   # Clear previous input line before asking again
                   stdscr.move(y_pos, 1)
                   stdscr.clrtoeol()
                   mark_str = ui.get_input(stdscr, prompt, y_pos, 1)
                   mark, err_msg = data_input.validate_mark(mark_str)

                   if err_msg:
                       ui.display_message(stdscr, err_msg + " Try again.", y_offset=1, color_pair=2, wait=False)
                       # Clear the error message after a short delay? Or leave until valid input.
                   else:
                       self.add_mark(selected_course.id, student.id, mark)
                       # Optionally clear error message line here if needed
                       stdscr.move(h - 1, 1) # Assuming h is height from stdscr.getmaxyx() if available
                       stdscr.clrtoeol()
                       y_pos += 1 # Move to next line for next student
                       break # Valid mark entered, move to next student

              if y_pos >= stdscr.getmaxyx()[0] - 2: # Avoid writing off screen
                  ui.display_message(stdscr, "Screen full, continuing...", wait=True)
                  stdscr.clear() # Or implement scrolling/pagination
                  y_pos = 2 # Reset position after clearing

         ui.display_message(stdscr, f"Marks input complete for {selected_course.id}. Press key.", wait=True)


    # --- Main Application Loop using Curses ---
    def main(self, stdscr):
        # Curses setup
        curses.curs_set(0) # Hide cursor
        curses.noecho()
        stdscr.keypad(True) # Enable special keys (arrows, etc.)
        curses.start_color()
        # Define color pairs (background is often black by default)
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK) # Success/Info messages
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)   # Error messages
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Warnings/Prompts

        # Initial data entry (outside main menu loop for simplicity)
        # In a real app, these might also be menu options
        self.run_input_students(stdscr)
        self.run_input_courses(stdscr)


        # Menu definition
        menu_options = [
            "1. Input Marks for a Course",
            "2. List All Students",
            "3. List All Courses",
            "4. Show Mark Sheet for a Course",
            "5. List Students Sorted by GPA",
            "0. Exit Program"
        ]
        current_row = 0

        while True:
            ui.display_menu(stdscr, menu_options, current_row)
            key = stdscr.getch()

            if key == curses.KEY_UP and current_row > 0:
                current_row -= 1
            elif key == curses.KEY_DOWN and current_row < len(menu_options) - 1:
                current_row += 1
            elif key == curses.KEY_ENTER or key in [10, 13]: # Enter key
                # Determine action based on current_row
                if current_row == 0: # Input Marks
                     self.run_input_marks(stdscr)
                elif current_row == 1: # List Students
                     self.calculate_all_gpas() # Ensure GPAs are calculated
                     ui.display_list(stdscr, "Student List",
                                     f"{'ID':<10} {'Name':<25} {'DoB':<15} {'GPA':<5}",
                                     self.students,
                                     lambda s: s.get_display_info(show_gpa=True))
                elif current_row == 2: # List Courses
                     ui.display_list(stdscr, "Course List",
                                     f"{'ID':<10} {'Name':<25} {'Credits':<8}",
                                     self.courses,
                                     lambda c: c.get_display_info())
                elif current_row == 3: # Show Mark Sheet
                      selected_course = ui.select_item(stdscr, self.courses, "Course", lambda c: c.get_display_info())
                      if selected_course:
                           ui.display_marks_table(stdscr, selected_course, self.students, self.marks)
                elif current_row == 4: # List Sorted Students
                      sorted_students = self.get_sorted_students_by_gpa()
                      ui.display_list(stdscr, "Students Sorted by GPA",
                                     f"{'ID':<10} {'Name':<25} {'DoB':<15} {'GPA':<5}",
                                     sorted_students, # Display the sorted list
                                     lambda s: s.get_display_info(show_gpa=True))
                elif current_row == len(menu_options) - 1: # Exit
                    break # Exit the while loop

            # Optional: Handle ESC key globally to exit?
            # elif key == 27: # ESC key
            #    break

        # Wait briefly before exiting curses (optional)
        stdscr.clear()
        ui.display_message(stdscr, "Exiting...", y_offset=3, wait=True)


# --- Script Execution ---
if __name__ == "__main__":
    # Check dependencies
    try:
        import numpy
        import curses
        # Check for windows-curses if on Windows
        if sys.platform == "win32":
             import curses.panel # Test if windows-curses is functional
    except ImportError as e:
        print(f"Error: Missing required library - {e}")
        print("Please install required libraries:")
        print("  pip install numpy")
        if sys.platform == "win32":
             print("  pip install windows-curses")
        sys.exit(1)

    # Create application instance
    app = Application()
    # Start the curses application using the wrapper
    curses.wrapper(app.main)