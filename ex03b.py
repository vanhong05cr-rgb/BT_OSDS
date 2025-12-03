from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import getpass

# Khởi tạo driver
driver = webdriver.Chrome()
driver.maximize_window()

# 1. Mở trang web
url = 'https://apps.lms.hutech.edu.vn/authn/login'
driver.get(url)
time.sleep(3) # Đợi trang tải xong

# Nhập thông tin từ bàn phím
my_email = input('Nhập Mã số sinh viên hoặc Email: ')
my_password = getpass.getpass('Nhập Mật khẩu: ')

# 1. Điền Tên đăng nhập
print(">> Đang điền tên đăng nhập...")
try:
    # Cách 1: Tìm theo tên chuẩn (thường dùng nhất)
    user_box = driver.find_element(By.NAME, "username")
except:
    # Cách 2 (Dự phòng): Tìm ô nhập liệu dạng text đầu tiên xuất hiện
    user_box = driver.find_element(By.CSS_SELECTOR, "input[type='text']")

user_box.clear()
user_box.send_keys(my_email)


# 2. Điền Mật khẩu
print(">> Đang điền mật khẩu...")
try:
    # Cách 1: Tìm theo tên chuẩn
    pass_box = driver.find_element(By.NAME, "password")
except:
    # Cách 2 (Dự phòng): Tìm ô nhập liệu dạng password
    pass_box = driver.find_element(By.CSS_SELECTOR, "input[type='password']")

pass_box.clear()
pass_box.send_keys(my_password)


# 3. CLICK NÚT ĐĂNG NHẬP
print(">> Đang click nút Đăng nhập...")
# Tìm nút có type='submit' (Nút Gửi form) -> Chính xác 100%
login_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
login_btn.click()

print(">> Đã bấm nút. Đang đợi vào trang chủ...")
time.sleep(5)

# Kiểm tra kết quả
if "home" in driver.current_url:
    print("ĐĂNG NHẬP THÀNH CÔNG!")
else:
    print("Có thể chưa thành công hoặc sai mật khẩu. Hãy kiểm tra trình duyệt.")

# Giữ trình duyệt để xem
input("Bấm phím ENTER vào cửa sổ đen này để kết thúc...")
driver.quit()
