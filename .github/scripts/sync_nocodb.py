import requests
import json
import os
import csv
import ast
from datetime import datetime
from collections import defaultdict
from urllib.parse import urlparse

def extract_float_from_string_list(s):
    try:
        # Nếu s là None hoặc rỗng
        if not s:
            return 0.0
            
        # Nếu s đã là số
        if isinstance(s, (int, float)):
            return float(s)
            
        # Xử lý chuỗi dạng ["15.3896874"]
        s = str(s).strip()
        if s.startswith('[') and s.endswith(']'):
            # Sử dụng ast.literal_eval để chuyển đổi an toàn
            lst = ast.literal_eval(s)
            if isinstance(lst, list) and len(lst) > 0:
                return float(lst[0])
        
        # Trường hợp khác, thử chuyển đổi trực tiếp
        return float(s)
    except Exception as e:
        print(f"Lỗi khi xử lý tọa độ: {e}, giá trị: {s}")
        return 0.0

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
            # Xử lý trường phân loại
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

            # Xử lý tọa độ với kiểm tra None và định dạng chuỗi danh sách
            try:
                lat = extract_float_from_string_list(item.get("latitude"))
                lon = extract_float_from_string_list(item.get("longitude"))
            except (ValueError, TypeError) as e:
                print(f"Cảnh báo: Tọa độ không hợp lệ cho bản ghi {item.get('text_headline', '')}: {e}")
                lat = 0
                lon = 0
            
            # Tạo slide từ dữ liệu với cấu trúc mới
            slide = {
                "text": {
                    "headline": item.get("text_headline", ""),
                    "text": item.get("text_description", "")
                },
                "location": {
                    "name": item.get("text_headline", ""),  # Sử dụng headline làm tên địa điểm
                    "lat": lat,
                    "lon": lon,
                    "zoom": 12,  # Mức zoom mặc định
                    "line": True  # Hiển thị đường kết nối mặc định
                },
                "_order": order_num  # Trường nội bộ để sắp xếp, sẽ bị xóa sau
            }
            
            # Thêm media nếu có
            media_url = item.get("media_url")
            if media_url:
                slide["media"] = {
                    "url": media_url,
                    "caption": item.get("media_caption", ""),
                    "credit": item.get("media_credit", "")
                }
            
            # Thêm date nếu có
            if item.get("date"):
                slide["date"] = item.get("date")
            
            # Thêm background nếu có
            background_color = item.get("background_color")
            background_opacity = item.get("background_opacity")
            if background_color or background_opacity:
                slide["background"] = {}
                if background_color:
                    slide["background"]["color"] = background_color
                if background_opacity:
                    try:
                        slide["background"]["opacity"] = int(background_opacity)
                    except (ValueError, TypeError):
                        slide["background"]["opacity"] = 100
            
            # Thêm type nếu có
            if item.get("type"):
                slide["type"] = item.get("type")

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
                    # Định nghĩa các cột CSV theo cấu trúc mới
                    fieldnames = [
                        'text_headline', 'text_description', 'latitude', 'longitude',
                        'media_url', 'media_caption', 'media_credit', 'date',
                        'background_color', 'background_opacity', 'type'
                    ]
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    # Viết dữ liệu cho mỗi slide
                    for slide in sorted_slides:
                        row = {
                            'text_headline': slide['text']['headline'],
                            'text_description': slide['text']['text'],
                            'latitude': slide['location']['lat'],
                            'longitude': slide['location']['lon'],
                            'media_url': slide.get('media', {}).get('url', ''),
                            'media_caption': slide.get('media', {}).get('caption', ''),
                            'media_credit': slide.get('media', {}).get('credit', ''),
                            'date': slide.get('date', ''),
                            'background_color': slide.get('background', {}).get('color', ''),
                            'background_opacity': slide.get('background', {}).get('opacity', ''),
                            'type': slide.get('type', '')
                        }
                        writer.writerow(row)
                
                print(f"Đã tạo file CSV: {file_path}")
                new_files.append(category)
            else:
                # Xử lý file JSON
                file_name = f"{category}.json"
                file_path = os.path.join(output_dir, file_name)
                
                # Đảm bảo slide đầu tiên có type="overview"
                if sorted_slides and not sorted_slides[0].get('type'):
                    sorted_slides[0]['type'] = 'overview'
                
                # Tạo cấu trúc StoryMap hoàn chỉnh theo định dạng mới
                storymap_data = {
                    "storymap": {
                        "call_to_action": True,
                        "call_to_action_text": "Xem thêm",
                        "map_as_image": False,
                        "slides": sorted_slides,
                        "zoomify": False,
                        "map_type": "osm:standard",
                        "map_subdomains": "",
                        "attribution": "",
                        "language": "vi"
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
