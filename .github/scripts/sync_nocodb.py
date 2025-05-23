import requests
import json
import os
import csv
import ast
from datetime import datetime
from collections import defaultdict
from urllib.parse import urlparse
import markdown

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
    """Chuyển markdown sang HTML, giữ nguyên HTML có sẵn, thay \\n thành <br>."""
    if not md_text:
        return ""
    html = markdown.markdown(md_text, extensions=['extra', 'sane_lists'])
    html = html.replace('\n', '<br>')
    return html

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
            
            # Chuyển markdown sang HTML cho text_description
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

        existing_files = [f for f in os.listdir(output_dir) if f.endswith('.json') or f.endswith('.csv')]
        new_files = []

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
                
                print(f"Đã tạo file CSV: {file_path}")
                new_files.append(category)
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

                print(f"Đã tạo file JSON: {file_path} với {len(reordered_slides)} slides")
                print(f"Call to action text: {final_call_to_action_text}")
                new_files.append(file_name)

        # Ghi log
        log_path = os.path.join(output_dir, 'sync_log.txt')
        with open(log_path, 'a') as log:
            log.write(f"{datetime.now()}: Đồng bộ {len(data)} bản ghi thành {len(storymaps)} files\n")

        # Xóa file không còn trong dữ liệu
        files_to_delete = set(existing_files) - set(new_files)
        for file_to_delete in files_to_delete:
            if file_to_delete != 'sync_log.txt':
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
