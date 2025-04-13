# pw4/domains/student.py
class Student:
    """Represents a student with ID, name, and date of birth."""
    def __init__(self, student_id, name, dob):
        self.id = student_id
        self.name = name
        self.dob = dob
        self.gpa = None # Calculated later

    # String representation used for simple display or debugging
    def __str__(self):
        gpa_str = f", GPA: {self.gpa:.2f}" if self.gpa is not None else ""
        return f"ID: {self.id}, Name: {self.name}, DoB: {self.dob}{gpa_str}"

    # Method specifically for table formatting in curses might be useful
    def get_display_info(self, show_gpa=False):
        gpa_str = f"{self.gpa:.2f}" if show_gpa and self.gpa is not None else "N/A"
        return f"{self.id:<10} {self.name:<25} {self.dob:<15}" + (f" {gpa_str:<5}" if show_gpa else "")