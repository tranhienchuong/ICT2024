# pw4/domains/course.py
class Course:
    """Represents a course with ID, name, and credits."""
    def __init__(self, course_id, name, credits):
        self.id = course_id
        self.name = name
        # Basic validation for credits
        try:
            self.credits = int(credits)
            if self.credits <= 0:
                print(f"Warning: Credits for course {course_id} must be positive. Set to 1.") # Print warning might interfere with curses, consider logging
                self.credits = 1
        except ValueError:
            print(f"Warning: Invalid credits value for course {course_id}. Set to 1.")
            self.credits = 1

    def __str__(self):
        return f"ID: {self.id}, Name: {self.name}, Credits: {self.credits}"

    def get_display_info(self):
        return f"{self.id:<10} {self.name:<25} {self.credits:<8}"