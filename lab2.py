import sys # Using sys.exit() for a cleaner exit

class Student:
    """Represents a student with ID, name, and date of birth."""
    def __init__(self, student_id, name, dob):
        self.id = student_id
        self.name = name
        self.dob = dob

    def display_info(self):
        """Prints the student's information."""
        print(f"  ID: {self.id}, Name: {self.name}, DoB: {self.dob}")

    def get_info_str(self):
        """Returns student info as a formatted string."""
        return f"{self.id:<10} {self.name:<25} {self.dob:<15}"

class Course:
    """Represents a course with ID and name."""
    def __init__(self, course_id, name):
        self.id = course_id
        self.name = name

    def display_info(self):
        """Prints the course's information."""
        print(f"  ID: {self.id}, Name: {self.name}")

    def get_info_str(self):
         """Returns course info as a formatted string."""
         return f"{self.id:<10} {self.name:<25}"

class MarkManagementSystem:
    """Manages students, courses, and marks using OOP principles."""
    def __init__(self):
        self.students = [] # List to store Student objects
        self.courses = []  # List to store Course objects
        self.marks = {}    # Dictionary: {course_id: {student_id: mark}}

    # --- Input Methods ---
    def input_students(self):
        """Handles inputting the number and details of students."""
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
            # Basic check for duplicate student ID
            if any(s.id == student_id for s in self.students):
                 print(f"  Error: Student ID '{student_id}' already exists. Skipping this student.")
                 continue
            name = input("  Enter student name: ")
            dob = input("  Enter student Date of Birth (dd/mm/yyyy): ")
            self.students.append(Student(student_id, name, dob))
        print("Student information input complete.")

    def input_courses(self):
        """Handles inputting the number and details of courses."""
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
             # Basic check for duplicate course ID
            if any(c.id == course_id for c in self.courses):
                 print(f"  Error: Course ID '{course_id}' already exists. Skipping this course.")
                 continue
            name = input("  Enter course name: ")
            self.courses.append(Course(course_id, name))
        print("Course information input complete.")

    def select_course(self):
        """Displays courses and prompts the user to select one by index."""
        if not self.courses:
            print("\nError: No courses available to select.")
            return None

        print("\n--- Available Courses ---")
        for index, course in enumerate(self.courses):
            print(f"{index + 1}. {course.get_info_str()}") # Use method from Course

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
        """Handles inputting marks for students in a selected course."""
        selected_course = self.select_course()
        if selected_course is None:
            return # No course selected or no courses exist

        course_id = selected_course.id
        print(f"\n--- Input Marks for Course: {selected_course.name} ({course_id}) ---")

        if not self.students:
            print("Error: No students available to input marks for.")
            return

        if course_id not in self.marks:
            self.marks[course_id] = {} # Initialize marks dict for this course if needed

        for student in self.students:
            while True:
                try:
                    mark_input = input(f"  Enter mark for {student.name} ({student.id}): ")
                    mark = float(mark_input)
                    # Optional: Add validation for mark range (e.g., 0-10, 0-100)
                    # if not (0 <= mark <= 10): # Example validation
                    #    print("  Mark must be between 0 and 10.")
                    #    continue
                    self.marks[course_id][student.id] = mark
                    break # Exit inner loop on valid input
                except ValueError:
                    print("  Invalid input. Please enter a numerical mark (e.g., 7.5).")
                except Exception as e:
                     print(f"  An unexpected error occurred: {e}")
                     break # Exit if other error happens

        print(f"Marks input complete for course {course_id}.")

    # --- Listing Methods ---
    def list_students(self):
        """Lists all registered students."""
        print("\n--- Student List ---")
        if not self.students:
            print("No students registered.")
            return
        print(f"{'ID':<10} {'Name':<25} {'Date of Birth':<15}")
        print("-" * 50)
        for student in self.students:
            # Polymorphism: We could just call student.display_info()
            # but using get_info_str() provides better formatting here.
            print(student.get_info_str())

    def list_courses(self):
        """Lists all registered courses."""
        print("\n--- Course List ---")
        if not self.courses:
            print("No courses registered.")
            return
        print(f"{'ID':<10} {'Name':<25}")
        print("-" * 35)
        for course in self.courses:
             # Polymorphism example: using a common method name implicitly
             print(course.get_info_str())


    def show_student_marks_for_course(self):
        """Shows the marks of all students for a selected course."""
        selected_course = self.select_course()
        if selected_course is None:
            return

        course_id = selected_course.id
        print(f"\n--- Mark Sheet for Course: {selected_course.name} ({course_id}) ---")

        if course_id not in self.marks or not self.marks[course_id]:
            print(f"No marks have been entered for this course yet.")
            # Still show students who *should* have marks
            if self.students:
                 print("\nRegistered students (no marks entered):")
                 self.list_students()
            return

        if not self.students:
             print("There are no students registered to show marks for.")
             return

        print(f"{'Student ID':<12} {'Student Name':<25} {'Mark'}")
        print("-" * 45)

        course_marks = self.marks[course_id]
        for student in self.students:
            student_id = student.id
            student_name = student.name
            # Use .get() to safely retrieve the mark, providing a default if not found
            mark = course_marks.get(student_id, "N/A - Not Entered")
            print(f"{student_id:<12} {student_name:<25} {mark}")

    # --- Main Program Loop ---
    def run(self):
        """Runs the main menu loop for the management system."""
        print("--- Student Mark Management System (OOP Version) ---")

        # Initial Data Entry
        self.input_students()
        self.input_courses()

        # Main Menu
        while True:
            print("\n--- Main Menu ---")
            print("1. Input Marks for a Course")
            print("2. List All Students")
            print("3. List All Courses")
            print("4. Show Mark Sheet for a Course")
            print("0. Exit Program")

            choice = input("Enter your choice: ")

            if choice == '1':
                self.input_marks()
            elif choice == '2':
                self.list_students()
            elif choice == '3':
                self.list_courses()
            elif choice == '4':
                self.show_student_marks_for_course()
            elif choice == '0':
                print("Exiting program. Goodbye!")
                sys.exit() # Cleanly exits the script
            else:
                print("Invalid choice. Please try again.")

# --- Script Execution ---
if __name__ == "__main__":
    system = MarkManagementSystem()
    system.run()