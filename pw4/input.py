# pw4/input.py
import math

def validate_positive_integer(input_str):
    """Tries to convert input to a positive integer."""
    try:
        num = int(input_str)
        if num > 0:
            return num
        else:
            return None # Indicate validation failure
    except ValueError:
        return None

def validate_student_id(student_id, existing_ids):
    """Checks if student ID is valid and not duplicate."""
    if not student_id: # Basic check if empty
        return False, "Student ID cannot be empty."
    if student_id in existing_ids:
        return False, f"Student ID '{student_id}' already exists."
    return True, "" # Valid

def validate_course_id(course_id, existing_ids):
    """Checks if course ID is valid and not duplicate."""
    if not course_id:
        return False, "Course ID cannot be empty."
    if course_id in existing_ids:
        return False, f"Course ID '{course_id}' already exists."
    return True, "" # Valid

def validate_credits(credits_str):
    """Validates course credits input."""
    try:
        credits = int(credits_str)
        if credits > 0:
            return credits
        else:
            return None # Indicate validation failure (must be positive)
    except ValueError:
        return None

def validate_mark(mark_str):
    """Validates and rounds down mark input to 1 decimal place."""
    try:
        mark_float = float(mark_str)
        # Add range validation if needed, e.g., 0-10 or 0-20
        # if not (0 <= mark_float <= 10):
        #     return None, "Mark must be between 0 and 10."

        # Round down using math.floor
        rounded_mark = math.floor(mark_float * 10) / 10
        return rounded_mark, "" # Return validated and rounded mark
    except ValueError:
        return None, "Invalid input. Please enter a numerical mark."