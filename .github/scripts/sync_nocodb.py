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
        
        # Tìm tên trường phân loại (có thể là story_map_collect hoặc storyMapCollect)
        category_field = None
        order_field = None
        
        if data:
            possible_category_fields = ['story_map_collect', 'storyMapCollect', 'story-map-collect', 'category']
            possible_order_fields = ['order_num', 'orderNum', 'order', 'sequence']
            
            for field in possible_category_fields:
                if field in data[0]:
                    category_field = field
                    print(f"Đã tìm thấy trường phân loại: {field}")
                    break
            
            for field in possible_order_fields:
                if field in data[0]:
                    order_field = field
                    print(f"Đã tìm thấy trường thứ tự: {field}")
                    break
        
        if not category_field:
            print("Không tìm thấy trường phân loại trong dữ liệu. Vui lòng kiểm tra tên trường.")
            # Debug: In ra một bản ghi mẫu
            if data:
                print(f"Bản ghi mẫu: {json.dumps(data[0], indent=2, ensure_ascii=False)}")
            return 1
        
        # Cấu trúc dữ liệu để lưu trữ slides theo category và thứ tự
        storymaps = defaultdict(list)

        for item in data:
            # Xử lý trường phân loại
            category = str(item.get(category_field, '')).strip()
            if not category:
                continue
            
            print(f"Đang xử lý bản ghi với {category_field}={category}")

            # Lấy thứ tự từ cột order_num, mặc định là 999 nếu không có
            try:
                order_num = int(item.get(order_field, 999)) if order_field else 999
            except (ValueError, TypeError):
                order_num = 999

            # Map các trường dữ liệu linh hoạt
            title_field = find_field(item, ['title', 'headline', 'name'])
            desc_field = find_field(item, ['description', 'text', 'content'])
            loc_field = find_field(item, ['location', 'place', 'locationName'])
            lat_field = find_field(item, ['latitude', 'lat', 'y'])
            lon_field = find_field(item, ['longitude', 'lng', 'lon', 'x'])
            media_field = find_field(item, ['media_url', 'mediaUrl', 'media', 'image'])
            
            # Tạo slide từ dữ liệu
            slide = {
                "text": {
                    "headline": item.get(title_field, ""),
                    "text": item.get(desc_field, "")
                },
                "location": {
                    "name": item.get(loc_field, ""),
                    "lat": float(item.get(lat_field, 0)),
                    "lon": float(item.get(lon_field, 0))
                },
                "_order": order_num  # Lưu thứ tự để sắp xếp sau này
            }

            media_url = item.get(media_field)
            if media_url:
                slide["media"] = {
                    "url": media_url,
                    "caption": item.get(find_field(item, ['media_caption', 'mediaCaption']), ""),
                    "credit": item.get(find_field(item, ['media_credit', 'mediaCredit']), "")
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
        
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi gọi API: {str(e)}")
        return 1
    except Exception as e:
        print(f"Lỗi không xác định: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

def find_field(item, possible_names):
    """Tìm trường dữ liệu từ danh sách các tên có thể"""
    for name in possible_names:
        if name in item:
            return name
    return possible_names[0]  # Trả về tên đầu tiên nếu không tìm thấy

if __name__ == "__main__":
    exit(main())
