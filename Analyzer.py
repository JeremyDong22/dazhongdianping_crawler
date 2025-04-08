import os
import json
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv, find_dotenv
import sys
import time
import re

# 检查.env文件是否存在
env_path = find_dotenv()
if not env_path:
    print("错误: 未找到.env文件。请创建.env文件并添加GEMINI_API_KEY")
    print("\n创建.env文件步骤：")
    print("1. 在当前目录创建名为'.env'的文本文件")
    print("2. 文件内容添加: GEMINI_API_KEY=你的API密钥")
    print("3. 保存文件并重新运行程序\n")
    
    print("获取Gemini API密钥的步骤：")
    print("1. 访问 https://makersuite.google.com/app/apikey")
    print("2. 登录Google账号")
    print("3. 点击'Create API Key'创建新密钥")
    print("4. 将生成的密钥复制到.env文件中")
    sys.exit(1)

# 加载环境变量
load_dotenv()

# 获取API密钥
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("错误: 未找到GEMINI_API_KEY环境变量。请在.env文件中添加GEMINI_API_KEY=你的API密钥")
    sys.exit(1)

# 清理API密钥（移除可能的空格或换行符）
api_key = api_key.strip()

# 配置Gemini API
try:
    # 使用正确的SDK接口
    genai.configure(api_key=api_key)
    
    # 尝试简单调用测试连接
    models = genai.list_models()
    print("成功连接到Gemini API")
except Exception as e:
    print(f"连接Gemini API失败: {e}")
    print("请检查API密钥是否正确，或尝试重新生成API密钥")
    sys.exit(1)

# 使用Gemini 2.0 Flash-Lite模型
try:
    model = genai.GenerativeModel('gemini-2.0-flash-lite')
    print(f"成功加载模型 gemini-2.0-flash-lite")
except Exception as e:
    print(f"加载模型失败: {e}")
    print("尝试使用备用模型...")
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("成功加载备用模型 gemini-1.5-flash")
    except Exception as e2:
        print(f"加载备用模型也失败: {e2}")
        sys.exit(1)

# 分析提示词
PROMPT = """帮我识别这些店铺所在的榜单（一个橙色高亮的文字。一般在"大众点评榜单"的正下方的栏目里面，以菜系或者食物种类命名），排名（店铺卡片左上角的灰色部分，储存为int，如1，2，3，4，5，6，7，8，9，10），
店铺名称，品牌（被包含在店铺名称里面，是"·"之前的，如果没有点就是"（"之前的），评分（含一位小数点的数字），
位置，细分榜单（在位置的右边一个空格的地方），价格（在"¥"后面，"人"之前，储存为int）。
以json数组的形式返回给我。"""

# 自然排序函数
def natural_sort_key(s):
    """提取数字用于自然排序"""
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

def process_folder(folder_path):
    """处理文件夹中的所有图片并一次性发送到Gemini API"""
    # 检查文件夹是否存在
    if not os.path.exists(folder_path):
        print(f"文件夹不存在: {folder_path}")
        return []
    
    # 获取文件夹中的所有图片文件
    image_files = [f for f in os.listdir(folder_path) if f.endswith('.png') or f.endswith('.jpg')]
    image_files.sort(key=lambda x: int(x.split('.')[0]) if x.split('.')[0].isdigit() else -1)
    
    if not image_files:
        print(f"文件夹中没有图片: {folder_path}")
        return []
    
    # 加载所有图片
    images = []
    for image_file in image_files:
        image_path = os.path.join(folder_path, image_file)
        try:
            img = Image.open(image_path)
            # 检查图片是否有效
            img.verify()  # 验证图片完整性
            # 重新打开，因为verify会消耗图片对象
            img = Image.open(image_path)
            images.append(img)
            print(f"已加载图片: {image_path}")
        except Exception as e:
            print(f"加载图片 {image_path} 时出错: {e}")
    
    if not images:
        print("没有成功加载任何图片")
        return []
    
    # 构建请求内容
    content_parts = [PROMPT]
    content_parts.extend(images)
    
    # 重试机制
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # 一次性发送所有图片进行分析
            print(f"正在发送 {len(images)} 张图片到Gemini API进行分析... (尝试 {attempt+1}/{max_retries})")
            
            # 使用正确的API调用方式
            response = model.generate_content(content_parts)
            
            # 检查响应是否有效
            if response.text and len(response.text) > 0:
                print("分析完成，正在处理结果...")
                return extract_json_from_response(response.text)
            else:
                print(f"API返回空响应 (尝试 {attempt+1}/{max_retries})")
                if attempt < max_retries - 1:
                    print("等待2秒后重试...")
                    time.sleep(2)
                    continue
        except Exception as e:
            print(f"API调用出错 (尝试 {attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                print("等待3秒后重试...")
                time.sleep(3)
                continue
    
    print(f"在 {max_retries} 次尝试后仍无法成功调用API，跳过当前文件夹")
    return []

def extract_json_from_response(response_text):
    """从Gemini的响应中提取JSON数据"""
    try:
        # 尝试找到JSON数组的开始和结束
        start_idx = response_text.find('[')
        end_idx = response_text.rfind(']') + 1
        
        if start_idx != -1 and end_idx != 0:
            json_text = response_text[start_idx:end_idx]
            # 解析JSON
            data = json.loads(json_text)
            return data
        else:
            print(f"无法在响应中找到JSON数组: {response_text}")
            return []
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        print(f"响应文本: {response_text}")
        return []

def determine_json_filename(data):
    """根据JSON数据确定输出文件名"""
    if not data:
        return "未知榜单.json"
    
    # 获取第一条数据的榜单名称
    first_item = data[0]
    banner_name = first_item.get("榜单", "未知榜单")
    
    return f"{banner_name}.json"

def save_results(data, output_folder, ranking_type):
    """保存JSON结果到文件"""
    if not data:
        print(f"没有数据需要保存: {ranking_type}")
        return
    
    # 创建输出文件夹（如果不存在）
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # 确定输出文件名
    if ranking_type == "主榜单":
        output_filename = "主榜单.json"
    else:
        output_filename = determine_json_filename(data)
    
    # 保存JSON文件
    output_path = os.path.join(output_folder, output_filename)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    print(f"结果已保存到: {output_path}")

def main():
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("使用方法: python Analyzer.py <武汉_时间戳文件夹路径>")
        print("例如: python Analyzer.py 搜索结果截图/武汉_20240801_120000")
        sys.exit(1)
    
    input_folder = sys.argv[1]
    if not os.path.exists(input_folder):
        print(f"输入文件夹不存在: {input_folder}")
        sys.exit(1)
    
    # 获取城市名称
    city_name = os.path.basename(input_folder).split('_')[0]
    
    # 创建输出根文件夹
    output_root = "分析结果文件"
    if not os.path.exists(output_root):
        os.makedirs(output_root)
    
    # 创建城市输出文件夹
    city_output_folder = os.path.join(output_root, os.path.basename(input_folder))
    if not os.path.exists(city_output_folder):
        os.makedirs(city_output_folder)
    
    # 初始化文件夹计数器
    folder_count = 0
    
    # 处理主榜单
    main_ranking_folder = os.path.join(input_folder, "主榜单")
    if os.path.exists(main_ranking_folder):
        print(f"\n开始处理主榜单: {main_ranking_folder}")
        main_ranking_results = process_folder(main_ranking_folder)
        save_results(main_ranking_results, city_output_folder, "主榜单")
        folder_count += 1
    
    # 处理细分榜单 - 使用自然排序
    subdirectories = []
    for item in os.listdir(input_folder):
        item_path = os.path.join(input_folder, item)
        if os.path.isdir(item_path) and item.startswith("细分榜单"):
            subdirectories.append(item)
    
    # 使用自然数排序
    subdirectories.sort(key=natural_sort_key)
    
    # 按排序后的顺序处理文件夹
    for item in subdirectories:
        item_path = os.path.join(input_folder, item)
        print(f"\n开始处理细分榜单: {item_path}")
        category_results = process_folder(item_path)
        save_results(category_results, city_output_folder, item)
        folder_count += 1
    
    # 打印分析结果统计
    print("\n=== 分析结果统计 ===")
    print(f"总共分析了 {folder_count} 个文件夹")
    
    # 判断是否达到标准数量
    if folder_count < 20:
        print(f"警告: 分析的文件夹数量少于标准数量 (20)，可能丢失了一些数据！")
    elif folder_count == 20:
        print("恭喜！分析的文件夹数量符合标准数量 (20)。")
    else:
        print(f"分析的文件夹数量 ({folder_count}) 超过了标准数量 (20)。")
    
    print("\n所有分析完成!")

if __name__ == "__main__":
    main() 