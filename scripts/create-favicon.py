"""
使用 PIL 生成 favicon
需要先安裝: pip install pillow
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_favicon(emoji, bg_color, size=512):
    """創建 favicon"""
    # 建立圖片
    img = Image.new('RGBA', (size, size), bg_color)
    draw = ImageDraw.Draw(img)

    # 畫圓角矩形背景
    # PIL 預設不支援圓角，我們用簡單的漸層和陰影效果

    # 嘗試使用系統字體顯示 emoji
    font_size = int(size * 0.7)

    # Windows 字體路徑
    font_paths = [
        "C:\\Windows\\Fonts\\seguiemj.ttf",  # Segoe UI Emoji
        "C:\\Windows\\Fonts\\Arial.ttf",
    ]

    font = None
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                font = ImageFont.truetype(font_path, font_size)
                break
            except:
                pass

    if font is None:
        font = ImageFont.load_default()

    # 計算文字位置（置中）
    bbox = draw.textbbox((0, 0), emoji, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (size - text_width) // 2 - bbox[0]
    y = (size - text_height) // 2 - bbox[1]

    # 畫 emoji
    draw.text((x, y), emoji, fill='white', font=font)

    return img

def save_all_sizes(base_img, output_dir):
    """儲存所有需要的尺寸"""
    sizes = {
        'favicon-16x16.png': 16,
        'favicon-32x32.png': 32,
        'favicon-48x48.png': 48,
        'favicon.ico': 32,  # ICO 格式
        'apple-touch-icon.png': 180,  # iOS
        'android-chrome-192x192.png': 192,  # Android
        'android-chrome-512x512.png': 512,  # Android
    }

    os.makedirs(output_dir, exist_ok=True)

    for filename, size in sizes.items():
        resized = base_img.resize((size, size), Image.Resampling.LANCZOS)
        filepath = os.path.join(output_dir, filename)

        if filename.endswith('.ico'):
            resized.save(filepath, format='ICO')
        else:
            resized.save(filepath, format='PNG')

        print(f"已生成: {filepath}")

def main():
    print("=" * 60)
    print("Work Progress Favicon Generator")
    print("=" * 60)

    # 配置
    EMOJI = "📊"  # 圖表 emoji
    BG_COLOR = (102, 126, 234, 255)  # #667eea
    OUTPUT_DIR = "../public"

    print(f"\n圖示: {EMOJI}")
    print(f"背景色: RGB{BG_COLOR[:3]}")
    print(f"輸出目錄: {OUTPUT_DIR}\n")

    # 生成 512x512 的基礎圖片
    print("正在生成 favicon...")
    base_img = create_favicon(EMOJI, BG_COLOR)

    # 儲存所有尺寸
    save_all_sizes(base_img, OUTPUT_DIR)

    print(f"\n✓ 完成！所有 favicon 已儲存到 {OUTPUT_DIR}")
    print("\n建議在 index.html 中加入以下程式碼：")
    print("""
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
    """)

if __name__ == "__main__":
    try:
        main()
    except ImportError:
        print("\n❌ 缺少 Pillow 套件")
        print("請執行: pip install pillow")
    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
