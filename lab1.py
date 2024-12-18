# Student Mark Management System

def input_number_of_students():
    return int(input("Enter the number of students in the class: "))

def input_student_information():
    students = []
    num_students = input_number_of_students()
    for _ in range(num_students):
        student_id = input("Enter student ID: ")
        name = input("Enter student name: ")
        dob = input("Enter student Date of Birth (DoB): ")
        students.append((student_id, name, dob))
    return students

def input_number_of_courses():
    return int(input("Enter the number of courses: "))

def input_course_information():
    courses = []
    num_courses = input_number_of_courses()
    for _ in range(num_courses):
        course_id = input("Enter course ID: ")
        name = input("Enter course name: ")
        courses.append((course_id, name))
    return courses

def input_marks(students, courses):
    course_id = input("Enter the course ID to input marks for: ")
    course_exists = any(course[0] == course_id for course in courses)
    if not course_exists:
        print("Course not found.")
        return {}

    marks = {}
    for student in students:
        mark = float(input(f"Enter mark for student {student[1]} (ID: {student[0]}): "))
        marks[student[0]] = mark
    return course_id, marks

def list_courses(courses):
    print("Courses:")
    for course in courses:
        print(f"ID: {course[0]}, Name: {course[1]}")

def list_students(students):
    print("Students:")
    for student in students:
        print(f"ID: {student[0]}, Name: {student[1]}, DoB: {student[2]}")

def show_student_marks(course_id, marks):
    print(f"Marks for course ID {course_id}:")
    for student_id, mark in marks.items():
        print(f"Student ID: {student_id}, Mark: {mark}")

def main():
    students = input_student_information()
    courses = input_course_information()
    course_marks = {}

    while True:
        print("\nMenu:")
        print("1. List courses")
        print("2. List students")
        print("3. Input marks for a course")
        print("4. Show student marks for a course")
        print("5. Exit")

        choice = input("Enter your choice: ")
        if choice == "1":
            list_courses(courses)
        elif choice == "2":
            list_students(students)
        elif choice == "3":
            course_id, marks = input_marks(students, courses)
            if course_id:
                course_marks[course_id] = marks
        elif choice == "4":
            course_id = input("Enter the course ID to view marks: ")
            if course_id in course_marks:
                show_student_marks(course_id, course_marks[course_id])
            else:
                print("Marks not found for this course.")
        elif choice == "5":
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
