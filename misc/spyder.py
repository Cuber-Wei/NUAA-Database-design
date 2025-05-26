import requests
from bs4 import BeautifulSoup
import os
import json
import urllib.parse
from urllib.parse import urljoin
import time


def get_html(url):
    """获取网页HTML内容"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    response.encoding = "utf-8"
    return response.text


def download_image(img_url, save_path, img_name):
    """下载图片到指定路径"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(img_url, headers=headers, timeout=30)
        if response.status_code == 200:
            with open(save_path, "wb") as f:
                f.write(response.content)
            print(f"成功下载图片: {img_name}")
            return True
        else:
            print(f"下载失败 {img_name}: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"下载图片时出错 {img_name}: {str(e)}")
        return False


def parse_images(html, base_url):
    """解析HTML中的图片信息"""
    soup = BeautifulSoup(html, "html.parser")
    images = []

    # 查找所有img标签
    img_tags = soup.find_all("img")

    for i, img in enumerate(img_tags):
        src = img.get("src")
        alt = img.get("alt", f"image_{i}")

        if src:
            # 处理相对URL
            if src.startswith("//"):
                img_url = "https:" + src
            elif src.startswith("/"):
                img_url = urljoin(base_url, src)
            elif not src.startswith("http"):
                img_url = urljoin(base_url, src)
            else:
                img_url = src

            # 获取文件扩展名
            parsed_url = urllib.parse.urlparse(img_url)
            path = parsed_url.path
            if "." in path:
                ext = os.path.splitext(path)[1]
                if not ext:
                    ext = ".jpg"  # 默认扩展名
            else:
                ext = ".jpg"

            # 生成安全的文件名
            safe_name = "".join(
                c for c in alt if c.isalnum() or c in (" ", "-", "_")
            ).rstrip()
            if not safe_name:
                safe_name = f"image_{i}"

            img_name = f"{safe_name}_{i}{ext}"

            images.append(
                {"name": alt, "url": img_url, "filename": img_name, "alt": alt}
            )

    return images


def main():
    url = "https://wiki.biligame.com/ys/%E8%A7%92%E8%89%B2"
    pic_dir = "pic"

    # 确保图片目录存在
    os.makedirs(pic_dir, exist_ok=True)

    print("正在获取网页内容...")
    html = get_html(url)

    print("正在解析图片信息...")
    images = parse_images(html, url)

    print(f"发现 {len(images)} 张图片")

    downloaded_images = []

    for i, img_info in enumerate(images):
        img_url = img_info["url"]
        img_name = img_info["filename"]
        save_path = os.path.join(pic_dir, img_name)

        print(f"正在下载 ({i + 1}/{len(images)}): {img_info['name']}")

        if download_image(img_url, save_path, img_name):
            downloaded_images.append(
                {
                    "name": img_info["name"],
                    "filename": img_name,
                    "storage_path": save_path,
                    "original_url": img_url,
                    "alt_text": img_info["alt"],
                }
            )

        # 添加延迟避免请求过快
        time.sleep(0.5)

    # 生成JSON描述文件
    json_file = "downloaded_images.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "total_downloaded": len(downloaded_images),
                "source_url": url,
                "download_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "images": downloaded_images,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    print(f"\n下载完成！")
    print(f"成功下载 {len(downloaded_images)} 张图片")
    print(f"图片保存在: {pic_dir} 文件夹")
    print(f"图片信息保存在: {json_file}")


if __name__ == "__main__":
    main()
