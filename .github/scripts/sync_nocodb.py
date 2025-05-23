import requests
import json
import os
import csv
import ast
from datetime import datetime
from collections import defaultdict
from urllib.parse import urlparse
import markdown
import re

def extract_float_from_string_list(s):
    """Trích xuất số thực từ chuỗi hoặc danh sách chuỗi."""
    try:
        if not s:
            return None
        if isinstance(s, (int, float)):
            return float(s)
        s = str(s).strip()
        if s.startswith('[') and s.endswith(']'):
            lst = ast.literal_eval(s)
            if isinstance(lst, list) and len(lst) > 0:
                return float(lst[0])
        return float(s)
    except Exception as e:
        print(f"Lỗi khi xử lý tọa độ: {e}, giá trị: {s}")
        return None

def markdown_to_html(md_text):
    """Chuyển markdown + HTML sang HTML thuần, xử lý hỗn hợp markdown và HTML."""
    if not md_text:
        return ""
    
    # Kiểm tra xem có thẻ HTML không
    has_html = re.search(r'<[^>]+>', md_text)
    
    if has_html:
        # Nếu có HTML, xử lý từng phần riêng biệt
        # Tách các phần HTML và markdown
        parts = re.split(r'(<[^>]*>)', md_text)
        processed_parts = []
        
        for part in parts:
            if re.match(r'<[^>]*>', part):
                # Đây là thẻ HTML, giữ nguyên
                processed_parts.append(part)
            else:
                # Đây là text/markdown, xử lý markdown
                if part.strip():
                    # Chuyển markdown sang HTML
                    html_part = markdown.markdown(part, extensions=['extra', 'sane_lists'])
                    # Loại bỏ thẻ <p> bọc ngoài nếu có
                    if html_part.startswith('<p>') and html_part.endswith('</p>'):
                        html_part = html_part[3:-4]
                    processed_parts.append(html_part)
                else:
                    processed_parts.append(part)
        
        result = ''.join(processed_parts)
    else:
        # Không có HTML, chỉ xử lý markdown
        result = markdown.markdown(md_text, extensions=['extra', 'sane_lists'])
        # Loại bỏ thẻ <p> bọc ngoài nếu có
        if result.startswith('<p>') and result.endswith('</p>'):
            result = result[3:-4]
    
    # Thay thế xuống dòng thành <br>
    result = result.replace('\n', '<br>')
    
    return result

def reorder_slide(slide, is_last=False):
    """Sắp xếp lại thứ tự thuộc tính trong slide."""
    new_slide = {}
    if is_last:
        # Slide cuối: text trước media, location sau cùng
        if "date" in slide:
            new_slide["date"] = slide["date"]
        if "text" in slide:
            new_slide["text"] = slide["text"]
        if "media" in slide:
            new_slide["media"] = slide["media"]
        if "type" in slide:
            new_slide["type"] = slide["type"]
        if "background" in slide:
            new_slide["background"] = slide["background"]
        if "location" in slide:
            new_slide["location"] = slide["location"]
    else:
        # Các slide khác: date → location → media → text → type/background
        if "date" in slide:
            new_slide["date"] = slide["date"]
        if "location" in slide:
            new_slide["location"] = slide["location"]
        if "media" in slide:
            new_slide["media"] = slide["media"]
        if "text" in slide:
            new_slide["text"] = slide["text"]
        if "type" in slide:
            new_slide["type"] = slide["type"]
        if "background" in slide:
            new_slide["background"] = slide["background"]
    return new_slide

def get_file_hash(file_path):
    """Tính hash của file để kiểm tra thay đổi."""
    try:
        import hashlib
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return None

def main():
    # Lấy thông tin từ biến môi trường
    domain = os.environ.get("NOCODB_DOMAIN")
    token = os.environ.get("NOCODB_TOKEN")
    table_id = os.environ.get("NOCODB_TABLE_ID")
    output_dir = os.environ.get("OUTPUT_DIR", "storymaps")
    language = os.environ.get("STORYMAP_LANGUAGE", "en")

    if not domain or not token or not table_id:
        print("Thiếu biến môi trường cần thiết")
        return 1

    # Xử lý URL chuẩn
    parsed = urlparse(domain)
    if parsed.scheme:
        domain = parsed.netloc

    url = f"https://{domain}/api/v2/tables/{table_id}/records"
    headers = {"xc-token": token, "Accept": "application/json"}
    params = {"limit": 1000}

    print(f"Đang kết nối tới NocoDB API: {url}")

    try:
        session = requests.Session()
        response = session.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        data = response.json().get("list", [])
        print(f"Đã lấy {len(data)} bản ghi từ NocoDB")

        storymaps = defaultdict(list)
        call_to_action_texts = {}  # Lưu trữ call_to_action_text cho từng category

        for item in data:
            category_field = "story_map_collect"
            order_field = "story_map_collect_num"
            zoom_field = "zoom"
            call_to_action_text_field = "call_to_action_text"

            category_value = str(item.get(category_field, '')).strip()
            
            # Bỏ qua các bản ghi có story_map_collect là null, rỗng hoặc "None"
            if not category_value or category_value.lower() in ['null', 'none', '']:
                print(f"Bỏ qua bản ghi có story_map_collect null/rỗng: {item.get('text_headline', 'Không có tiêu đề')}")
                continue

            categories = [cat.strip() for cat in category_value.split(',') if cat.strip()]
            if not categories:
                continue

            try:
                order_num = int(item.get(order_field, 999))
            except (ValueError, TypeError):
                order_num = 999

            lat = extract_float_from_string_list(item.get("latitude"))
            lon = extract_float_from_string_list(item.get("longitude"))

            # Lấy zoom từ cột zoom hoặc mặc định
            try:
                zoom_value = int(item.get(zoom_field, 12))
            except (ValueError, TypeError):
                zoom_value = 12

            # Lấy call_to_action_text từ slide có type="overview" hoặc order_num = 1
            call_to_action_text = item.get(call_to_action_text_field, "")
            is_overview_slide = (item.get("type") == "overview" or order_num == 1)
            
            # Chuyển markdown + HTML sang HTML thuần cho text_description
            text_description_html = markdown_to_html(item.get("text_description", ""))

            # Xây dựng slide
            slide = {}

            # Thuộc tính date, thay null thành ""
            slide["date"] = item.get("date") or ""

            # Thuộc tính location - khởi tạo cơ bản
            location = {"line": True}

            # Thuộc tính media
            media_url = item.get("media_url")
            media = None
            if media_url:
                media = {
                    "caption": item.get("media_caption", ""),
                    "credit": item.get("media_credit", ""),
                    "url": media_url
                }

            # Thuộc tính text
            text = {
                "headline": item.get("text_headline", ""),
                "text": text_description_html
            }

            # Thuộc tính type và background
            type_value = item.get("type")
            background_color = item.get("background_color")
            background_opacity = item.get("background_opacity")
            background = None
            if background_color or background_opacity:
                background = {}
                if background_color:
                    background["color"] = background_color
                if background_opacity:
                    try:
                        background["opacity"] = int(background_opacity)
                    except:
                        background["opacity"] = 100

            # Lưu các trường vào slide
            slide["location"] = location
            if media:
                slide["media"] = media
            slide["text"] = text
            if type_value:
                slide["type"] = type_value
            if background:
                slide["background"] = background

            # Lưu các trường tạm thời để xử lý sau
            slide["_order"] = order_num
            slide["_zoom"] = zoom_value
            slide["_lat"] = lat
            slide["_lon"] = lon

            for category in categories:
                # Xử lý tên file - KHÔNG loại bỏ phần mở rộng
                base_category = os.path.basename(category)
                
                # Lưu call_to_action_text cho slide overview của category này
                if is_overview_slide and call_to_action_text:
                    call_to_action_texts[base_category] = call_to_action_text
                
                storymaps[base_category].append(slide)

        os.makedirs(output_dir, exist_ok=True)

        # Lấy danh sách file hiện có và hash của chúng
        existing_files = {}
        for file in os.listdir(output_dir):
            if file.endswith('.json') or file.endswith('.csv'):
                file_path = os.path.join(output_dir, file)
                file_hash = get_file_hash(file_path)
                existing_files[file] = file_hash

        new_files = {}
        created_files = []
        updated_files = []

        for category, slides in storymaps.items():
            # Sắp xếp slides theo thứ tự
            sorted_slides = sorted(slides, key=lambda x: x.get("_order", 999))

            # Xử lý từng slide
            for i, slide in enumerate(sorted_slides):
                is_overview = (i == 0)
                
                if is_overview:
                    # Slide overview: location chỉ giữ line: true, không có zoom
                    slide["location"] = {"line": True}
                    slide["type"] = "overview"
                else:
                    # Các slide khác: thêm tọa độ và zoom
                    lat = slide.get("_lat")
                    lon = slide.get("_lon")
                    
                    if lat is not None and lon is not None:
                        slide["location"]["lat"] = lat
                        slide["location"]["lon"] = lon
                        
                        # Xử lý zoom theo quy tắc
                        if "background" in slide and slide["background"]:
                            slide["location"]["zoom"] = 12
                        else:
                            slide["location"]["zoom"] = slide.get("_zoom", 12)

                # Xóa các trường tạm thời
                for temp_field in ["_order", "_zoom", "_lat", "_lon"]:
                    if temp_field in slide:
                        del slide[temp_field]

            # Kiểm tra định dạng file dựa trên tên category
            if category.endswith('.csv'):
                # Xử lý file CSV
                file_path = os.path.join(output_dir, category)
                
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    # Định nghĩa các cột CSV theo cấu trúc mới
                    fieldnames = [
                        'text_headline', 'text_description', 'latitude', 'longitude',
                        'media_url', 'media_caption', 'media_credit', 'date',
                        'background_color', 'background_opacity', 'type', 'zoom'
                    ]
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    # Viết dữ liệu cho mỗi slide
                    for slide in sorted_slides:
                        row = {
                            'text_headline': slide['text']['headline'],
                            'text_description': slide['text']['text'],
                            'latitude': slide['location'].get('lat', ''),
                            'longitude': slide['location'].get('lon', ''),
                            'media_url': slide.get('media', {}).get('url', ''),
                            'media_caption': slide.get('media', {}).get('caption', ''),
                            'media_credit': slide.get('media', {}).get('credit', ''),
                            'date': slide.get('date', ''),
                            'background_color': slide.get('background', {}).get('color', ''),
                            'background_opacity': slide.get('background', {}).get('opacity', ''),
                            'type': slide.get('type', ''),
                            'zoom': slide['location'].get('zoom', '')
                        }
                        writer.writerow(row)
                
                # Kiểm tra file mới tạo hay cập nhật
                new_hash = get_file_hash(file_path)
                new_files[category] = new_hash
                
                if category in existing_files:
                    if existing_files[category] != new_hash:
                        updated_files.append(f"{category} (CSV, {len(sorted_slides)} slides)")
                        print(f"Đã cập nhật file CSV: {file_path}")
                    else:
                        print(f"File CSV không thay đổi: {file_path}")
                else:
                    created_files.append(f"{category} (CSV, {len(sorted_slides)} slides)")
                    print(f"Đã tạo file CSV mới: {file_path}")
                    
            else:
                # Xử lý file JSON - thêm .json nếu chưa có
                if not category.endswith('.json'):
                    file_name = f"{category}.json"
                else:
                    file_name = category
                    
                file_path = os.path.join(output_dir, file_name)
                
                # Sắp xếp lại thứ tự thuộc tính trong slides
                reordered_slides = []
                for i, slide in enumerate(sorted_slides):
                    is_last = (i == len(sorted_slides) - 1)
                    reordered_slides.append(reorder_slide(slide, is_last))

                # Đảm bảo chỉ slide đầu tiên có type="overview"
                if reordered_slides:
                    # Xóa type từ tất cả các slide
                    for slide in reordered_slides:
                        if "type" in slide:
                            del slide["type"]
                    
                    # Thêm type="overview" cho slide đầu tiên
                    reordered_slides[0]["type"] = "overview"

                # Lấy call_to_action_text cho category này hoặc mặc định
                final_call_to_action_text = call_to_action_texts.get(category, "Khám phá!")

                # Tạo cấu trúc StoryMap hoàn chỉnh
                storymap_data = {
                    "storymap": {
                        "call_to_action": True,
                        "call_to_action_text": final_call_to_action_text,
                        "map_as_image": False,
                        "slides": reordered_slides,
                        "zoomify": False,
                        "map_type": "osm:standard",
                        "map_subdomains": "",
                        "attribution": "",
                        "language": language
                    }
                }

                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(storymap_data, f, ensure_ascii=False, indent=2)

                # Kiểm tra file mới tạo hay cập nhật
                new_hash = get_file_hash(file_path)
                new_files[file_name] = new_hash
                
                if file_name in existing_files:
                    if existing_files[file_name] != new_hash:
                        updated_files.append(f"{file_name} (JSON, {len(reordered_slides)} slides, CTA: '{final_call_to_action_text}')")
                        print(f"Đã cập nhật file JSON: {file_path}")
                    else:
                        print(f"File JSON không thay đổi: {file_path}")
                else:
                    created_files.append(f"{file_name} (JSON, {len(reordered_slides)} slides, CTA: '{final_call_to_action_text}')")
                    print(f"Đã tạo file JSON mới: {file_path}")

        # Xác định file cần xóa
        files_to_delete = set(existing_files.keys()) - set(new_files.keys())
        deleted_files = []
        
        for file_to_delete in files_to_delete:
            if file_to_delete != 'sync_log.txt':
                try:
                    file_path = os.path.join(output_dir, file_to_delete)
                    file_size = os.path.getsize(file_path)
                    os.remove(file_path)
                    deleted_files.append(f"{file_to_delete} ({file_size} bytes)")
                    print(f"Đã xóa file không còn trong dữ liệu: {file_to_delete}")
                except Exception as e:
                    print(f"Lỗi khi xóa file {file_to_delete}: {e}")

        # Ghi log chi tiết
        log_path = os.path.join(output_dir, 'sync_log.txt')
        with open(log_path, 'a', encoding='utf-8') as log:
            log.write(f"\n{'='*80}\n")
            log.write(f"Thời gian đồng bộ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            log.write(f"Tổng số bản ghi từ NocoDB: {len(data)}\n")
            log.write(f"Số categories được xử lý: {len(storymaps)}\n")
            log.write(f"Ngôn ngữ: {language}\n")
            
            if created_files:
                log.write(f"\nFile được TẠO MỚI ({len(created_files)}):\n")
                for file_info in created_files:
                    log.write(f"  + {file_info}\n")
            
            if updated_files:
                log.write(f"\nFile được CẬP NHẬT ({len(updated_files)}):\n")
                for file_info in updated_files:
                    log.write(f"  ~ {file_info}\n")
            
            if deleted_files:
                log.write(f"\nFile bị XÓA ({len(deleted_files)}):\n")
                for file_info in deleted_files:
                    log.write(f"  - {file_info}\n")
            
            if not created_files and not updated_files and not deleted_files:
                log.write(f"\nKhông có thay đổi nào được thực hiện.\n")
            
            log.write(f"Tổng số file hiện tại: {len(new_files)}\n")
            log.write(f"{'='*80}\n")

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
