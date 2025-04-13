# pw5/output.py
import curses
import time # For potential delays

# Helper function to add centered text (no changes needed)
def print_center(win, text):
    h, w = win.getmaxyx()
    y = h // 2
    x = w // 2 - len(text) // 2
    try:
        win.addstr(y, x, text)
    except curses.error:
        pass # Ignore error if writing outside bounds

# Function to display the menu (no changes needed)
def display_menu(stdscr, options, current_row_idx, title="Main Menu"):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    x_title = w // 2 - len(title) // 2
    # Ensure title fits
    if x_title < 0: x_title = 0
    stdscr.addstr(0, x_title, title[:w], curses.A_BOLD | curses.A_UNDERLINE) # Truncate title if needed

    for idx, option_text in enumerate(options):
        # Ensure option fits
        display_text = option_text[:w-2] # Leave margin
        x = w // 2 - len(display_text) // 2
        if x < 0: x = 0
        y = h // 2 - len(options) // 2 + idx
        # Ensure writing within height bounds
        if 0 <= y < h:
            try:
                if idx == current_row_idx:
                    stdscr.attron(curses.A_REVERSE)
                    stdscr.addstr(y, x, display_text)
                    stdscr.attroff(curses.A_REVERSE)
                else:
                    stdscr.addstr(y, x, display_text)
            except curses.error:
                pass # Ignore error if writing outside bounds
    stdscr.refresh()

# Function to get string input in curses (no changes needed)
def get_input(stdscr, prompt, y, x):
    # Ensure prompt fits and input area is valid
    h, w = stdscr.getmaxyx()
    if y >= h or x >= w: return "" # Cannot get input outside screen

    max_prompt_len = w - x - 1 # Leave space for cursor
    display_prompt = prompt[:max_prompt_len]

    try:
        stdscr.addstr(y, x, display_prompt)
        stdscr.refresh()
        curses.echo() # Turn echoing back on for input
        # Adjust getting input to prevent writing past screen width
        input_str = stdscr.getstr(y, x + len(display_prompt), w - (x + len(display_prompt)) -1).decode('utf-8')
        curses.noecho() # Turn echoing off again
        return input_str
    except curses.error:
         curses.noecho() # Ensure echo is off even if error occurs
         return "" # Return empty string on error


# Function to display messages (Updated for wait=False)
def display_message(stdscr, message, y_offset=2, color_pair=1, wait=False):
    h, w = stdscr.getmaxyx()
    # Ensure message fits
    display_text = message[:w-2] # Leave margin
    x = w // 2 - len(display_text) // 2
    if x < 0: x = 0
    y = h - y_offset # Display near the bottom

    # Ensure y is within bounds
    if y < 0: y = 0
    elif y >=h: y = h -1

    try:
        # Clear the line first
        stdscr.move(y, 0)
        stdscr.clrtoeol()
        # Write the message
        stdscr.addstr(y, x, display_text, curses.color_pair(color_pair))
        stdscr.refresh()

        if wait:
            # Wait for any key press if wait is True
            stdscr.nodelay(False) # Ensure getch waits
            stdscr.getch()
            # Clear the message line after key press
            stdscr.move(y, 0)
            stdscr.clrtoeol()
            stdscr.refresh()
        # If wait is False, just display and return immediately

    except curses.error:
         # If message display fails (e.g., small screen), just continue
         pass

# Function to display lists (students, courses) (no changes needed)
def display_list(stdscr, title, header, items, get_info_func, start_y=2):
    stdscr.clear()
    h, w = stdscr.getmaxyx()

    # Title
    x_title = w // 2 - len(title) // 2
    if x_title < 0: x_title = 0
    stdscr.addstr(0, x_title, title[:w], curses.A_BOLD | curses.A_UNDERLINE)

    # Header
    # Ensure header fits, adjust start_y if needed
    if start_y >= h: start_y = h - 1
    if start_y < 1: start_y = 1
    try:
        stdscr.addstr(start_y, 1, header[:w-2], curses.A_BOLD)
        if start_y + 1 < h:
            stdscr.addstr(start_y + 1, 1, "-" * (min(len(header), w - 2))) # Divider based on header length or width
    except curses.error: pass # Ignore header errors if screen too small

    # Items
    current_y = start_y + 2
    if not items:
        if current_y < h: stdscr.addstr(current_y, 1, "No items to display.")
    else:
        for item in items:
            if current_y < h - 2: # Check bounds before writing (leave space for prompt)
                display_string = get_info_func(item)
                try:
                    stdscr.addstr(current_y, 1, display_string[:w-2]) # Truncate if too long
                except curses.error: pass # Ignore error for this line
                current_y += 1
            else:
                if current_y < h: stdscr.addstr(current_y, 1, "--- More items not shown ---"[:w-2])
                break

    # Prompt line at the bottom
    prompt_text = "Press any key to return to menu..."
    prompt_y = h - 1
    if prompt_y < 0: prompt_y = 0
    try:
        stdscr.move(prompt_y, 0) # Clear line first
        stdscr.clrtoeol()
        stdscr.addstr(prompt_y, 1, prompt_text[:w-2])
    except curses.error: pass

    stdscr.refresh()
    stdscr.nodelay(False) # Ensure getch waits
    stdscr.getch() # Wait for key press

# Function to display marks table (no changes needed)
def display_marks_table(stdscr, course, students, marks_dict, start_y=2):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    title = f"Mark Sheet for Course: {course.name} ({course.id})"
    x_title = w // 2 - len(title) // 2
    if x_title < 0: x_title = 0
    stdscr.addstr(0, x_title, title[:w], curses.A_BOLD | curses.A_UNDERLINE)

    header = f"{'Student ID':<12} {'Student Name':<25} {'Mark':<5}"
    # Ensure header fits, adjust start_y if needed
    if start_y >= h: start_y = h - 1
    if start_y < 1: start_y = 1
    try:
        stdscr.addstr(start_y, 1, header[:w-2], curses.A_BOLD)
        if start_y + 1 < h:
             stdscr.addstr(start_y + 1, 1, "-" * (min(len(header), w - 2)))
    except curses.error: pass

    current_y = start_y + 2
    if not students:
         if current_y < h: stdscr.addstr(current_y, 1, "No students registered.")
    elif not marks_dict or course.id not in marks_dict or not marks_dict[course.id]:
         if current_y < h: stdscr.addstr(current_y, 1, f"No marks entered for this course yet.")
    else:
        course_marks = marks_dict[course.id]
        for student in students:
             if current_y < h - 2: # Leave space for prompt
                 mark = course_marks.get(student.id, "N/A")
                 display_string = f"{student.id:<12} {student.name:<25} {mark}"
                 try:
                    stdscr.addstr(current_y, 1, display_string[:w-2])
                 except curses.error: pass
                 current_y += 1
             else:
                if current_y < h: stdscr.addstr(current_y, 1, "--- More students not shown ---"[:w-2])
                break

    # Prompt line at the bottom
    prompt_text = "Press any key to return to menu..."
    prompt_y = h - 1
    if prompt_y < 0: prompt_y = 0
    try:
        stdscr.move(prompt_y, 0) # Clear line first
        stdscr.clrtoeol()
        stdscr.addstr(prompt_y, 1, prompt_text[:w-2])
    except curses.error: pass

    stdscr.refresh()
    stdscr.nodelay(False)
    stdscr.getch() # Wait for key press

# Function to select an item from a list (no changes needed)
def select_item(stdscr, items, title, display_func):
    if not items:
        display_message(stdscr, f"No {title.lower()} available. Press key.", wait=True, color_pair=3) # Use color 3 for warning
        return None

    current_row = 0
    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        prompt = f"Select {title} (Use UP/DOWN arrows, ENTER to select, ESC to cancel):"
        try:
            stdscr.addstr(0, 1, prompt[:w-2], curses.A_BOLD)
        except curses.error: pass

        items_to_display = h - 3 # Max items fitting on screen leaving space for prompt and bottom line
        start_index = 0
        # Basic pagination logic (can be improved)
        if current_row >= items_to_display:
            start_index = current_row - items_to_display + 1

        for idx, item in enumerate(items[start_index:], start=start_index):
            if idx >= start_index + items_to_display:
                 if 2 + idx - start_index < h : stdscr.addstr(2 + idx - start_index, 1, "--- More items not shown ---"[:w-2])
                 break # Stop if we run out of screen space

            display_string = f"{idx + 1}. {display_func(item)}"
            y = 2 + idx - start_index
            if y < h -1: # Check vertical bounds
                 line_text = display_string[:w-2] # Truncate
                 try:
                     if idx == current_row:
                         stdscr.attron(curses.A_REVERSE)
                         stdscr.addstr(y, 1, line_text)
                         stdscr.attroff(curses.A_REVERSE)
                     else:
                         stdscr.addstr(y, 1, line_text)
                 except curses.error: pass # Ignore if cannot write

        stdscr.refresh()

        key = stdscr.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(items) - 1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]: # Enter key
            return items[current_row] # Return the selected object
        elif key == 27: # ESC key
             display_message(stdscr,"Selection cancelled. Press key.", wait=True, color_pair=3)
             return None