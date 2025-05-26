import os
import shutil
from collections import defaultdict
import hashlib


def get_file_hash(filepath):
    """计算文件的MD5哈希值，用于判断文件是否相同"""
    hash_md5 = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        print(f"计算文件哈希时出错 {filepath}: {e}")
        return None


def extract_name_before_png(filename):
    """提取文件名中第一个'png'之前的内容"""
    # 找到第一个'png'的位置
    png_index = filename.lower().find('png')
    if png_index != -1:
        # 提取png之前的内容，去掉末尾可能的下划线
        name_part = filename[:png_index].rstrip('_')
        return name_part
    else:
        # 如果没有找到png，返回不带扩展名的文件名
        return os.path.splitext(filename)[0]


def process_images(pic_dir):
    """处理图片文件：去重和重命名"""
    if not os.path.exists(pic_dir):
        print(f"目录不存在: {pic_dir}")
        return
    
    print("开始处理图片文件...")
    
    # 获取所有图片文件
    image_files = []
    for filename in os.listdir(pic_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            filepath = os.path.join(pic_dir, filename)
            image_files.append((filename, filepath))
    
    print(f"找到 {len(image_files)} 个图片文件")
    
    # 按新文件名分组
    name_groups = defaultdict(list)
    
    for filename, filepath in image_files:
        new_name = extract_name_before_png(filename)
        if new_name:
            # 获取文件信息
            file_size = os.path.getsize(filepath)
            file_hash = get_file_hash(filepath)
            
            name_groups[new_name].append({
                'original_filename': filename,
                'filepath': filepath,
                'size': file_size,
                'hash': file_hash
            })
    
    print(f"分组后得到 {len(name_groups)} 个不同的名称")
    
    # 创建处理后的目录
    processed_dir = os.path.join(os.path.dirname(pic_dir), 'pic_processed')
    os.makedirs(processed_dir, exist_ok=True)
    
    # 统计信息
    total_files = 0
    duplicates_removed = 0
    processed_files = 0
    
    # 处理每个分组
    for new_name, files in name_groups.items():
        total_files += len(files)
        
        if len(files) == 1:
            # 只有一个文件，直接重命名
            file_info = files[0]
            original_ext = os.path.splitext(file_info['original_filename'])[1]
            new_filename = f"{new_name}{original_ext}"
            new_filepath = os.path.join(processed_dir, new_filename)
            
            try:
                shutil.copy2(file_info['filepath'], new_filepath)
                processed_files += 1
                print(f"✓ 重命名: {file_info['original_filename']} -> {new_filename}")
            except Exception as e:
                print(f"✗ 复制文件失败 {file_info['original_filename']}: {e}")
        
        else:
            # 多个文件，需要去重
            print(f"\n处理重复文件组: {new_name} ({len(files)} 个文件)")
            
            # 按哈希值分组来识别真正相同的文件
            hash_groups = defaultdict(list)
            for file_info in files:
                if file_info['hash']:
                    hash_groups[file_info['hash']].append(file_info)
            
            # 为每个不同的哈希值保留一个文件
            saved_count = 0
            for hash_value, identical_files in hash_groups.items():
                if saved_count == 0:
                    # 选择文件大小最大的作为保留文件
                    best_file = max(identical_files, key=lambda x: x['size'])
                    original_ext = os.path.splitext(best_file['original_filename'])[1]
                    new_filename = f"{new_name}{original_ext}"
                    new_filepath = os.path.join(processed_dir, new_filename)
                    
                    try:
                        shutil.copy2(best_file['filepath'], new_filepath)
                        processed_files += 1
                        saved_count += 1
                        print(f"  ✓ 保留: {best_file['original_filename']} -> {new_filename} (大小: {best_file['size']} bytes)")
                    except Exception as e:
                        print(f"  ✗ 复制文件失败 {best_file['original_filename']}: {e}")
                
                # 统计重复文件
                duplicates_removed += len(identical_files) - (1 if saved_count <= 1 else 0)
                
                # 显示被删除的重复文件
                for file_info in identical_files:
                    if saved_count <= 1 and file_info != best_file:
                        print(f"  - 删除重复: {file_info['original_filename']} (大小: {file_info['size']} bytes)")
                    elif saved_count > 1:
                        print(f"  - 删除重复: {file_info['original_filename']} (大小: {file_info['size']} bytes)")
    
    # 输出统计信息
    print(f"\n" + "="*50)
    print(f"处理完成！")
    print(f"原始文件总数: {total_files}")
    print(f"处理后文件数: {processed_files}")
    print(f"删除重复文件: {duplicates_removed}")
    print(f"节省空间: {total_files - processed_files} 个文件")
    print(f"处理后的文件保存在: {processed_dir}")
    
    return processed_dir


def main():
    pic_dir = "pic"
    
    # 检查目录是否存在
    if not os.path.exists(pic_dir):
        print(f"错误: 目录 {pic_dir} 不存在")
        return
    
    # 显示处理前的文件数量
    original_count = len([f for f in os.listdir(pic_dir) 
                         if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))])
    print(f"原始图片文件数量: {original_count}")
    
    # 处理图片
    processed_dir = process_images(pic_dir)
    
    if processed_dir:
        # 显示一些示例重命名结果
        print(f"\n示例重命名结果:")
        processed_files = os.listdir(processed_dir)[:10]  # 显示前10个
        for filename in processed_files:
            print(f"  - {filename}")
        
        if len(processed_files) > 10:
            print(f"  ... 还有 {len(processed_files) - 10} 个文件")


if __name__ == "__main__":
    main() 