# pw4/output.py
import curses
import time # For potential delays

# Helper function to add centered text
def print_center(win, text):
    h, w = win.getmaxyx()
    y = h // 2
    x = w // 2 - len(text) // 2
    try:
        win.addstr(y, x, text)
    except curses.error:
        pass # Ignore error if writing outside bounds (e.g., small terminal)

# Function to display the menu
def display_menu(stdscr, options, current_row_idx, title="Main Menu"):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    x_title = w // 2 - len(title) // 2
    stdscr.addstr(0, x_title, title, curses.A_BOLD | curses.A_UNDERLINE)

    for idx, option_text in enumerate(options):
        x = w // 2 - len(option_text) // 2
        y = h // 2 - len(options) // 2 + idx
        if idx == current_row_idx:
            stdscr.attron(curses.A_REVERSE) # Highlight selected
            stdscr.addstr(y, x, option_text)
            stdscr.attroff(curses.A_REVERSE)
        else:
            stdscr.addstr(y, x, option_text)
    stdscr.refresh()

# Function to get string input in curses
def get_input(stdscr, prompt, y, x):
    stdscr.addstr(y, x, prompt)
    stdscr.refresh()
    curses.echo() # Turn echoing back on for input
    input_str = stdscr.getstr(y, x + len(prompt)).decode('utf-8')
    curses.noecho() # Turn echoing off again
    return input_str

# Function to display messages
def display_message(stdscr, message, y_offset=2, color_pair=1, wait=False):
    h, w = stdscr.getmaxyx()
    x = w // 2 - len(message) // 2
    y = h - y_offset # Display near the bottom
    try:
        stdscr.addstr(y, x, message, curses.color_pair(color_pair))
        stdscr.refresh()
        if wait:
            time.sleep(1.5) # Pause to let user see the message
            # Clear the message line
            stdscr.addstr(y, x, " " * len(message))
            stdscr.refresh()
    except curses.error:
         # If message display fails (e.g., small screen), just continue
         pass


# Function to display lists (students, courses)
def display_list(stdscr, title, header, items, get_info_func, start_y=2):
    stdscr.clear()
    h, w = stdscr.getmaxyx()

    # Title
    x_title = w // 2 - len(title) // 2
    stdscr.addstr(0, x_title, title, curses.A_BOLD | curses.A_UNDERLINE)

    # Header
    stdscr.addstr(start_y, 1, header, curses.A_BOLD)
    stdscr.addstr(start_y + 1, 1, "-" * (w - 2)) # Divider

    # Items
    current_y = start_y + 2
    if not items:
        stdscr.addstr(current_y, 1, "No items to display.")
    else:
        for item in items:
            if current_y < h - 2: # Check bounds before writing
                # Use the provided function to get formatted string
                display_string = get_info_func(item)
                stdscr.addstr(current_y, 1, display_string[:w-2]) # Truncate if too long
                current_y += 1
            else:
                stdscr.addstr(current_y, 1, "--- More items not shown ---")
                break

    stdscr.addstr(h - 1, 1, "Press any key to return to menu...")
    stdscr.refresh()
    stdscr.getch() # Wait for key press

# Function to display marks (more complex table)
def display_marks_table(stdscr, course, students, marks_dict, start_y=2):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    title = f"Mark Sheet for Course: {course.name} ({course.id})"
    x_title = w // 2 - len(title) // 2
    stdscr.addstr(0, x_title, title, curses.A_BOLD | curses.A_UNDERLINE)

    header = f"{'Student ID':<12} {'Student Name':<25} {'Mark':<5}"
    stdscr.addstr(start_y, 1, header, curses.A_BOLD)
    stdscr.addstr(start_y + 1, 1, "-" * (w - 2))

    current_y = start_y + 2
    if not students:
         stdscr.addstr(current_y, 1, "No students registered.")
    elif not marks_dict or course.id not in marks_dict or not marks_dict[course.id]:
         stdscr.addstr(current_y, 1, f"No marks entered for this course yet.")
    else:
        course_marks = marks_dict[course.id]
        for student in students:
             if current_y < h - 2:
                 mark = course_marks.get(student.id, "N/A")
                 display_string = f"{student.id:<12} {student.name:<25} {mark}"
                 stdscr.addstr(current_y, 1, display_string[:w-2])
                 current_y += 1
             else:
                stdscr.addstr(current_y, 1, "--- More students not shown ---")
                break

    stdscr.addstr(h - 1, 1, "Press any key to return to menu...")
    stdscr.refresh()
    stdscr.getch() # Wait for key press

# Function to select an item from a list (like selecting a course)
def select_item(stdscr, items, title, display_func):
    if not items:
        display_message(stdscr, f"No {title.lower()} available.", wait=True)
        return None

    current_row = 0
    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        prompt = f"Select {title} (Use UP/DOWN arrows, ENTER to select):"
        stdscr.addstr(0, 1, prompt, curses.A_BOLD)

        for idx, item in enumerate(items):
            display_string = f"{idx + 1}. {display_func(item)}"
            y = 2 + idx
            if y < h - 1:
                 if idx == current_row:
                     stdscr.attron(curses.A_REVERSE)
                     stdscr.addstr(y, 1, display_string[:w-2])
                     stdscr.attroff(curses.A_REVERSE)
                 else:
                     stdscr.addstr(y, 1, display_string[:w-2])
            else:
                 stdscr.addstr(y, 1, "--- More items not shown ---")
                 break
        stdscr.refresh()

        key = stdscr.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(items) - 1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]: # Enter key
            return items[current_row] # Return the selected object
        elif key == 27: # ESC key (optional: allow canceling selection)
             return None