import sqlite3
import time
import re
import os
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# --- 1. CẤU HÌNH ---
DB_FILE = 'longchau_db.sqlite'
TABLE_NAME = 'products'  # Đặt tên bảng thống nhất là 'products'
GECKO_PATH = r"D:/MaNguonMo/BAITAP/geckodriver.exe"
FIREFOX_PATH = r"C:/Program Files/Mozilla Firefox/firefox.exe"

# --- 2. KHỞI TẠO DATABASE ---
if os.path.exists(DB_FILE):
    os.remove(DB_FILE) # Xóa làm mới để test cho sạch
    print(f"[*] Đã xóa file DB cũ: {DB_FILE}")

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Tạo bảng 
sql_create = f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        id TEXT,
        product_name TEXT,
        price REAL,
        original_price REAL,
        unit TEXT,
        product_url TEXT PRIMARY KEY,
        image_url TEXT,
        crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
"""

cursor.execute(sql_create)
conn.commit()
print(f"[*] Đã tạo bảng '{TABLE_NAME}' thành công.")

# --- 3. KHỞI TẠO SELENIUM ---
ser = Service(GECKO_PATH)
options = webdriver.FirefoxOptions()
options.binary_location = FIREFOX_PATH
options.headless = False 

driver = webdriver.Firefox(options=options, service=ser)
url = 'https://nhathuoclongchau.com.vn/thuc-pham-chuc-nang/vitamin-khoang-chat'

try:
    print(f"[*] Đang truy cập: {url}")
    driver.get(url)
    time.sleep(2)

    # --- 4. CUỘN TRANG & CLICK XEM THÊM ---
    body = driver.find_element(By.TAG_NAME, "body")
    
    # Click xem thêm 
    for k in range(15):
        try:
            buttons = driver.find_elements(By.TAG_NAME, "button")
            for btn in buttons:
                if "Xem thêm" in btn.text and "sản phẩm" in btn.text:
                    driver.execute_script("arguments[0].click();", btn)
                    time.sleep(2)
                    print(f" -> Đã click 'Xem thêm' lần {k+1}")
                    break
        except: pass
    
    # Cuộn trang
    print("[*] Đang cuộn trang...")
    for i in range(50):
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(0.2)
    time.sleep(2)

    # --- 5. TÌM NÚT CHỌN MUA ĐỂ XÁC ĐỊNH VỊ TRÍ SP ---
    buttons = driver.find_elements(By.XPATH, "//button[text()='Chọn mua']")
    print(f"[*] Tìm thấy {len(buttons)} sản phẩm. Bắt đầu lưu...")

    # --- 6. VÒNG LẶP XỬ LÝ TỪNG SẢN PHẨM ---
    for i, bt in enumerate(buttons, 1):
        try:
            # Tìm thẻ cha chứa thông tin
            parent_div = bt
            for _ in range(3):
                parent_div = parent_div.find_element(By.XPATH, "./..")
            sp = parent_div
            
            # --- [QUAN TRỌNG] Lấy toàn bộ text để xử lý ---
            full_text = sp.text 

            # A. Lấy Tên SP
            try:
                tsp = sp.find_element(By.TAG_NAME, 'h3').text
            except:
                tsp = "No Name"

            # B. Lấy URL & ID
            try:
                p_url = sp.find_element(By.TAG_NAME, 'a').get_attribute('href')
                # Tách ID từ URL (VD: ...-30144.html -> 30144)
                p_id = p_url.split('-')[-1].replace('.html', '')
            except:
                p_url = f"unknown_{i}"
                p_id = str(i)

            # D. XỬ LÝ GIÁ & UNIT (Logic Regex)
            price_number = 0
            original_price = 0
            unit = "Không xác định"

            lines = full_text.split('\n')
            for line in lines:
                if 'đ' in line:
                    clean_line = line.replace('.', '').replace(',', '')
                    # Tìm số trong dòng
                    numbers = re.findall(r'\d+', clean_line)
                    if numbers:
                        found_price = float(numbers[0])
                        
                        # Nếu có dấu /, đây là giá chính kèm đơn vị
                        if '/' in line:
                            price_number = found_price
                            unit = line.split('/')[-1].strip().replace('đ', '')
                        # Nếu chưa có giá, lấy tạm số đầu tiên tìm thấy
                        elif price_number == 0:
                            price_number = found_price

            # E. Xử lý Giá Gốc (Class gạch ngang)
            try:
                org_elem = sp.find_element(By.CSS_SELECTOR, ".line-through")
                org_text = org_elem.text.replace('.', '').replace('đ', '').strip()
                original_price = float(re.findall(r'\d+', org_text)[0])
            except:
                original_price = 0

            # --- 7. LƯU TỨC THỜI VÀO DB ---
            if tsp:
                sql = f'''
                    INSERT OR IGNORE INTO {TABLE_NAME}
                    (id, product_name, price, original_price, unit, product_url)
                    VALUES (?, ?, ?, ?, ?, ?)
                '''
                cursor.execute(sql, (p_id, tsp, price_number, original_price, unit, p_url))
                conn.commit() # Commit ngay lập tức
                print(f"[{i}] Đã lưu: {tsp[:30]}... | {price_number}")

        except Exception as e:
            # print(f"Lỗi sp {i}: {e}") # Có thể bật lên để debug
            continue

except Exception as e:
    print(f"Lỗi chương trình: {e}")

print("\nHoàn tất quá trình cào và lưu dữ liệu tức thời.")  


# --- NHÓM 1: KIỂM TRA CHẤT LƯỢNG (Quality Check) ---

print("\n" + "-"*30)
print("Nhóm 1: Kiểm Tra Chất Lượng Dữ Liệu (Bắt buộc)")
print("-" * 30)

# 1.a. Kiểm tra trùng lặp theo URL
print("\n1.a. Kiểm tra trùng lặp theo URL")
sql_1a = "SELECT product_url, COUNT(*) FROM products GROUP BY product_url HAVING COUNT(*) > 1;"
cursor.execute(sql_1a)
ket_qua = cursor.fetchall()
for row in ket_qua:
    print(f"- {row[0]} (Lặp {row[1]} lần)")

# 1.b. Kiểm tra trùng lặp theo tên
print("\n1.a. Kiểm tra trùng lặp theo tên")
sql_1b = "SELECT product_name, COUNT(*) FROM products GROUP BY product_name HAVING COUNT(*) > 1;"
cursor.execute(sql_1b)
ket_qua = cursor.fetchall()
for row in ket_qua:
    print(f"- {row[0]} (Lặp {row[1]} lần)")

# 2. Đếm sản phẩm bị thiếu giá bán
print("\n2. Kiểm tra dữ liệu thiếu (Giá = 0):")
sql_2 = "SELECT COUNT(*) FROM products WHERE price IS NULL OR price = 0"
cursor.execute(sql_2)
so_luong_loi = cursor.fetchone()[0]
if so_luong_loi > 0:
    print(f"Có {so_luong_loi} sản phẩm chưa lấy được giá (Giá = 0).")
else:
    print("Tất cả sản phẩm đều có giá.")

# 3. Giá bán > giá gốc (lỗi)
print("\n3. Kiểm tra logic giá (Giá bán > Giá gốc):")
sql_3 = "SELECT product_name, price, original_price FROM products WHERE original_price > 0 AND price > original_price"
cursor.execute(sql_3)
ds_loi_gia = cursor.fetchall()
print(f"Có {len(ds_loi_gia)} sản phẩm giá bất thường")
for row in ds_loi_gia:
    print(f" - {row[0]}: Bán {row[1]} > Gốc {row[2]}")

# 4. Kiểm tra sự nhất quán của Đơn vị tính
print("\n4. Danh sách các đơn vị tính (Unit):")
sql_4 = "SELECT DISTINCT unit FROM products"
cursor.execute(sql_4)
ds_unit = cursor.fetchall()
print("Các loại đơn vị tìm thấy:", end=" ")
# Dùng list comprehension để in đẹp hơn
print(", ".join([row[0] for row in ds_unit]))

# 5. Tổng số lượng bản ghi
print("\n5. Tổng số lượng sản phẩm:")
sql_5 = "SELECT COUNT(*) FROM products"
cursor.execute(sql_5)
tong_sp = cursor.fetchone()[0]
print(f"Đã cào được tổng cộng: {tong_sp} sản phẩm.")

# --- NHÓM 2: KHẢO SÁT VÀ PHÂN TÍCH ---

print("\n" + "-"*30)
print("Nhóm 2: Khảo sát và Phân Tích (Bổ sung)")
print("-" * 30)

# 6. Top 10 sản phẩm giảm giá mạnh nhất (theo số tiền)
print("\n6. Top 10 sản phẩm giảm giá nhiều nhất (VNĐ):")
sql_6 = """
    SELECT product_name, (original_price - price) as giam_gia 
    FROM products 
    WHERE original_price > 0 
    ORDER BY giam_gia DESC LIMIT 10
"""
cursor.execute(sql_6)
results = cursor.fetchall()
for row in results:
    print(f" - Giảm {row[1]:,.0f}đ: {row[0]}") # format :,.0f để thêm dấu phẩy hàng nghìn

# 7. Sản phẩm đắt nhất
print("\n7. Sản phẩm có giá bán cao nhất:")
sql_7 = "SELECT product_name, price FROM products ORDER BY price DESC LIMIT 1"
cursor.execute(sql_7)
row = cursor.fetchone()
print(f"{row[0]} - Giá: {row[1]:,.0f}đ")

# 8. Thống kê theo Đơn vị tính
print("\n8. Số lượng sản phẩm theo từng Đơn vị:")
sql_8 = "SELECT unit, COUNT(*) FROM products GROUP BY unit"
cursor.execute(sql_8)
results = cursor.fetchall()
for row in results:
    print(f" - {row[0]}: {row[1]} sản phẩm")

# 9. Tìm kiếm sản phẩm "Vitamin C"
print(f"\n9. Tìm kiếm sản phẩm chứa Vitamin C:")
sql_9 = "SELECT product_name, price FROM products WHERE product_name LIKE '%Vitamin C%'"
cursor.execute(sql_9)
results = cursor.fetchall()
print(f"Tìm thấy {len(results)} sản phẩm:")
for row in results[:5]: # Chỉ in 5 cái đầu tiên cho gọn
    print(f"   * {row[0]} ({row[1]:,.0f}đ)")

# 10. Lọc sản phẩm giá 100k - 200k
print("\n10. Sản phẩm giá từ 100k - 200k:")
sql_10 = "SELECT product_name, price FROM products WHERE price BETWEEN 100000 AND 200000 LIMIT 5"
cursor.execute(sql_10)
results = cursor.fetchall()
for row in results:
    print(f" - {row[0]} ({row[1]:,.0f}đ)")

# --- NHÓM 3: TRUY VẤN NÂNG CAO ---

print("\n" + "-"*30)
print("Nhóm 3: Các Truy vấn Nâng cao (Tùy chọn)")
print("-" * 30)

# 11. Sắp xếp giá tăng dần
print("\n11. Các sản phẩm theo Giá bán từ thấp đến cao:")
sql_11 = "SELECT product_name, price FROM products ORDER BY price ASC"
cursor.execute(sql_11)
results = cursor.fetchall()
for row in results:
    print(f" - {row[1]:,.0f}đ: {row[0]}")

# 12. Top 5 sản phẩm có % giảm giá cao nhất
print("\n12. Top 5 sản phẩm có % giảm giá cao nhất:")
sql_12 = """
    SELECT product_name, ROUND(((original_price - price) * 100.0 / original_price), 1) as phan_tram
    FROM products 
    WHERE original_price > 0 
    ORDER BY phan_tram DESC LIMIT 5
"""
cursor.execute(sql_12)
results = cursor.fetchall()
for row in results:
    print(f" - Giảm {row[1]}%: {row[0]}")

# 13. Xóa bản ghi trùng lặp 
print("\n13. Thực hiện xóa bản ghi trùng lặp (giữ bản ghi mới nhất)...")
sql_13 = """
    DELETE FROM products
    WHERE rowid NOT IN (
        SELECT MAX(rowid) FROM products GROUP BY product_url
    )
"""
cursor.execute(sql_13)
conn.commit()
print(f"Đã thực thi. Số dòng bị xóa: {cursor.rowcount}")

# 14. Phân tích nhóm giá 
print("\n14. Phân bố sản phẩm theo nhóm giá:")
sql_14 = """
    SELECT 
        CASE 
            WHEN price < 100000 THEN 'Dưới 100k'
            WHEN price BETWEEN 100000 AND 300000 THEN '100k - 300k'
            ELSE 'Trên 300k'
        END as nhom_gia,
        COUNT(*) 
    FROM products
    GROUP BY nhom_gia
"""
cursor.execute(sql_14)
results = cursor.fetchall()
for row in results:
    print(f" - Nhóm {row[0]}: {row[1]} sản phẩm")

# 15. Tìm URL lỗi
print("\n15. Kiểm tra URL bị lỗi (NULL hoặc rỗng):")
sql_15 = "SELECT id, product_name FROM products WHERE product_url IS NULL OR product_url = ''"
cursor.execute(sql_15)
results = cursor.fetchall()
print(f"Có {len(results)} bản ghi lỗi URL.")


# Đóng kết nối cuối cùng
driver.quit()
conn.close()
print("\nĐã đóng kết nối cơ sở dữ liệu.")
