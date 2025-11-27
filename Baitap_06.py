from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import re
import time

# ==========================================
# 1. KHỞI TẠO
# ==========================================
# Dùng list để lưu tạm dữ liệu (Nhanh hơn pd.concat gấp nhiều lần)
data_list = []
driver = webdriver.Chrome()

# URL cần cào
url = "https://en.wikipedia.org/wiki/List_of_painters_by_name_beginning_with_%22F%22"

print("--- BẮT ĐẦU CÀO DỮ LIỆU ---")

try:
    # ==========================================
    # 2. LẤY DANH SÁCH LINK 
    # ==========================================
    driver.get(url)
    
    # Dùng WebDriverWait để đảm bảo list đã tải xong (từ Code I - rất tốt)
    anchors = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#mw-content-text .div-col li > a"))
    )
    
    # Lọc link rác ngay lập tức
    all_links = []
    for a in anchors:
        href = a.get_attribute("href")
        if href and "/wiki/" in href and "User:" not in href and "File:" not in href:
            all_links.append(href)

    # Khử trùng lặp
    all_links = list(set(all_links))
    print(f"--- Tìm thấy {len(all_links)} họa sĩ khả dụng ---")

    # ==========================================
    # 3. LẤY THÔNG TIN CHI TIẾT
    # ==========================================
    count = 0
    # Chạy thử 5 người đầu tiên (Xóa dòng if bên dưới để chạy hết)
    for link in all_links:
        if count >= 5: 
            break
        
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

            # --- E. Lưu vào List tạm ---
            painter_info = {
                'name': name,
                'birth': birth,
                'death': death,
                'nationality': nationality,
                # 'link': link
            }
            data_list.append(painter_info)

        except Exception as e:
            print(f"Lỗi khi xử lý link {link}: {e}")
            continue

except Exception as e:
    print(f"Lỗi hệ thống: {e}")

finally:
    # Luôn đóng driver dù có lỗi hay không
    driver.quit()

# ==========================================
# 4. XUẤT FILE
# ==========================================
if data_list:
    d = pd.DataFrame(data_list)
    print(d)

    # Determining the name of the file
    file_name = 'Painters.xlsx'

    # Saving the excel
    d.to_excel(file_name)
    print('DataFrame is written to Excel File successfully.')

else:
    print("Không lấy được dữ liệu nào.")