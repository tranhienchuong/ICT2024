import math # For floor function
import numpy as np # For GPA calculation
import sys

class Student:
    """Represents a student with ID, name, and date of birth."""
    def __init__(self, student_id, name, dob):
        self.id = student_id
        self.name = name
        self.dob = dob
        # Add a placeholder for GPA, calculated later
        self.gpa = None

    def display_info(self, show_gpa=False):
        """Prints the student's information, optionally including GPA."""
        gpa_str = f", GPA: {self.gpa:.2f}" if show_gpa and self.gpa is not None else ""
        if show_gpa and self.gpa is None:
             gpa_str = ", GPA: N/A" # Indicate if GPA hasn't been calculated or is invalid

        print(f"  ID: {self.id}, Name: {self.name}, DoB: {self.dob}{gpa_str}")

    def get_info_str(self, show_gpa=False):
        """Returns student info as a formatted string, optionally including GPA."""
        gpa_str = f"{self.gpa:.2f}" if show_gpa and self.gpa is not None else "N/A"
        return f"{self.id:<10} {self.name:<25} {self.dob:<15} {gpa_str if show_gpa else ''}"

class Course:
    """Represents a course with ID, name, and credits."""
    # Added credits attribute
    def __init__(self, course_id, name, credits):
        self.id = course_id
        self.name = name
        try:
            self.credits = int(credits) # Ensure credits are integers
            if self.credits <= 0:
                 print(f"Warning: Credits for course {self.id} should be positive. Setting to 1.")
                 self.credits = 1
        except ValueError:
             print(f"Warning: Invalid credit value for course {self.id}. Setting to 1.")
             self.credits = 1


    def display_info(self):
        """Prints the course's information."""
        print(f"  ID: {self.id}, Name: {self.name}, Credits: {self.credits}")

    def get_info_str(self):
         """Returns course info as a formatted string."""
         # Added credits display
         return f"{self.id:<10} {self.name:<25} {self.credits:<8}"

class MarkManagementSystem:
    """Manages students, courses, and marks using OOP principles."""
    def __init__(self):
        self.students = []
        self.courses = []
        self.marks = {} # Dictionary: {course_id: {student_id: mark}}

    # --- Helper Methods ---
    def find_student_by_id(self, student_id):
        """Finds and returns a Student object by ID, or None if not found."""
        for student in self.students:
            if student.id == student_id:
                return student
        return None

    def find_course_by_id(self, course_id):
        """Finds and returns a Course object by ID, or None if not found."""
        for course in self.courses:
            if course.id == course_id:
                return course
        return None

    # --- Input Methods ---
    def input_students(self):
        # (Identical to previous version - no changes needed here)
        print("\n--- Input Student Information ---")
        while True:
            try:
                num_students = int(input("Enter the number of students: "))
                if num_students > 0:
                    break
                else:
                    print("Number must be positive.")
            except ValueError:
                print("Invalid input. Please enter an integer.")

        for i in range(num_students):
            print(f"\nEnter details for student {i+1}:")
            student_id = input("  Enter student ID: ")
            if any(s.id == student_id for s in self.students):
                 print(f"  Error: Student ID '{student_id}' already exists. Skipping this student.")
                 continue
            name = input("  Enter student name: ")
            dob = input("  Enter student Date of Birth (dd/mm/yyyy): ")
            self.students.append(Student(student_id, name, dob))
        print("Student information input complete.")


    def input_courses(self):
        # Modified to include credits input
        print("\n--- Input Course Information ---")
        while True:
            try:
                num_courses = int(input("Enter the number of courses: "))
                if num_courses > 0:
                    break
                else:
                    print("Number must be positive.")
            except ValueError:
                print("Invalid input. Please enter an integer.")

        for i in range(num_courses):
            print(f"\nEnter details for course {i+1}:")
            course_id = input("  Enter course ID: ")
            if any(c.id == course_id for c in self.courses):
                 print(f"  Error: Course ID '{course_id}' already exists. Skipping this course.")
                 continue
            name = input("  Enter course name: ")
            # Add credits input
            credits = input("  Enter course credits: ")
            self.courses.append(Course(course_id, name, credits)) # Pass credits to constructor
        print("Course information input complete.")

    def select_course(self):
        # (Small modification to use updated get_info_str)
        if not self.courses:
            print("\nError: No courses available to select.")
            return None

        print("\n--- Available Courses ---")
        # Display header including credits
        print(f"   {'ID':<10} {'Name':<25} {'Credits':<8}")
        print("   " + "-" * 45)
        for index, course in enumerate(self.courses):
             # Use the updated method that includes credits
            print(f"{index + 1}. {course.get_info_str()}")

        while True:
            try:
                choice = int(input("Select a course by number to input marks: "))
                if 1 <= choice <= len(self.courses):
                    return self.courses[choice - 1] # Return the selected Course object
                else:
                    print(f"Invalid choice. Please enter a number between 1 and {len(self.courses)}.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def input_marks(self):
        # Modified to round down marks using math.floor
        selected_course = self.select_course()
        if selected_course is None:
            return

        course_id = selected_course.id
        print(f"\n--- Input Marks for Course: {selected_course.name} ({course_id}) ---")

        if not self.students:
            print("Error: No students available to input marks for.")
            return

        if course_id not in self.marks:
            self.marks[course_id] = {}

        for student in self.students:
            while True:
                try:
                    mark_input = input(f"  Enter mark for {student.name} ({student.id}): ")
                    mark_float = float(mark_input)

                    # --- Apply rounding down to 1 decimal place ---
                    # Formula: floor(value * 10) / 10
                    rounded_mark = math.floor(mark_float * 10) / 10
                    # ------------------------------------------------

                    # Optional: Add validation for mark range AFTER rounding
                    # if not (0 <= rounded_mark <= 10): # Example validation
                    #    print(f"  Mark must be between 0 and 10. Value entered: {mark_float}")
                    #    continue

                    self.marks[course_id][student.id] = rounded_mark # Store the rounded mark
                    print(f"  > Stored mark as: {rounded_mark}") # Show the user the stored value
                    break
                except ValueError:
                    print("  Invalid input. Please enter a numerical mark (e.g., 7.5).")
                except Exception as e:
                     print(f"  An unexpected error occurred: {e}")
                     break

        print(f"Marks input complete for course {course_id}.")
        # Invalidate previously calculated GPAs as marks have changed
        self._invalidate_gpas()

    # --- Calculation and Sorting Methods ---

    def _invalidate_gpas(self):
         """Sets all student GPAs to None, indicating they need recalculation."""
         for student in self.students:
              student.gpa = None

    def calculate_student_gpa(self, student_id):
        """Calculates GPA for a specific student using numpy."""
        student = self.find_student_by_id(student_id)
        if not student:
            print(f"Error: Student with ID {student_id} not found.")
            return None # Or raise an error

        student_marks = []
        corresponding_credits = []

        # Collect all marks and credits for this student
        for course_id, marks_dict in self.marks.items():
            if student_id in marks_dict:
                course = self.find_course_by_id(course_id)
                if course:
                    student_marks.append(marks_dict[student_id])
                    corresponding_credits.append(course.credits)
                else:
                    # Should not happen if data integrity is maintained
                    print(f"Warning: Course {course_id} not found for mark calculation.")

        if not student_marks or not corresponding_credits:
            # print(f"No marks or credits found for student {student_id} to calculate GPA.")
            student.gpa = 0.0 # Assign 0 GPA if no marks/credits found
            return 0.0 # Or None, depending on desired behavior

        # Use numpy arrays for vectorized calculation
        marks_arr = np.array(student_marks)
        credits_arr = np.array(corresponding_credits)

        total_weighted_marks = np.sum(marks_arr * credits_arr)
        total_credits = np.sum(credits_arr)

        if total_credits == 0:
            # print(f"Total credits are zero for student {student_id}. Cannot calculate GPA.")
            student.gpa = 0.0 # Assign 0 GPA
            return 0.0 # Avoid division by zero

        gpa = total_weighted_marks / total_credits
        student.gpa = gpa # Store calculated GPA in the student object
        return gpa

    def calculate_all_gpas(self):
         """Calculates GPA for all students."""
         print("\nCalculating GPAs for all students...")
         if not self.students:
             print("No students available.")
             return
         for student in self.students:
             self.calculate_student_gpa(student.id)
         print("GPA calculation complete.")


    def sort_students_by_gpa(self):
        """Sorts the internal student list by calculated GPA in descending order."""
        print("\nSorting students by GPA (descending)...")
        # Ensure all GPAs are calculated first
        self.calculate_all_gpas()

        # Sort the list in-place
        # Handle potential None GPAs by treating them as lowest (e.g., -1 or 0)
        self.students.sort(key=lambda s: s.gpa if s.gpa is not None else -1, reverse=True)

        print("Students sorted.")
        # Display the sorted list immediately
        self.list_students(show_gpa=True)


    # --- Listing Methods ---
    def list_students(self, show_gpa=False):
        # Modified to optionally show GPA
        print("\n--- Student List ---")
        if not self.students:
            print("No students registered.")
            return

        # Print header including GPA if requested
        header = f"{'ID':<10} {'Name':<25} {'Date of Birth':<15}"
        if show_gpa:
            header += f" {'GPA':<5}"
        print(header)
        print("-" * (len(header) + 2)) # Adjust divider length

        for student in self.students:
            print(student.get_info_str(show_gpa=show_gpa)) # Pass show_gpa flag

    def list_courses(self):
        # Modified to show credits
        print("\n--- Course List ---")
        if not self.courses:
            print("No courses registered.")
            return

        # Print header including credits
        print(f"{'ID':<10} {'Name':<25} {'Credits':<8}")
        print("-" * 45) # Adjust divider

        for course in self.courses:
             print(course.get_info_str())


    def show_student_marks_for_course(self):
        # (No significant changes needed here, but uses updated find methods)
        selected_course = self.select_course()
        if selected_course is None:
            return

        course_id = selected_course.id
        course_name = selected_course.name
        print(f"\n--- Mark Sheet for Course: {course_name} ({course_id}) ---")

        if course_id not in self.marks or not self.marks[course_id]:
            print(f"No marks have been entered for this course yet.")
            return

        if not self.students:
             print("There are no students registered to show marks for.")
             return

        print(f"{'Student ID':<12} {'Student Name':<25} {'Mark':<5}")
        print("-" * 45)

        course_marks = self.marks[course_id]
        for student in self.students:
            student_id = student.id
            student_name = student.name
            mark = course_marks.get(student_id, "N/A") # Mark already rounded on input
            print(f"{student_id:<12} {student_name:<25} {mark}")


    # --- Main Program Loop ---
    def run(self):
        """Runs the main menu loop for the management system."""
        print("--- Student Mark Management System (OOP + Math/Numpy) ---")

        self.input_students()
        self.input_courses()

        while True:
            print("\n--- Main Menu ---")
            print("1. Input Marks for a Course (Rounds down to 1 decimal)")
            print("2. List All Students")
            print("3. List All Courses (Shows Credits)")
            print("4. Show Mark Sheet for a Course")
            print("5. Calculate GPA for all students")
            print("6. List Students Sorted by GPA (Descending)")
            print("0. Exit Program")

            choice = input("Enter your choice: ")

            if choice == '1':
                self.input_marks()
            elif choice == '2':
                self.list_students(show_gpa=True) # Show GPA when listing normally now
            elif choice == '3':
                self.list_courses()
            elif choice == '4':
                self.show_student_marks_for_course()
            elif choice == '5':
                self.calculate_all_gpas()
                print("GPAs calculated. Choose option 2 or 6 to view.")
            elif choice == '6':
                self.sort_students_by_gpa() # Sorts and then lists
            elif choice == '0':
                print("Exiting program. Goodbye!")
                sys.exit()
            else:
                print("Invalid choice. Please try again.")

# --- Script Execution ---
if __name__ == "__main__":
    # Add numpy installation check maybe?
    try:
        import numpy
    except ImportError:
        print("Error: NumPy library not found.")
        print("Please install it using: pip install numpy")
        sys.exit(1)

    system = MarkManagementSystem()
    system.run()