import csv
import sys
import re
import os

def clean_csv(input_file, keyword):
    # 讀取CSV檔案
    with open(input_file, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)
    
    # 過濾資料
    cleaned_rows = []
    for row in rows:
        # 檢查價格是否超過5000
        try:
            price = float(row['price'])
            if price > 5000:
                continue
        except ValueError:
            continue
        
        # 檢查商品名稱是否包含完整關鍵字
        if keyword in row['product_name']:
            cleaned_rows.append(row)
    
    # 在原檔案名稱上加上標記
    file_name, file_ext = os.path.splitext(input_file)
    output_file = f"{file_name}_cleaned{file_ext}"
    
    # 寫入新的CSV檔案
    with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(cleaned_rows)
    
    return output_file

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("使用方法: python clean_csv.py <輸入檔案> <關鍵字>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    keyword = sys.argv[2]
    
    output_file = clean_csv(input_file, keyword)
    print(f"清理完成！結果已儲存至 {output_file}") 