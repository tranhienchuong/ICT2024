# pw5/main.py
import curses
import sys
import time # For delays if needed
import math # For input validation needing math.floor
import numpy as np
import os       # Needed for file operations (exists, remove)
import zipfile  # Needed for compression/decompression

# Import classes and functions from our modules
from .domains import Student, Course # Relative imports are correct
from . import input as data_input
from . import output as ui

# --- Constants for filenames ---
STUDENTS_FILE = "students.txt"
COURSES_FILE = "courses.txt"
MARKS_FILE = "marks.txt"
ARCHIVE_FILE = "students.dat"
# --- Delimiter for text files ---
DELIMITER = ";" # Using semicolon as CSV doesn't handle commas in names well easily

class Application:
    def __init__(self):
        self.students = []
        self.courses = []
        self.marks = {} # {course_id: {student_id: mark}}
        # Attempt to load data when the application starts
        self._decompress_and_load_data()

    # --- Data Persistence Methods ---

    def _save_students_to_txt(self):
        """Saves the current student list to students.txt"""
        try:
            with open(STUDENTS_FILE, "w", encoding="utf-8") as f:
                for student in self.students:
                    # Use student attributes directly
                    line = f"{student.id}{DELIMITER}{student.name}{DELIMITER}{student.dob}\n"
                    f.write(line)
            # Optional: display success message via curses UI
            # ui.display_message(stdscr, "Students saved to students.txt", wait=True) # Needs stdscr passed
        except IOError as e:
            # Optional: display error message via curses UI
            # ui.display_message(stdscr, f"Error saving students: {e}", color_pair=2, wait=True)
            print(f"Error saving students: {e}") # Fallback print

    def _save_courses_to_txt(self):
        """Saves the current course list to courses.txt"""
        try:
            with open(COURSES_FILE, "w", encoding="utf-8") as f:
                for course in self.courses:
                    line = f"{course.id}{DELIMITER}{course.name}{DELIMITER}{course.credits}\n"
                    f.write(line)
        except IOError as e:
            print(f"Error saving courses: {e}")

    def _save_marks_to_txt(self):
        """Saves the current marks dictionary to marks.txt"""
        # Overwrites the file each time - simpler for loading
        try:
            with open(MARKS_FILE, "w", encoding="utf-8") as f:
                for course_id, student_marks in self.marks.items():
                    for student_id, mark in student_marks.items():
                        line = f"{course_id}{DELIMITER}{student_id}{DELIMITER}{mark}\n"
                        f.write(line)
        except IOError as e:
            print(f"Error saving marks: {e}")

    def _load_students_from_txt(self):
        """Loads student data from students.txt"""
        try:
            if not os.path.exists(STUDENTS_FILE):
                return # File doesn't exist, nothing to load
            with open(STUDENTS_FILE, "r", encoding="utf-8") as f:
                self.students = [] # Clear existing list before loading
                for line in f:
                    line = line.strip()
                    if line:
                        parts = line.split(DELIMITER)
                        if len(parts) == 3:
                            student_id, name, dob = parts
                            # Avoid duplicates if loading multiple times (though we clear list first)
                            if not any(s.id == student_id for s in self.students):
                                self.students.append(Student(student_id, name, dob))
                        else:
                             print(f"Warning: Skipping malformed line in {STUDENTS_FILE}: {line}")
        except IOError as e:
            print(f"Error loading students: {e}")
        except Exception as e:
            print(f"Error processing {STUDENTS_FILE}: {e}")


    def _load_courses_from_txt(self):
        """Loads course data from courses.txt"""
        try:
            if not os.path.exists(COURSES_FILE):
                return
            with open(COURSES_FILE, "r", encoding="utf-8") as f:
                 self.courses = [] # Clear existing list
                 for line in f:
                     line = line.strip()
                     if line:
                         parts = line.split(DELIMITER)
                         if len(parts) == 3:
                             course_id, name, credits_str = parts
                             if not any(c.id == course_id for c in self.courses):
                                 # Let Course constructor handle credit validation
                                 self.courses.append(Course(course_id, name, credits_str))
                         else:
                             print(f"Warning: Skipping malformed line in {COURSES_FILE}: {line}")
        except IOError as e:
            print(f"Error loading courses: {e}")
        except Exception as e:
            print(f"Error processing {COURSES_FILE}: {e}")


    def _load_marks_from_txt(self):
        """Loads marks data from marks.txt"""
        try:
            if not os.path.exists(MARKS_FILE):
                return
            with open(MARKS_FILE, "r", encoding="utf-8") as f:
                 self.marks = {} # Clear existing marks
                 for line in f:
                     line = line.strip()
                     if line:
                         parts = line.split(DELIMITER)
                         if len(parts) == 3:
                             course_id, student_id, mark_str = parts
                             try:
                                 mark = float(mark_str)
                                 if course_id not in self.marks:
                                     self.marks[course_id] = {}
                                 self.marks[course_id][student_id] = mark
                             except ValueError:
                                 print(f"Warning: Skipping invalid mark in {MARKS_FILE}: {line}")
                         else:
                             print(f"Warning: Skipping malformed line in {MARKS_FILE}: {line}")
        except IOError as e:
            print(f"Error loading marks: {e}")
        except Exception as e:
            print(f"Error processing {MARKS_FILE}: {e}")


    def _compress_data(self, stdscr=None):
        """Compresses the data files into students.dat using zip."""
        files_to_compress = [STUDENTS_FILE, COURSES_FILE, MARKS_FILE]
        # Optional: Check if files exist before trying to compress
        existing_files = [f for f in files_to_compress if os.path.exists(f)]

        if not existing_files:
             if stdscr: ui.display_message(stdscr, "No data files found to compress.", color_pair=3, wait=True)
             else: print("No data files found to compress.")
             return

        try:
            # Display message in curses if stdscr provided
            if stdscr: ui.display_message(stdscr, f"Compressing data to {ARCHIVE_FILE}...", wait=False)

            with zipfile.ZipFile(ARCHIVE_FILE, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
                for file in existing_files:
                    zipf.write(file, arcname=os.path.basename(file)) # Use basename to avoid storing full path

            # Optional: Remove the original .txt files after successful compression
            # for file in existing_files:
            #     os.remove(file)

            if stdscr: ui.display_message(stdscr, "Data compressed successfully. Press key.", wait=True) # Update message
            else: print("Data compressed successfully.")

        except zipfile.BadZipFile:
            if stdscr: ui.display_message(stdscr, f"Error: Failed creating zip file {ARCHIVE_FILE}.", color_pair=2, wait=True)
            else: print(f"Error: Failed creating zip file {ARCHIVE_FILE}.")
        except IOError as e:
             if stdscr: ui.display_message(stdscr, f"Error during compression I/O: {e}", color_pair=2, wait=True)
             else: print(f"Error during compression I/O: {e}")
        except Exception as e:
             if stdscr: ui.display_message(stdscr, f"An unexpected error occurred during compression: {e}", color_pair=2, wait=True)
             else: print(f"An unexpected error occurred during compression: {e}")


    def _decompress_and_load_data(self, stdscr=None):
        """Checks for students.dat, decompresses, and loads data."""
        if os.path.exists(ARCHIVE_FILE):
            try:
                if stdscr: ui.display_message(stdscr, f"Found {ARCHIVE_FILE}. Decompressing...", wait=False)
                else: print(f"Found {ARCHIVE_FILE}. Decompressing...")

                with zipfile.ZipFile(ARCHIVE_FILE, 'r') as zipf:
                    zipf.extractall() # Extract all files to current directory

                if stdscr: ui.display_message(stdscr, "Decompression complete. Loading data...", wait=False)
                else: print("Decompression complete. Loading data...")

                # Load data from extracted files
                self._load_students_from_txt()
                self._load_courses_from_txt()
                self._load_marks_from_txt()

                if stdscr: ui.display_message(stdscr, "Data loaded successfully. Press key.", wait=True)
                else: print("Data loaded successfully.")

            except zipfile.BadZipFile:
                if stdscr: ui.display_message(stdscr, f"Error: {ARCHIVE_FILE} is corrupted or not a zip file.", color_pair=2, wait=True)
                else: print(f"Error: {ARCHIVE_FILE} is corrupted or not a zip file.")
            except FileNotFoundError as e:
                 # This might happen if a file listed inside zip doesn't extract correctly
                 if stdscr: ui.display_message(stdscr, f"Error extracting file: {e}", color_pair=2, wait=True)
                 else: print(f"Error extracting file: {e}")
            except IOError as e:
                 if stdscr: ui.display_message(stdscr, f"Error during decompression I/O: {e}", color_pair=2, wait=True)
                 else: print(f"Error during decompression I/O: {e}")
            except Exception as e:
                 if stdscr: ui.display_message(stdscr, f"An unexpected error occurred during decompression/loading: {e}", color_pair=2, wait=True)
                 else: print(f"An unexpected error occurred during decompression/loading: {e}")

        else:
             if stdscr: ui.display_message(stdscr, f"{ARCHIVE_FILE} not found. Starting fresh.", color_pair=3, wait=True)
             else: print(f"{ARCHIVE_FILE} not found. Starting fresh.")


    # --- Helper Methods (Keep existing ones like find_*, get_*_ids) ---
    def find_student_by_id(self, student_id):
        # ... (keep existing code) ...
        for student in self.students:
            if student.id == student_id:
                return student
        return None

    def find_course_by_id(self, course_id):
        # ... (keep existing code) ...
        for course in self.courses:
            if course.id == course_id:
                return course
        return None

    def get_student_ids(self):
         return {s.id for s in self.students}

    def get_course_ids(self):
         return {c.id for c in self.courses}

    # --- Data Manipulation Methods (Keep existing add_*, calculate_*, etc.) ---
    def add_student(self, student_id, name, dob):
        # ... (keep existing code, maybe call save?) ...
        if not self.find_student_by_id(student_id):
             self.students.append(Student(student_id, name, dob))
             self._invalidate_gpas() # Invalidate GPAs when student list changes
             # Decide if save should happen here or after bulk input
             # self._save_students_to_txt() # SAVING HERE MIGHT BE INEFFICIENT
             return True
        return False

    def add_course(self, course_id, name, credits):
         # ... (keep existing code, maybe call save?) ...
         if not self.find_course_by_id(course_id):
              self.courses.append(Course(course_id, name, credits))
              self._invalidate_gpas()
              # self._save_courses_to_txt() # SAVING HERE MIGHT BE INEFFICIENT
              return True
         return False

    def add_mark(self, course_id, student_id, mark):
         # ... (keep existing code, maybe call save?) ...
         if course_id not in self.marks:
              self.marks[course_id] = {}
         self.marks[course_id][student_id] = mark
         self._invalidate_gpas() # Marks changed, GPAs need recalculation
         # Save happens after *all* marks for a course are input

    # --- GPA and Sorting (Keep existing methods) ---
    def _invalidate_gpas(self):
         # ... (keep existing code) ...
         for student in self.students:
              student.gpa = None

    def calculate_student_gpa(self, student_id):
        # ... (keep existing code) ...
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
         # ... (keep existing code) ...
         if not self.students: return
         for student in self.students:
             self.calculate_student_gpa(student.id)

    def get_sorted_students_by_gpa(self):
         # ... (keep existing code) ...
         self.calculate_all_gpas()
         return sorted(self.students, key=lambda s: s.gpa if s.gpa is not None else -1, reverse=True)

    # --- Curses Interaction Methods ---
    # Modify these to call save methods *after* the input loops finish

    def run_input_students(self, stdscr):
        # ... (keep existing input loop logic from pw4/main.py) ...
        # ... this loop collects student details and calls self.add_student ...
        print("\n--- Input Student Information ---") # Placeholder if curses fails
        num_students_str = ui.get_input(stdscr, "Enter number of students: ", 2, 1)
        num_students = data_input.validate_positive_integer(num_students_str)

        if num_students is None:
            ui.display_message(stdscr, "Invalid number. Press any key.", wait=True, color_pair=2)
            return

        existing_ids = self.get_student_ids()
        added_count = 0
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
                if self.add_student(s_id, s_name, s_dob):
                     existing_ids.add(s_id) # Update existing IDs for next check
                     added_count += 1
                     # ui.display_message(stdscr, f"Student {s_id} added.", wait=True, color_pair=1) # Message per student might be too much
                else:
                     # Should not happen if validate_student_id worked, but safety check
                      ui.display_message(stdscr, f"Failed to add student {s_id}. Might already exist.", wait=True, color_pair=2)
                break # Move to next student
        # --- Save AFTER the loop ---
        if added_count > 0:
             self._save_students_to_txt()
             ui.display_message(stdscr, f"{added_count} student(s) added and saved. Press key.", wait=True)
        else:
             ui.display_message(stdscr, "No new students added. Press key.", wait=True)


    def run_input_courses(self, stdscr):
        # ... (keep existing input loop logic from pw4/main.py) ...
        # ... this loop collects course details and calls self.add_course ...
        print("\n--- Input Course Information ---") # Placeholder
        num_courses_str = ui.get_input(stdscr, "Enter number of courses: ", 2, 1)
        num_courses = data_input.validate_positive_integer(num_courses_str)

        if num_courses is None:
            ui.display_message(stdscr, "Invalid number. Press any key.", wait=True, color_pair=2)
            return

        existing_ids = self.get_course_ids()
        added_count = 0
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
                if self.add_course(c_id, c_name, c_credits):
                    existing_ids.add(c_id)
                    added_count += 1
                else:
                     ui.display_message(stdscr, f"Failed to add course {c_id}. Might already exist.", wait=True, color_pair=2)
                break # Move to next course
        # --- Save AFTER the loop ---
        if added_count > 0:
            self._save_courses_to_txt()
            ui.display_message(stdscr, f"{added_count} course(s) added and saved. Press key.", wait=True)
        else:
             ui.display_message(stdscr, "No new courses added. Press key.", wait=True)


    def run_input_marks(self, stdscr):
         # ... (keep existing logic to select course and input marks) ...
         # ... this loop calls self.add_mark for each student...
         selected_course = ui.select_item(stdscr, self.courses, "Course", lambda c: c.get_display_info())
         if selected_course is None:
              return # User cancelled or no courses

         if not self.students:
             ui.display_message(stdscr, "No students available to input marks for. Press key.", wait=True, color_pair=2)
             return

         stdscr.clear()
         title = f"--- Input Marks for {selected_course.name} ({selected_course.id}) ---"
         # Use h, w = stdscr.getmaxyx() for better positioning
         h, w = stdscr.getmaxyx()
         ui.display_message(stdscr, title, y_offset=len(self.students) + 5 if len(self.students) + 5 < h else 3) # Adjust position

         y_pos = 2 # Start displaying prompts from row 2
         marks_entered = False
         for student in self.students:
              while True:
                   prompt = f"  Mark for {student.name} ({student.id}): "
                   # Clear previous input line before asking again
                   stdscr.move(y_pos, 1)
                   stdscr.clrtoeol()
                   mark_str = ui.get_input(stdscr, prompt, y_pos, 1)
                   mark, err_msg = data_input.validate_mark(mark_str) # Uses rounding down

                   if err_msg:
                       # Display error message near the bottom, temporarily
                       ui.display_message(stdscr, err_msg + " Try again.", y_offset=1, color_pair=2, wait=False)
                       # No 'wait=True' so it disappears on next loop/refresh
                   else:
                       self.add_mark(selected_course.id, student.id, mark)
                       marks_entered = True
                       # Clear potential old error message line before moving cursor
                       stdscr.move(h - 1, 1) # Assuming msg displayed at h-1
                       stdscr.clrtoeol()
                       y_pos += 1 # Move to next line for next student
                       break # Valid mark entered, move to next student

              if y_pos >= h - 2: # Avoid writing off screen (leave space for messages)
                  ui.display_message(stdscr, "Screen full, scrolling required (not implemented)... Press key to continue anyway.", wait=True)
                  stdscr.clear() # Basic clear for now
                  # Re-display title or context if needed after clearing
                  ui.display_message(stdscr, title, y_offset=5)
                  y_pos = 2 # Reset position after clearing

         # --- Save AFTER the loop ---
         if marks_entered:
             self._save_marks_to_txt() # Overwrites marks file with current state
             ui.display_message(stdscr, f"Marks input complete for {selected_course.id} and saved. Press key.", wait=True)
         else:
              ui.display_message(stdscr, f"No marks were entered for {selected_course.id}. Press key.", wait=True)


    # --- Main Application Loop using Curses ---
    # Modify start and exit
    def main(self, stdscr):
        # Curses setup (keep existing)
        curses.curs_set(0)
        curses.noecho()
        stdscr.keypad(True)
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)

        # --- LOAD DATA AT START ---
        # Pass stdscr so loading messages can be displayed
        self._decompress_and_load_data(stdscr)
        # If loading failed or no archive, might need initial input?
        # The current design relies on loading or starting fresh.
        # We could force initial input if lists are empty after loading attempt.
        if not self.students or not self.courses:
             ui.display_message(stdscr,"No data loaded. Please input initial students and courses.", wait=True, color_pair=3)
             # Consider calling input methods directly here or rely on user menu choice
             # Forcing it might be better for first run:
             if not self.students: self.run_input_students(stdscr)
             if not self.courses: self.run_input_courses(stdscr)


        # Menu definition (keep existing)
        menu_options = [
            "1. Input Students", # Add options to ADD more later maybe?
            "2. Input Courses",
            "3. Input Marks for a Course",
            "4. List All Students",
            "5. List All Courses",
            "6. Show Mark Sheet for a Course",
            "7. List Students Sorted by GPA",
            "0. Save, Compress & Exit" # Modified Exit
        ]
        current_row = 0

        while True:
            # Update menu based on new options
            ui.display_menu(stdscr, menu_options, current_row)
            key = stdscr.getch()

            if key == curses.KEY_UP and current_row > 0:
                current_row -= 1
            elif key == curses.KEY_DOWN and current_row < len(menu_options) - 1:
                current_row += 1
            elif key == curses.KEY_ENTER or key in [10, 13]:
                action_row = current_row # Store selected row

                # --- Perform action based on menu choice ---
                if action_row == 0: self.run_input_students(stdscr)
                elif action_row == 1: self.run_input_courses(stdscr)
                elif action_row == 2: self.run_input_marks(stdscr)
                elif action_row == 3: # List Students
                     self.calculate_all_gpas()
                     ui.display_list(stdscr, "Student List",
                                     f"{'ID':<10} {'Name':<25} {'DoB':<15} {'GPA':<5}",
                                     self.students,
                                     lambda s: s.get_display_info(show_gpa=True))
                elif action_row == 4: # List Courses
                     ui.display_list(stdscr, "Course List",
                                     f"{'ID':<10} {'Name':<25} {'Credits':<8}",
                                     self.courses,
                                     lambda c: c.get_display_info())
                elif action_row == 5: # Show Mark Sheet
                      selected_course = ui.select_item(stdscr, self.courses, "Course", lambda c: c.get_display_info())
                      if selected_course:
                           ui.display_marks_table(stdscr, selected_course, self.students, self.marks)
                elif action_row == 6: # List Sorted Students
                      sorted_students = self.get_sorted_students_by_gpa()
                      ui.display_list(stdscr, "Students Sorted by GPA",
                                     f"{'ID':<10} {'Name':<25} {'DoB':<15} {'GPA':<5}",
                                     sorted_students,
                                     lambda s: s.get_display_info(show_gpa=True))

                # --- EXIT LOGIC ---
                elif action_row == len(menu_options) - 1: # Exit
                    ui.display_message(stdscr, "Saving data before exiting...", wait=False)
                    self._save_students_to_txt()
                    self._save_courses_to_txt()
                    self._save_marks_to_txt()
                    # Pass stdscr so compress can show messages
                    self._compress_data(stdscr)
                    # Short delay before final exit message
                    time.sleep(0.5)
                    break # Exit the while loop

        # Final message before curses cleanup (wrapper handles cleanup)
        stdscr.clear()
        ui.display_message(stdscr, "Exiting program. Goodbye!", y_offset=3, wait=True)
        time.sleep(1) # Ensure user sees final message


# --- Script Execution ---
if __name__ == "__main__":
    # Keep dependency checks
    try:
        import numpy
        import curses
        if sys.platform == "win32":
             import curses.panel
    except ImportError as e:
        print(f"Error: Missing required library - {e}")
        # ... (print install instructions) ...
        sys.exit(1)

    app = Application()
    curses.wrapper(app.main) # Wrapper handles setup/cleanup