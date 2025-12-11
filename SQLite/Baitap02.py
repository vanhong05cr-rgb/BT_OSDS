import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import string
import re
import time
import os # Thêm thư viện để kiểm tra/xóa file DB (tùy chọn)

######################################################
## I. Cấu hình và Chuẩn bị
######################################################

# Thiết lập tên file DB và Bảng
DB_FILE = 'Painters_Data.db'
TABLE_NAME = 'painters_info'


# Nếu muốn bắt đầu với DB trống, có thể xóa file cũ (Tùy chọn)
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)
    print(f"Đã xóa file DB cũ: {DB_FILE}")

# Mở kết nối SQLite và tạo bảng nếu chưa tồn tại
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Tạo bảng
create_table_sql = f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    name TEXT PRIMARY KEY, -- Sử dụng tên làm khóa chính để tránh trùng lặp
    birth TEXT,
    death TEXT,
    nationality TEXT
);
"""
cursor.execute(create_table_sql)
conn.commit()
print(f"Đã kết nối và chuẩn bị bảng '{TABLE_NAME}' trong '{DB_FILE}'.")

# Hàm đóng driver an toàn
def safe_quit_driver(driver):
    try:
        if driver:
            driver.quit()
    except:
        pass
print("\n--- Bắt đầu Lấy Đường dẫn ---")


## ==========================================
## 2. LẤY DANH SÁCH LINK 
## ==========================================

driver = webdriver.Chrome() # Khởi tạo driver
all_links = []

for letter in string.ascii_uppercase:
    url = f"https://en.wikipedia.org/wiki/List_of_painters_by_name_beginning_with_%22{letter}%22"
    driver.get(url)
    time.sleep(2)

    try:
        # Dùng WebDriverWait để đảm bảo list đã tải xong (từ Code I - rất tốt)
        anchors = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#mw-content-text .div-col li > a")))
    
        # Lọc link rác ngay lập tức
    
        for a in anchors:
            href = a.get_attribute("href")
            if href and "/wiki/" in href and "User:" not in href and "File:" not in href:
                all_links.append(href)
    except:
        print(f"⚠ Không tìm thấy danh sách trên trang {letter}")


# Khử trùng lặp
all_links = list(set(all_links))
print(f"--- Tìm thấy {len(all_links)} họa sĩ khả dụng ---")

# ==========================================
# 3. LẤY THÔNG TIN CHI TIẾT
# ==========================================

print("\n--- Bắt đầu cào thông tin chi tiết ---")
count = 0
# Chạy thử 20 người đầu tiên
for link in all_links:
    # if count >= 20: 
    #     break   
    count += 1
    print(f"[{count}] Đang xử lý: {link}")
        
    try:
        driver.get(link)
        # Không cần sleep quá lâu nếu mạng tốt, 1s là đủ lịch sự
        time.sleep(1) 

        # --- A. Lấy Tên ---
        try:
            name = driver.find_element(By.TAG_NAME, "h1").text
        except:
            name = ""

        # --- B. Lấy Năm Sinh (Born) ---
        try:
            birth_element = driver.find_element(By.XPATH, "//th[text()='Born']/following-sibling::td")
            birth_text = birth_element.text
            # Regex an toàn: Nếu tìm thấy thì lấy, không thì giữ nguyên text gốc
            res = re.findall(r'[0-9]{1,2}\s+[A-Za-z]+\s+[0-9]{4}', birth_text)
            birth = res[0] if res else birth_text
        except:
            birth = ""
            birth_text = "" # Để dùng cho fallback quốc tịch

        # --- C. Lấy Năm Mất (Died) ---
        try:
            death_element = driver.find_element(By.XPATH, "//th[text()='Died']/following-sibling::td")
            death_text = death_element.text
            res = re.findall(r'[0-9]{1,2}\s+[A-Za-z]+\s+[0-9]{4}', death_text)
            death = res[0] if res else death_text
        except:
            death = ""

        # --- D. Lấy Quốc Tịch (Nationality) ---
        nationality = ""
        try:
            # Cách 1: Tìm dòng Nationality riêng
            nat_element = driver.find_element(By.XPATH, "//th[text()='Nationality']/following-sibling::td")
            nationality = nat_element.text.strip()
        except:
            # Cách 2 (Fallback): Lấy từ địa điểm sinh (Logic từ Code II)
            if "," in birth_text:
                nationality = birth_text.split(",")[-1].strip()
       
        # 5. LƯU TỨC THỜI VÀO SQLITE
        insert_sql = f"""
        INSERT OR IGNORE INTO {TABLE_NAME} (name, birth, death, nationality) 
        VALUES (?, ?, ?, ?);
        """
        # Sử dụng 'INSERT OR IGNORE' để bỏ qua nếu Tên (PRIMARY KEY) đã tồn tại
        cursor.execute(insert_sql, (name, birth, death, nationality))
        conn.commit()
        print(f"  --> Đã lưu thành công: {name}")

    except Exception as e:
        print(f"Lỗi khi xử lý hoặc lưu họa sĩ {link}: {e}")

print("\nHoàn tất quá trình cào và lưu dữ liệu tức thời.")  


# A. Yêu Cầu Thống Kê và Toàn Cục

print("\n======================")
print("A. Thống kê và Kiểm tra")
print("======================")

# 1. Đếm tổng số họa sĩ đã được lưu trữ trong bảng.
count_sql = "SELECT COUNT(*) FROM painters_info"
cursor.execute(count_sql)
ket_qua = cursor.fetchone()
print("1) Tổng số họa sĩ đã được lưu trữ trong bảng là:", ket_qua[0])

# 2. Hiển thị 5 dòng dữ liệu đầu tiên để kiểm tra cấu trúc và nội dung bảng.
sql2 = "SELECT * FROM painters_info LIMIT 5"

df = pd.read_sql_query(sql2, conn)
print("--- Kiểm tra cấu trúc và dữ liệu ---")
print(df)

# 3. Liệt kê danh sách các quốc tịch duy nhất có trong tập dữ liệu.
print("\n3) Danh sách quốc tịch:")
sql3 = "SELECT DISTINCT nationality FROM painters_info"
cursor.execute(sql3)
ket_qua = cursor.fetchall()
for row in ket_qua:
    print(" -", row[0])

# B. Yêu Cầu Lọc và Tìm Kiếm

print("\n======================")
print("B. Lọc và Tìm kiếm")
print("======================")

# 4. Tìm và hiển thị tên của các họa sĩ có tên bắt đầu bằng ký tự 'F'.
print("\n4) Họa sĩ tên bắt đầu bằng F:")
sql4 = "SELECT name FROM painters_info WHERE name LIKE 'F%'"
cursor.execute(sql4)
ket_qua = cursor.fetchall()
for row in ket_qua:
    print(" -", row[0])

# 5. Tìm và hiển thị tên và quốc tịch của những họa sĩ có quốc tịch chứa từ khóa 'French' (ví dụ: French, French-American).
print("\n5) Quốc tịch chứa French:")
sql5 = "SELECT name, nationality FROM painters_info WHERE nationality LIKE '%French%'"
cursor.execute(sql5)
ket_qua = cursor.fetchall()
for name, nationality in ket_qua:
    print(f"Tên họa sĩ: {name} | Quốc tịch: {nationality}")

# 6. Hiển thị tên của các họa sĩ không có thông tin quốc tịch (hoặc để trống, hoặc NULL).
print("\n6) Không có quốc tịch:")
sql6 = "SELECT * FROM painters_info WHERE nationality = '' OR nationality IS NULL"
cursor.execute(sql6)
ket_qua = cursor.fetchall()
for row in ket_qua:
    print(" -", row[0])

# 7. Tìm và hiển thị tên của những họa sĩ có cả thông tin ngày sinh và ngày mất (không rỗng).
print("\n7) Có đủ Birth + Death:")
sql7 = "SELECT * FROM painters_info WHERE birth != '' AND death != ''"
cursor.execute(sql7)
ket_qua = cursor.fetchall()
for row in ket_qua:
    print(" -", row[0])

# 8. Hiển thị tất cả thông tin của họa sĩ có tên chứa từ khóa '%Fales%'
print("\n8) Tên chứa 'Fales':")
sql8 = "SELECT * FROM painters_info WHERE name LIKE '%Fales%'"
cursor.execute(sql8)
ket_qua = cursor.fetchall()
for row in ket_qua:
    print(" -", row[0])

# C. Yêu Cầu Nhóm và Sắp Xếp


print("\n======================")
print("C. Nhóm và Sắp xếp")
print("======================")

# 9. Sắp xếp và hiển thị tên của tất cả họa sĩ theo thứ tự bảng chữ cái (A-Z).
print("\n9) Danh sách tên A-Z:")
sql9 = "SELECT name FROM painters_info ORDER BY name ASC"
cursor.execute(sql9)
ket_qua = cursor.fetchall()
for row in ket_qua:
    print(" -", row[0])

# 10. Nhóm và đếm số lượng họa sĩ theo từng quốc tịch.
print("\n10) Đếm số họa sĩ theo quốc tịch:")
sql10 = "SELECT nationality, COUNT(*) FROM painters_info GROUP BY nationality"
cursor.execute(sql10)
ket_qua = cursor.fetchall()
for row in ket_qua:
    print(f"Quốc tịch: {row[0]} - Số lượng: {row[1]}")

# Đóng kết nối cuối cùng
driver.quit()
conn.close()
print("\nĐã đóng kết nối cơ sở dữ liệu.")
