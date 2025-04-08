import os
import json
import sys
import re
from supabase import create_client, Client
from dotenv import load_dotenv
import traceback
from collections import defaultdict

# Load environment variables from .env file
load_dotenv()

# Get Supabase credentials from environment variables
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

# 检查API密钥是否存在
if not supabase_url or not supabase_key:
    print("错误: 未找到Supabase凭据。请在.env文件中添加SUPABASE_URL和SUPABASE_KEY")
    sys.exit(1)

# Initialize Supabase client
supabase: Client = create_client(supabase_url, supabase_key)

# Required fields that must be present in each record
REQUIRED_FIELDS = ["榜单", "品牌"]

def extract_city_from_path(file_path):
    """从文件路径中提取城市名称"""
    # 解析文件路径获取目录名
    dir_path = os.path.dirname(file_path)
    
    # 提取目录名中的城市名称（格式如："分析结果文件/上海_20250408_032249"）
    dir_name = os.path.basename(dir_path)
    
    # 使用正则表达式提取城市名称（匹配下划线前的内容）
    city_match = re.match(r'([^_]+)_', dir_name)
    if city_match:
        return city_match.group(1)
    
    # 如果无法解析，返回"未知"
    return "未知"

def validate_data(data):
    """Validate if data meets requirements for upload"""
    if not data or not isinstance(data, list):
        raise ValueError("Data must be a non-empty list")
    
    # Check each record for required fields
    for record in data:
        for field in REQUIRED_FIELDS:
            if field not in record or not record[field]:
                raise ValueError(f"Missing required field: {field}")
    
    return True

def handle_duplicate_keys(data):
    """Handle duplicate primary key combinations"""
    # Keep track of seen (榜单, 品牌) combinations
    seen_keys = defaultdict(int)
    modified_data = []
    
    for record in data:
        key = (record["榜单"], record["品牌"])
        seen_keys[key] += 1
        
        # If this is a duplicate, append a counter to make it unique
        if seen_keys[key] > 1:
            new_record = record.copy()
            new_record["品牌"] = f"{record['品牌']}_{seen_keys[key]}"
            modified_data.append(new_record)
            print(f"  Renamed duplicate key: {record['品牌']} → {new_record['品牌']}")
        else:
            modified_data.append(record)
    
    return modified_data

def handle_missing_required_fields(data):
    """处理缺失必要字段的记录"""
    valid_records = []
    skipped_count = 0
    
    for record in data:
        is_valid = True
        for field in REQUIRED_FIELDS:
            if field not in record or not record[field]:
                is_valid = False
                skipped_count += 1
                break
                
        if is_valid:
            valid_records.append(record)
    
    if skipped_count > 0:
        print(f"  警告: 跳过了 {skipped_count} 条缺少必要字段的记录")
        
    return valid_records

def process_json_file(file_path):
    # Get filename without extension to replace "榜单" field
    filename = os.path.basename(file_path)
    filename_without_ext = os.path.splitext(filename)[0]
    
    # 从文件路径提取城市
    city = extract_city_from_path(file_path)
    print(f"  城市: {city}")
    
    # Read JSON file
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Validate data format
    if not data or not isinstance(data, list):
        raise ValueError(f"Invalid JSON format in {filename}: Must be a non-empty list")
    
    # 处理缺失必要字段的记录
    data = handle_missing_required_fields(data)
    
    # Process each record in the JSON file
    for record in data:
        if not isinstance(record, dict):
            raise ValueError(f"Invalid record format in {filename}: Each item must be an object")
        
        # Replace "榜单" field with filename
        record["榜单"] = filename_without_ext
        
        # 添加城市字段
        record["城市"] = city
    
    # Handle potential duplicate keys
    data = handle_duplicate_keys(data)
    
    return data

def upload_to_supabase(data):
    try:
        # Validate data before uploading
        validate_data(data)
        
        # Print first record for debugging
        if data:
            print(f"Sample record: {json.dumps(data[0], ensure_ascii=False)}")
        
        # Upload data to Supabase - use lowercase table name
        result = supabase.table("dzdpdata").upsert(data).execute()
        return result
    except Exception as e:
        # Capture and re-raise with more details
        error_details = f"Error type: {type(e).__name__}, Message: {repr(e)}"
        print(f"Supabase upload error: {error_details}")
        traceback.print_exc()  # Print the full stack trace
        raise Exception(error_details)

def process_directory(directory_path):
    if not os.path.exists(directory_path):
        print(f"Directory not found: {directory_path}")
        return
    
    # Keep track of total records processed
    total_records = 0
    total_files = 0
    successful_files = 0
    failed_files = 0
    
    # Process all JSON files in the directory
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.json') and not file.startswith('.'):  # Skip hidden files
                file_path = os.path.join(root, file)
                print(f"Processing {file_path}...")
                
                try:
                    # Process JSON file and get modified data
                    data = process_json_file(file_path)
                    
                    # Upload to Supabase
                    result = upload_to_supabase(data)
                    
                    total_records += len(data)
                    total_files += 1
                    successful_files += 1
                    
                    print(f"Successfully uploaded {len(data)} records from {file}")
                except Exception as e:
                    failed_files += 1
                    total_files += 1
                    print(f"Error processing {file}: {repr(e)}")
    
    print(f"\nSummary: Processed {total_files} files, {successful_files} successful, {failed_files} failed, {total_records} records uploaded")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python Upload.py <directory_path>")
        sys.exit(1)
    
    directory_path = sys.argv[1]
    process_directory(directory_path) 