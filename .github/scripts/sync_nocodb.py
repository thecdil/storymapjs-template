import requests
import json
import os
import csv
from datetime import datetime
from collections import defaultdict
from urllib.parse import urlparse

def main():
    # Lấy thông tin từ biến môi trường
    domain = os.environ.get("NOCODB_DOMAIN")
    token = os.environ.get("NOCODB_TOKEN")
    table_id = os.environ.get("NOCODB_TABLE_ID")
    output_dir = os.environ.get("OUTPUT_DIR", "storymaps")
    
    # Kiểm tra các biến môi trường bắt buộc
    if not domain:
        print("Lỗi: Thiếu biến môi trường NOCODB_DOMAIN")
        return 1
    if not token:
        print("Lỗi: Thiếu biến môi trường NOCODB_TOKEN")
        return 1
    if not table_id:
        print("Lỗi: Thiếu biến môi trường NOCODB_TABLE_ID")
        return 1
    
    # Xử lý URL chuẩn
    parsed = urlparse(domain)
    if parsed.scheme:
        domain = parsed.netloc
    
    # Cấu hình API endpoint
    url = f"https://{domain}/api/v2/tables/{table_id}/records"
    
    headers = {
        "xc-token": token,
        "Accept": "application/json"
    }
    
    params = {
        "limit": 1000  # Lấy tối đa 1000 bản ghi
    }

    print(f"Đang kết nối tới NocoDB API: {url}")
    
    try:
        # Thiết lập session với retry
        session = requests.Session()
        
        # Gọi API
        response = session.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        
        # Lấy dữ liệu từ response
        data = response.json().get("list", [])
        print(f"Đã lấy {len(data)} bản ghi từ NocoDB")
        
        # Debug: In ra tên các trường trong bản ghi đầu tiên
        if data:
            print(f"Các trường có trong bản ghi: {', '.join(data[0].keys())}")
        
        # Cấu trúc dữ liệu để lưu trữ slides theo category và thứ tự
        storymaps = defaultdict(list)

        for item in data:
            # Xử lý trường phân loại (sử dụng tên trường mới)
            category_field = "story_map_collect"
            order_field = "story_map_collect_num"
            
            # Lấy giá trị trường phân loại
            category_value = str(item.get(category_field, '')).strip()
            if not category_value:
                continue
            
            # Phân tách các giá trị nếu có nhiều file đích
            categories = [cat.strip() for cat in category_value.split(',') if cat.strip()]
            if not categories:
                continue
                
            print(f"Đang xử lý bản ghi cho các file: {', '.join(categories)}")

            # Lấy thứ tự từ cột story_map_collect_num, mặc định là 999 nếu không có
            try:
                order_num = int(item.get(order_field, 999))
            except (ValueError, TypeError):
                order_num = 999

            # Sử dụng tên trường chính xác từ log
            headline = item.get("text_headline", "")
            description = item.get("text_description", "")
            
            # Xử lý tọa độ với kiểm tra None
            try:
                lat = float(item.get("latitude", 0) or 0)
                lon = float(item.get("longitude", 0) or 0)
            except (ValueError, TypeError):
                print(f"Cảnh báo: Tọa độ không hợp lệ cho bản ghi {headline}")
                lat = 0
                lon = 0
            
            # Tạo slide từ dữ liệu
            slide = {
                "text": {
                    "headline": headline,
                    "text": description
                },
                "location": {
                    "name": headline,  # Sử dụng headline làm tên địa điểm nếu không có trường riêng
                    "lat": lat,
                    "lon": lon
                },
                "_order": order_num  # Lưu thứ tự để sắp xếp sau này
            }

            # Thêm media nếu có
            media_url = item.get("media_url")
            if media_url:
                slide["media"] = {
                    "url": media_url,
                    "caption": item.get("media_caption", ""),
                    "credit": item.get("media_credit", "")
                }

            # Thêm slide vào mỗi category tương ứng
            for category in categories:
                # Chuẩn hóa tên file: loại bỏ .json nếu có trong tên category
                if category.endswith('.json'):
                    category_key = category[:-5]  # Loại bỏ .json
                elif category.endswith('.csv'):
                    category_key = category  # Giữ nguyên .csv
                else:
                    category_key = category
                    
                # Lấy tên file không có đường dẫn
                base_category = os.path.basename(category_key)
                storymaps[base_category].append(slide)

        # Tạo thư mục đầu ra
        os.makedirs(output_dir, exist_ok=True)
        
        # Lấy danh sách file hiện có trong thư mục đầu ra
        existing_files = []
        for file in os.listdir(output_dir):
            if file.endswith('.json') or file.endswith('.csv'):
                existing_files.append(file)
        
        # Danh sách file mới sẽ được tạo
        new_files = []
        
        # Tạo và lưu các file
        print(f"Số lượng categories: {len(storymaps)}")
        for category, slides in storymaps.items():
            print(f"Đang tạo file cho category: {category} với {len(slides)} slides")
            
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
                new_files.append(category)
            else:
                # Xử lý file JSON
                file_name = f"{category}.json"
                file_path = os.path.join(output_dir, file_name)
                
                # Tạo overview slide
                overview_slide = {
                    "type": "overview",
                    "text": {
                        "headline": f"Bản đồ {category.replace('-', ' ').title()}",
                        "text": f"Bản đồ tổng quan về {category.replace('-', ' ')}"
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
                new_files.append(file_name)

        # Ghi log
        log_path = os.path.join(output_dir, 'sync_log.txt')
        with open(log_path, 'a') as log:
            log.write(f"{datetime.now()}: Đồng bộ {len(data)} bản ghi thành {len(storymaps)} files\n")
        
        # Xác định file cần xóa (có trong existing_files nhưng không có trong new_files)
        files_to_delete = set(existing_files) - set(new_files)
        for file_to_delete in files_to_delete:
            if file_to_delete != 'sync_log.txt':  # Không xóa file log
                try:
                    os.remove(os.path.join(output_dir, file_to_delete))
                    print(f"Đã xóa file không còn trong dữ liệu: {file_to_delete}")
                except Exception as e:
                    print(f"Lỗi khi xóa file {file_to_delete}: {e}")
        
        return 0
        
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi gọi API: {str(e)}")
        return 1
    except Exception as e:
        print(f"Lỗi không xác định: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
