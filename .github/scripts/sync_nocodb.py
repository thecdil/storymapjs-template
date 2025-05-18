import requests
import json
import os
import csv
from datetime import datetime
from collections import defaultdict

def main():
    # Lấy thông tin từ biến môi trường
    domain = os.environ.get("NOCODB_DOMAIN")
    token = os.environ.get("NOCODB_TOKEN")
    table = os.environ.get("NOCODB_TABLE")
    view = os.environ.get("NOCODB_VIEW")
    output_dir = os.environ.get("OUTPUT_DIR", "storymaps")

    # Lấy dữ liệu từ NocoDB
    url = f"https://{domain}/api/v1/db/data/noco/{table}/{view}"
    headers = {"accept": "application/json", "xc-token": token}
    params = {"offset": 0, "limit": 1000}

    print(f"Đang kết nối tới NocoDB API: {url}")
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        print(f"Lỗi API: {response.status_code}")
        print(response.text)
        return 1

    data = response.json()
    print(f"Đã lấy {len(data)} bản ghi từ NocoDB")
    
    # Cấu trúc dữ liệu để lưu trữ slides theo category và thứ tự
    storymaps = defaultdict(list)

    for item in data:
        # Xử lý trường phân loại
        category = item.get('story-map-collect', '').strip()
        if not category:
            continue

        # Lấy thứ tự từ cột story-map-collect-num, mặc định là 999 nếu không có
        try:
            order_num = int(item.get('story-map-collect-num', 999))
        except (ValueError, TypeError):
            order_num = 999

        # Tạo slide từ dữ liệu
        slide = {
            "text": {
                "headline": item.get("Headline", ""),
                "text": item.get("Text", "")
            },
            "location": {
                "name": item.get("Location", ""),
                "lat": float(item.get("Latitude", 0)),
                "lon": float(item.get("Longitude", 0))
            },
            "_order": order_num  # Lưu thứ tự để sắp xếp sau này
        }

        if "Media" in item and item["Media"]:
            slide["media"] = {
                "url": item["Media"],
                "caption": item.get("MediaCaption", ""),
                "credit": item.get("MediaCredit", "")
            }

        # Thêm slide vào category tương ứng
        storymaps[category].append(slide)

    # Tạo thư mục đầu ra
    os.makedirs(output_dir, exist_ok=True)
    
    # Lấy danh sách file hiện có trong thư mục đầu ra
    existing_files = []
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            if file.endswith('.json') or file.endswith('.csv'):
                rel_path = os.path.relpath(os.path.join(root, file), output_dir)
                existing_files.append(rel_path)
    
    # Danh sách file mới sẽ được tạo
    new_files = []
    
    # Tạo và lưu các file
    for category, slides in storymaps.items():
        # Sắp xếp slides theo thứ tự tăng dần
        sorted_slides = sorted(slides, key=lambda x: x.get("_order", 999))
        
        # Loại bỏ trường _order khỏi slides
        for slide in sorted_slides:
            if "_order" in slide:
                del slide["_order"]
        
        # Xác định đường dẫn file
        if category.endswith('.csv'):
            # Xử lý file CSV
            file_path = os.path.join(output_dir, category)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # Viết header
                writer.writerow(['Headline', 'Text', 'Location', 'Latitude', 'Longitude', 'Media', 'MediaCaption', 'MediaCredit'])
                # Viết dữ liệu
                for slide in sorted_slides:
                    writer.writerow([
                        slide['text']['headline'],
                        slide['text']['text'],
                        slide['location']['name'],
                        slide['location']['lat'],
                        slide['location']['lon'],
                        slide.get('media', {}).get('url', ''),
                        slide.get('media', {}).get('caption', ''),
                        slide.get('media', {}).get('credit', '')
                    ])
            
            print(f"Đã tạo file CSV: {file_path}")
            new_files.append(os.path.relpath(file_path, output_dir))
        else:
            # Xử lý file JSON
            if category.endswith('.json'):
                file_name = category
            else:
                file_name = f"{category}.json"
                
            # Tạo thư mục con nếu cần
            file_path = os.path.join(output_dir, file_name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Tạo overview slide
            overview_slide = {
                "type": "overview",
                "text": {
                    "headline": f"Bản đồ {os.path.basename(category).replace('-', ' ').replace('.json', '').title()}",
                    "text": f"Bản đồ tổng quan về {os.path.basename(category).replace('-', ' ').replace('.json', '')}"
                }
            }
            
            # Tạo cấu trúc StoryMap hoàn chỉnh
            storymap_data = {
                "storymap": {
                    "slides": [overview_slide] + sorted_slides
                }
            }
            
            # Lưu file JSON
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(storymap_data, f, ensure_ascii=False, indent=2)
            
            print(f"Đã tạo file JSON: {file_path} với {len(sorted_slides)} slides đã sắp xếp")
            new_files.append(os.path.relpath(file_path, output_dir))

    # Ghi log
    log_path = os.path.join(output_dir, 'sync_log.txt')
    with open(log_path, 'a') as log:
        log.write(f"{datetime.now()}: Đồng bộ {len(data)} bản ghi thành {len(storymaps)} files\n")
    
    # Xác định file cần xóa (có trong existing_files nhưng không có trong new_files)
    files_to_delete = set(existing_files) - set(new_files)
    for file_to_delete in files_to_delete:
        try:
            os.remove(os.path.join(output_dir, file_to_delete))
            print(f"Đã xóa file không còn trong dữ liệu: {file_to_delete}")
        except Exception as e:
            print(f"Lỗi khi xóa file {file_to_delete}: {e}")
    
    return 0

if __name__ == "__main__":
    exit(main())
