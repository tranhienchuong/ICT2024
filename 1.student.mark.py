# Khởi tạo các danh sách và từ điển để lưu trữ dữ liệu
students = []
courses = []
marks = {} # Key: course_id, Value: {student_id: mark}

# --- Hàm nhập liệu ---

def input_number_of_students():
  """Hỏi và trả về số lượng sinh viên."""
  while True:
    try:
      num = int(input("Nhập số lượng sinh viên trong lớp: "))
      if num > 0:
        return num
      else:
        print("Số lượng phải là số dương.")
    except ValueError:
      print("Vui lòng nhập một số nguyên hợp lệ.")

def input_student_info(student_id_prefix="SV"):
    """Nhập thông tin cho một sinh viên và trả về dưới dạng dictionary."""
    student_id = input(f"Nhập mã sinh viên (ví dụ: {student_id_prefix}001): ")
    # Có thể thêm kiểm tra trùng lặp ID ở đây nếu cần
    name = input("Nhập tên sinh viên: ")
    dob = input("Nhập ngày sinh (dd/mm/yyyy): ")
    return {'id': student_id, 'name': name, 'DoB': dob}

def input_number_of_courses():
  """Hỏi và trả về số lượng khóa học."""
  while True:
    try:
      num = int(input("Nhập số lượng khóa học: "))
      if num > 0:
        return num
      else:
        print("Số lượng phải là số dương.")
    except ValueError:
      print("Vui lòng nhập một số nguyên hợp lệ.")

def input_course_info(course_id_prefix="KH"):
  """Nhập thông tin cho một khóa học và trả về dưới dạng dictionary."""
  course_id = input(f"Nhập mã khóa học (ví dụ: {course_id_prefix}001): ")
  # Có thể thêm kiểm tra trùng lặp ID ở đây nếu cần
  name = input("Nhập tên khóa học: ")
  return {'id': course_id, 'name': name}

def select_course():
    """Hiển thị danh sách khóa học và yêu cầu người dùng chọn một khóa."""
    if not courses:
        print("Chưa có khóa học nào được nhập.")
        return None

    print("\n--- Danh sách khóa học ---")
    for index, course in enumerate(courses):
        print(f"{index + 1}. {course['id']} - {course['name']}")

    while True:
        try:
            choice = int(input("Chọn khóa học bằng số thứ tự để nhập điểm: "))
            if 1 <= choice <= len(courses):
                return courses[choice - 1]['id'] # Trả về ID của khóa học được chọn
            else:
                print(f"Lựa chọn không hợp lệ. Vui lòng chọn từ 1 đến {len(courses)}.")
        except ValueError:
            print("Vui lòng nhập một số.")

def input_marks_for_course(course_id):
    """Nhập điểm cho tất cả sinh viên trong một khóa học cụ thể."""
    if not students:
        print("Chưa có sinh viên nào để nhập điểm.")
        return
    if course_id not in marks:
        marks[course_id] = {} # Khởi tạo từ điển điểm cho khóa học nếu chưa có

    print(f"\n--- Nhập điểm cho khóa học {course_id} ---")
    for student in students:
        student_id = student['id']
        while True:
            try:
                mark_input = input(f"Nhập điểm cho sinh viên {student['name']} ({student_id}): ")
                mark = float(mark_input) # Chuyển đổi sang số thực
                # Có thể thêm kiểm tra điểm hợp lệ (ví dụ: 0-10) ở đây
                marks[course_id][student_id] = mark
                break # Thoát vòng lặp khi nhập thành công
            except ValueError:
                print("Điểm không hợp lệ. Vui lòng nhập một số (ví dụ: 7.5).")
            except Exception as e:
                print(f"Đã xảy ra lỗi: {e}")
                break # Thoát nếu có lỗi khác

# --- Hàm hiển thị ---

def list_courses():
  """Hiển thị danh sách tất cả các khóa học."""
  if not courses:
    print("\nChưa có khóa học nào.")
    return
  print("\n--- Danh sách khóa học ---")
  for course in courses:
    print(f"ID: {course['id']}, Tên: {course['name']}")

def list_students():
  """Hiển thị danh sách tất cả sinh viên."""
  if not students:
    print("\nChưa có sinh viên nào.")
    return
  print("\n--- Danh sách sinh viên ---")
  for student in students:
    print(f"ID: {student['id']}, Tên: {student['name']}, Ngày sinh: {student['DoB']}")

def show_student_marks_for_course():
    """Chọn một khóa học và hiển thị điểm của tất cả sinh viên trong khóa đó."""
    course_id = select_course()
    if course_id is None:
        return # Không có khóa học để chọn hoặc không có khóa nào

    if course_id not in marks or not marks[course_id]:
        print(f"\nChưa có điểm nào được nhập cho khóa học {course_id}.")
        # Tìm tên khóa học để hiển thị
        course_name = next((c['name'] for c in courses if c['id'] == course_id), course_id)
        print(f"Khóa học: {course_name}")
        return

    # Tìm tên khóa học để hiển thị
    course_name = next((c['name'] for c in courses if c['id'] == course_id), course_id)
    print(f"\n--- Bảng điểm khóa học: {course_name} ({course_id}) ---")

    if not students:
        print("Chưa có sinh viên nào trong danh sách.")
        return

    print(f"{'Mã SV':<10} {'Tên Sinh Viên':<25} {'Điểm'}")
    print("-" * 40)
    for student in students:
        student_id = student['id']
        student_name = student['name']
        # Lấy điểm, nếu sinh viên chưa có điểm trong khóa này thì hiển thị 'Chưa nhập'
        mark = marks[course_id].get(student_id, "Chưa nhập")
        print(f"{student_id:<10} {student_name:<25} {mark}")

# --- Chương trình chính (ví dụ cách sử dụng các hàm) ---
def main():
    print("--- Chương trình quản lý điểm sinh viên ---")

    # 1. Nhập sinh viên
    num_students = input_number_of_students()
    print("\n--- Nhập thông tin sinh viên ---")
    for i in range(num_students):
        print(f"\nNhập thông tin cho sinh viên thứ {i+1}:")
        student_data = input_student_info()
        students.append(student_data)

    # 2. Nhập khóa học
    num_courses = input_number_of_courses()
    print("\n--- Nhập thông tin khóa học ---")
    for i in range(num_courses):
        print(f"\nNhập thông tin cho khóa học thứ {i+1}:")
        course_data = input_course_info()
        courses.append(course_data)

    # Vòng lặp menu chính
    while True:
        print("\n--- Menu ---")
        print("1. Nhập điểm cho khóa học")
        print("2. Liệt kê danh sách khóa học")
        print("3. Liệt kê danh sách sinh viên")
        print("4. Hiển thị bảng điểm theo khóa học")
        print("0. Thoát chương trình")

        choice = input("Nhập lựa chọn của bạn: ")

        if choice == '1':
            selected_course_id = select_course()
            if selected_course_id:
                input_marks_for_course(selected_course_id)
        elif choice == '2':
            list_courses()
        elif choice == '3':
            list_students()
        elif choice == '4':
            show_student_marks_for_course()
        elif choice == '0':
            print("Đang thoát chương trình...")
            break
        else:
            print("Lựa chọn không hợp lệ. Vui lòng chọn lại.")

# Chạy chương trình chính
if __name__ == "__main__":
    main()