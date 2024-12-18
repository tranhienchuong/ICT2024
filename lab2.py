# Student Mark Management System (OOP)

class Student:
    def __init__(self, student_id, name, dob):
        self.student_id = student_id
        self.name = name
        self.dob = dob

    def __str__(self):
        return f"ID: {self.student_id}, Name: {self.name}, DoB: {self.dob}"

class Course:
    def __init__(self, course_id, name):
        self.course_id = course_id
        self.name = name

    def __str__(self):
        return f"ID: {self.course_id}, Name: {self.name}"

class MarkManagement:
    def __init__(self):
        self.students = []
        self.courses = []
        self.marks = {}

    def input_students(self):
        num_students = int(input("Enter the number of students in the class: "))
        for _ in range(num_students):
            student_id = input("Enter student ID: ")
            name = input("Enter student name: ")
            dob = input("Enter student Date of Birth (DoB): ")
            self.students.append(Student(student_id, name, dob))

    def input_courses(self):
        num_courses = int(input("Enter the number of courses: "))
        for _ in range(num_courses):
            course_id = input("Enter course ID: ")
            name = input("Enter course name: ")
            self.courses.append(Course(course_id, name))

    def input_marks(self):
        course_id = input("Enter the course ID to input marks for: ")
        course = next((course for course in self.courses if course.course_id == course_id), None)
        if not course:
            print("Course not found.")
            return

        if course_id not in self.marks:
            self.marks[course_id] = {}

        for student in self.students:
            mark = float(input(f"Enter mark for student {student.name} (ID: {student.student_id}): "))
            self.marks[course_id][student.student_id] = mark

    def list_courses(self):
        print("Courses:")
        for course in self.courses:
            print(course)

    def list_students(self):
        print("Students:")
        for student in self.students:
            print(student)

    def show_student_marks(self):
        course_id = input("Enter the course ID to view marks: ")
        if course_id in self.marks:
            print(f"Marks for course ID {course_id}:")
            for student_id, mark in self.marks[course_id].items():
                student = next((s for s in self.students if s.student_id == student_id), None)
                if student:
                    print(f"Student: {student.name} (ID: {student_id}), Mark: {mark}")
        else:
            print("Marks not found for this course.")

    def run(self):
        while True:
            print("\nMenu:")
            print("1. List courses")
            print("2. List students")
            print("3. Input marks for a course")
            print("4. Show student marks for a course")
            print("5. Exit")

            choice = input("Enter your choice: ")
            if choice == "1":
                self.list_courses()
            elif choice == "2":
                self.list_students()
            elif choice == "3":
                self.input_marks()
            elif choice == "4":
                self.show_student_marks()
            elif choice == "5":
                break
            else:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    management = MarkManagement()
    management.input_students()
    management.input_courses()
    management.run()
