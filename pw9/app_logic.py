# pw9/app_logic.py
import os
import sys
import pickle
import gzip
import threading
import copy
import numpy as np

# Assuming domains and input are in the same package level or accessible
# If running main.py directly, might need adjustment, but with -m should be fine
from .domains import Student, Course
from . import input as data_input # Keep validation logic separate

SAVE_FILE = "student_data.pkl.gz"

class AppLogic:
    def __init__(self):
        self.students = []
        self.courses = []
        self.marks = {} # {course_id: {student_id: mark}}
        self.save_thread = None
        self._load_data_pickle() # Load data on initialization

    def _load_data_pickle(self):
        """Loads application state from a gzipped pickle file."""
        load_success = False
        if os.path.exists(SAVE_FILE):
            try:
                print(f"Loading data from {SAVE_FILE}...") # Log to console
                with gzip.open(SAVE_FILE, 'rb') as f:
                    loaded_data = pickle.load(f)
                self.students = loaded_data.get('students', [])
                self.courses = loaded_data.get('courses', [])
                self.marks = loaded_data.get('marks', {})
                self._invalidate_gpas()
                print("Data loaded successfully.")
                load_success = True
            except Exception as e:
                 print(f"Error loading data: {e}. Starting fresh.", file=sys.stderr)
                 # If loading fails, ensure we start with empty lists/dict
                 self.students, self.courses, self.marks = [], [], {}
        else:
             print(f"Save file {SAVE_FILE} not found. Starting fresh.")
        return load_success # Indicate if load was successful

    def _save_thread_target(self, data_to_save):
        """This function runs in the background thread to save data."""
        thread_name = threading.current_thread().name
        print(f"\n[{thread_name}] Starting background save to {SAVE_FILE}...")
        try:
            with gzip.open(SAVE_FILE, 'wb') as f:
                pickle.dump(data_to_save, f, pickle.HIGHEST_PROTOCOL)
            print(f"[{thread_name}] Background save completed.")
        except Exception as e:
            print(f"\n[{thread_name}] ERROR during background save: {e}", file=sys.stderr)

    def save_in_background(self):
        """Initiates the saving process in a background daemon thread."""
        if self.save_thread and self.save_thread.is_alive():
            print("Note: Previous save operation still in progress.")
            return False # Indicate save didn't start

        print("\nInitiating background save...")
        try:
             data_copy = {
                 'students': copy.deepcopy(self.students),
                 'courses': copy.deepcopy(self.courses),
                 'marks': copy.deepcopy(self.marks)
             }
        except Exception as e:
             print(f"\nError creating deep copy for saving: {e}", file=sys.stderr)
             return False # Indicate save didn't start

        self.save_thread = threading.Thread(
            target=self._save_thread_target, args=(data_copy,),
            name="SaveThread", daemon=True
        )
        self.save_thread.start()
        print("Background save process started.")
        return True # Indicate save started

    # --- Data Access Methods for GUI ---
    def get_students(self):
        return self.students

    def get_courses(self):
        return self.courses

    def get_marks(self):
        return self.marks # GUI can iterate through this

    def get_course_by_id(self, course_id): # Renamed from find_
         for course in self.courses:
            if course.id == course_id:
                return course
         return None

    def get_student_by_id(self, student_id): # Renamed from find_
         for student in self.students:
              if student.id == student_id:
                  return student
         return None

    # --- Data Manipulation Methods ---
    def add_student(self, student_id, name, dob):
        """Adds a student. Returns True on success, False if ID exists."""
        # Use validation logic (can be enhanced)
        is_valid_id, _ = data_input.validate_student_id(student_id, {s.id for s in self.students})
        if not is_valid_id: return False
        if not name: return False # Basic validation
        if not dob: return False # Basic validation

        self.students.append(Student(student_id, name, dob))
        self._invalidate_gpas()
        return True

    def add_course(self, course_id, name, credits_str):
        """Adds a course. Returns True on success, False if ID exists or credits invalid."""
        is_valid_id, _ = data_input.validate_course_id(course_id, {c.id for c in self.courses})
        credits = data_input.validate_credits(credits_str) # Use validator
        if not is_valid_id: return False
        if not name: return False
        if credits is None: return False # Invalid credits

        self.courses.append(Course(course_id, name, credits)) # Pass validated credits
        self._invalidate_gpas()
        return True

    def add_mark(self, course_id, student_id, mark_str):
        """Adds or updates a mark. Returns True on success, False if mark invalid."""
        mark, err_msg = data_input.validate_mark(mark_str) # Use validator (rounds down)
        if err_msg:
            return False # Mark validation failed

        if course_id not in self.marks:
            self.marks[course_id] = {}
        self.marks[course_id][student_id] = mark
        self._invalidate_gpas()
        return True

    # --- GPA and Sorting ---
    def _invalidate_gpas(self):
         for student in self.students: student.gpa = None

    def calculate_all_gpas(self):
        if not self.students: return
        for student in self.students: self.calculate_student_gpa(student.id)

    def calculate_student_gpa(self, student_id):
        # ... (Keep existing calculation logic from pw6) ...
        student = self.get_student_by_id(student_id)
        if not student: return 0.0
        student_marks_values = []; corresponding_credits = []
        for course_id, marks_dict in self.marks.items():
            if student_id in marks_dict:
                course = self.get_course_by_id(course_id)
                if course: student_marks_values.append(marks_dict[student_id]); corresponding_credits.append(course.credits)
        if not student_marks_values: student.gpa = 0.0; return 0.0
        marks_arr = np.array(student_marks_values); credits_arr = np.array(corresponding_credits)
        total_credits = np.sum(credits_arr)
        if total_credits == 0: student.gpa = 0.0; return 0.0
        gpa = np.sum(marks_arr * credits_arr) / total_credits; student.gpa = gpa; return gpa

    def get_students_sorted_by_gpa(self):
        """Calculates all GPAs and returns a *new* sorted list of students."""
        self.calculate_all_gpas()
        # Sort by GPA descending, handle None as lowest
        return sorted(self.students, key=lambda s: s.gpa if s.gpa is not None else -1, reverse=True)