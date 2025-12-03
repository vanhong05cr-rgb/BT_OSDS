# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import time
# import pandas as pd

# # Đọc danh sách mã vạch
# with open("ma_vach.txt", "r") as f:
#     barcodes = [x.strip() for x in f.readlines()]

# driver = webdriver.Chrome()
# driver.get("https://shop.gochek.vn/products")

# data = []

# for code in barcodes:
#     try:
#         # print("Đang cào:", code)

#         # # Nhập mã
#         # input_box = WebDriverWait(driver, 10).until(
#         #     EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Nhập mã vạch, QR code...']"))
#         # )
#         # input_box.clear()
#         # input_box.send_keys(code)

#         # Bấm tìm kiếm
#         search_btn = driver.find_element(By.XPATH, "//button[contains(@class,'btn-search')]")
#         search_btn.click()

#         # Đợi kết quả load
#         time.sleep(2)

#         # Lấy dữ liệu
#         try:
#             name = driver.find_element(By.XPATH, "//div[@class='info-product']//h1").text
#         except:
#             name = "Không tìm thấy"

#         try:
#             brand = driver.find_element(By.XPATH, "//div[contains(text(),'Thương hiệu')]/following-sibling::div").text
#         except:
#             brand = ""

#         try:
#             origin = driver.find_element(By.XPATH, "//div[contains(text(),'Xuất xứ')]/following-sibling::div").text
#         except:
#             origin = ""

#         try:
#             img = driver.find_element(By.XPATH, "//div[contains(@class,'image-product')]//img").get_attribute("src")
#         except:
#             img = ""

#         data.append([code, name, brand, origin, img])

#     except Exception as e:
#         print("Lỗi:", e)

# # Lưu file CSV
# df = pd.DataFrame(data, columns=["Ma_vach", "Ten", "Thuong_hieu", "Xuat_xu", "Hinh_anh"])
# df.to_csv("ket_qua_gocheck.csv", index=False)

# driver.quit()

# print("Hoàn thành!")

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import time
import pandas as pd
# # Đường dẫn đến file thực thi geckodriver
# gecko_path = r"D:/MaNguonMo/BAITAP/geckodriver.exe"

# # Khởi tởi đối tượng dịch vụ với đường geckodriver
# ser = Service(gecko_path)

# # Tạo tùy chọn
# options = webdriver.firefox.options.Options();
# options.binary_location ="C:/Program Files/Mozilla Firefox/firefox.exe"
# # gecko_path = r"C:/Users/user/OneDrive/Desktop/ma nguon mo/firefox/geckodriver.exe"
# service = Service(gecko_path)
# options = Options()
# options.headless = False  

# driver = webdriver.Firefox(service=service, options=options)
# Đường dẫn đến file thực thi geckodriver
gecko_path = r"D:/MaNguonMo/BAITAP/geckodriver.exe"

# Khởi tởi đối tượng dịch vụ với đường geckodriver
ser = Service(gecko_path)

# Tạo tùy chọn
options = webdriver.firefox.options.Options();
options.binary_location ="C:/Program Files/Mozilla Firefox/firefox.exe"
# Thiết lập firefox chỉ hiện thị giao diện
options.headless = False

# Khởi tạo driver
driver = webdriver.Firefox(options = options, service=ser)
url = "https://gochek.vn/collections/all"
driver.get(url)
time.sleep(3)

SCROLL_PAUSE_TIME = 2
last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(SCROLL_PAUSE_TIME)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

time.sleep(1)

cards = driver.find_elements(By.XPATH,
    "//div[.//img and (.//h3 or .//h2) and .//*[contains(text(),'₫')]]"
)

print(f"{len(cards)}")

data = []
for card in cards:
    try:
        # Tên sản phẩm
        name = ""
        try:
            name = card.find_element(By.TAG_NAME, "h3").text.strip()
        except:
            name = card.find_element(By.TAG_NAME, "h2").text.strip()
    except:
        continue
    
    # Ảnh sản phẩm
    img = ""
    try:
        img = card.find_element(By.TAG_NAME, "img").get_attribute("src")
    except:
        img = ""
    
    # Giá sản phẩm
    price = ""
    try:
        texts = card.text.split()
        for t in texts:
            if "₫" in t:
                price = t
                break
    except:
        price = ""
    
    if name:
        data.append({
            "Tên sản phẩm": name,
            "Giá bán": price,
            "Hình ảnh": img
        })

# Loại bỏ trùng theo tên sản phẩm 
df = pd.DataFrame(data)
df_unique = df.drop_duplicates(subset=['Tên sản phẩm']).reset_index(drop=True)

df_unique.to_excel("gochek_all_products_unique.xlsx", index=False)
driver.quit()

# from selenium import webdriver
# from selenium.webdriver.firefox.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import time
# from openpyxl import Workbook

# # =============================
# #   FIREFOX + GECKODRIVER
# # =============================
# # Đường dẫn đến file thực thi geckodriver
# gecko_path = r"D:/MaNguonMo/BAITAP/geckodriver.exe"

# # Khởi tởi đối tượng dịch vụ với đường geckodriver
# ser = Service(gecko_path)

# # Tạo tùy chọn
# options = webdriver.firefox.options.Options();
# options.binary_location ="C:/Program Files/Mozilla Firefox/firefox.exe"
# # Thiết lập firefox chỉ hiện thị giao diện
# options.headless = False

# # Khởi tạo driver
# driver = webdriver.Firefox(options = options, service=ser)

# wait = WebDriverWait(driver, 10)

# # =============================
# #       LOGIN WEBSITE
# # =============================
# driver.get("https://quotes.toscrape.com/login")

# wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys("myuser")
# driver.find_element(By.ID, "password").send_keys("mypassword")
# driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

# print("⏳ Đang đăng nhập...")
# time.sleep(2)

# if "Logout" in driver.page_source or "logout" in driver.page_source:
#     print("ĐĂNG NHẬP THÀNH CÔNG!")
# else:
#     print("ĐĂNG NHẬP THẤT BẠI!")
#     driver.quit()
#     exit()

# # =============================
# #        CÀO QUOTES
# # =============================
# quotes = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "quote")))

# data = []  # để lưu tạm vào list

# for q in quotes:
#     quote_text = q.find_element(By.CLASS_NAME, "text").text
#     author = q.find_element(By.CLASS_NAME, "author").text

#     tags = q.find_elements(By.CSS_SELECTOR, ".tags a.tag")
#     tag_list = ", ".join([t.text for t in tags])

#     data.append([quote_text, author, tag_list])

# driver.quit()

# # =============================
# #        LƯU EXCEL
# # =============================
# wb = Workbook()
# ws = wb.active
# ws.title = "Quotes"

# # Header
# ws.append(["Quote", "Author", "Tags"])

# # Data rows
# for row in data:
#     ws.append(row)

# # Lưu file
# output_path = "quotes_data.xlsx"
# wb.save(output_path)

# print(f"File Excel đã được lưu thành công: {output_path}")