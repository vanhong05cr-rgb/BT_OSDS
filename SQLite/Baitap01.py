import sqlite3
# 1. Kết nối tới cơ sở dữ liệu
conn = sqlite3.connect("inventory.db")
# Tạo đối tượng 'cursor' để thực thi các câu lệnh SQL
cursor = conn.cursor()
# 2. Thao tasc voiws Database vaf Table
# Lenh SQL de tao bang products
sql1 = """
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price NUMERIC NOT NULL,
    quantity INTEGER
)
"""
# Thực thi câu lệnh tạo bảng

cursor.execute(sql1)

conn.commit() # Lưu thay đổi vào DB

# 3. CRUD

# 3.1. Thêm (INSERT)

products_data = [

    ("Laptop A100", 999.99, 15),

    ("Mouse Wireless X", 25.50, 50),

    ("Monitor 27-inch", 249.00, 10)

]

# Lệnh SQL để chèn dữ liệu. Dùng '?' để tráng lỗi SQL Injection

sql2 = """

INSERT INTO products (name, price, quantity) 

VALUES

(?, ?, ?)

"""

# THêm nhiều bản ghi cùng lúc

cursor.executemany(sql2, products_data)

conn.commit() # Lưu thay đổi

# 3.2 READ (SELECT)

sql3 = "SELECT * FROM products"

# Thực thi truy vấn

cursor.execute(sql3)

# Lấy tất cả kết quả

all_products = cursor.fetchall()

# In tiêu đề

print(f"{'ID':<4} | {'Tên Sản Phẩm':<20} | {'Giá':<10} | {'Số Lượng':<10}")

# Lặp và in ra

for p in all_products:

    print(f"{p[0]:<4} | {p[1]:<20} | {p[2]:<10} | {p[3]:<10}")


# # Cach nhap truc tiep
# # 3.3 UPDATE
# sql4 = " UPDATE products SET price = 500 WHERE id = 2 "
# # Thực thi truy vấn
# cursor.execute(sql4)
# conn.commit() # Lưu thay đổi vào DB
# # UPDATE tên_bảng
# # SET tên_cột = giá_trị_mới
# # WHERE điều_kiện;

# # 3.4 DELETE
# sql5 = " DELETE FROM products WHERE id = 3"
# # Thực thi truy vấn
# cursor.execute(sql5)
# conn.commit() # Lưu thay đổi vào DB
# # DELETE FROM tên_bảng
# # WHERE điều_kiện;

# Cach nhap gian tiep
# 3.3 UPDATE
sql4 = """
UPDATE products
SET price = ?, quantity = ?
WHERE id = ?
"""

cursor.execute(sql4, (1099.99, 20, 1))  # cập nhật sản phẩm id=1
conn.commit()
print("Đã cập nhật sản phẩm có id = 1")

# 3.4 DELETE
sql5 = """
DELETE FROM products
WHERE id = ?
"""

cursor.execute(sql5, (2,))  # xóa sản phẩm id=2
conn.commit()
print("Đã xóa sản phẩm có id = 2")