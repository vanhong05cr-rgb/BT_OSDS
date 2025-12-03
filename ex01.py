# from selenium import webdriver
# from selenium.webdriver.firefox.options import Options
# import time

# # 1. Tạo tùy chọn (Options)
# options = Options()
# # Chỉ trỏ đường dẫn Firefox nếu nó không cài ở thư mục mặc định. 
# # Nếu cài mặc định thì dòng dưới đây có thể bỏ qua (comment lại).
# options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe" 

# # 2. Khởi tạo driver (KHÔNG CẦN Service, KHÔNG CẦN chỉ đường dẫn geckodriver)
# # Selenium sẽ tự tải geckodriver phù hợp về máy
# driver = webdriver.Firefox(options=options)

# try:
#     # 3. Truy cập web
#     url = 'http://pythonscraping.com/pages/javascript/ajaxDemo.html'
#     driver.get(url)

#     print("Before: ================================\n")
#     print(driver.page_source) # Tạm ẩn để dễ nhìn log

#     time.sleep(3)

#     print("\n\nAfter: ================================\n")
#     print("Đã chạy thành công! Trang web đã tải xong.")

# except Exception as e:
#     print(f"Có lỗi xảy ra: {e}")

# finally:
#     # 4. Đóng trình duyệt
#     driver.quit()
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
import time
# Đường dẫn đến file thực thi geckodriver
gecko_path = r"D:/MaNguonMo/BAITAP/geckodriver.exe"
# Khởi tởi đối tượng dịch vụ với đường geckodriver
ser = Service(gecko_path)
# Tạo tùy chọn
options = webdriver.firefox.options.Options()
options.binary_location = "C:\\Program Files\\Mozilla Firefox\\firefox.exe"
# Thiết lập firefox chỉ hiện thị giao diện
options.headless = False
# Khởi tạo driver
driver = webdriver.Firefox(options = options, service=ser)
# Tạo url
url = 'http://pythonscraping.com/pages/javascript/ajaxDemo.html'
# Truy cập
driver.get(url)
# In ra nội dung của trang web
print("Before: ================================\n")
print(driver.page_source)
# Tạm dừng khoảng 3 giây
time.sleep(3)
# In lai
print("\n\n\n\nAfter: ================================\n")
print(driver.page_source)
# Đóng browser
driver.quit()