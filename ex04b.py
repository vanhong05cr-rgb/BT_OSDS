from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from openpyxl import Workbook
import time

# =============================
# 1. CẤU HÌNH (Giữ nguyên)
# =============================
gecko_path = r"D:/MaNguonMo/BAITAP/geckodriver.exe"
ser = Service(gecko_path)
options = webdriver.FirefoxOptions()
options.binary_location = "C:/Program Files/Mozilla Firefox/firefox.exe"
# options.add_argument("--headless") # Bỏ comment nếu muốn chạy ẩn

driver = webdriver.Firefox(options=options, service=ser)
wait = WebDriverWait(driver, 10)

# =============================
# 2. TRUY CẬP OLD REDDIT
# =============================
# Mẹo: Thêm /top/ để lấy các bài hót nhất, tránh các bài quảng cáo rác
url = "https://old.reddit.com/top/?sort=top&t=day"
print(f"Đang truy cập: {url}")
driver.get(url)

# =============================
# 3. CÀO DỮ LIỆU
# =============================
data = []

try:
    # Ở giao diện cũ, mỗi bài viết nằm trong thẻ div có class là "thing"
    print("Đang quét danh sách bài viết...")
    posts = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.thing")))
    
    print(f"--> Tìm thấy {len(posts)} bài viết.")

    for post in posts:
        try:
            # 1. Lấy Tiêu đề (Nằm trong thẻ p có class "title", rồi vào thẻ a)
            title_element = post.find_element(By.CSS_SELECTOR, "p.title > a")
            title = title_element.text
            link = title_element.get_attribute("href")

            # 2. Lấy Tác giả (Nằm trong class "author")
            # Dùng try-except nhỏ ở đây vì có thể bài viết quảng cáo sẽ không có tác giả
            try:
                author = post.find_element(By.CSS_SELECTOR, "a.author").text
            except:
                author = "Unknown/Ad"

            # 3. Lấy Số Vote (Nằm trong class "score unvoted")
            try:
                score = post.find_element(By.CSS_SELECTOR, "div.score.unvoted").text
                if score == "•": score = "Hidden" # Đôi khi reddit ẩn điểm
            except:
                score = "0"

            # 4. Lấy tên subreddit (Cộng đồng)
            try:
                subreddit = post.find_element(By.CSS_SELECTOR, "a.subreddit").text
            except:
                subreddit = ""

            # Chỉ lấy các bài có tiêu đề rõ ràng
            if title:
                data.append([title, author, score, subreddit, link])
                print(f"Đã lấy: {title[:40]}...")

        except Exception as e:
            # Bỏ qua lỗi nhỏ ở từng bài để code chạy tiếp
            continue

except Exception as e:
    print(f"Lỗi lớn: {e}")

finally:
    driver.quit()

# =============================
# 4. LƯU EXCEL
# =============================
if data:
    wb = Workbook()
    ws = wb.active
    ws.title = "Old Reddit Top"

    ws.append(["Tiêu đề", "Tác giả", "Số Vote", "Subreddit", "Link"])

    for row in data:
        ws.append(row)

    output_path = "old_reddit_data.xlsx"
    wb.save(output_path)
    print(f"Thành công! File đã lưu tại: {output_path}")
else:
    print("Không cào được dữ liệu nào.")