import pyautogui
import time
import os
import importlib
import sys

# 确保Config.py存在
if not os.path.exists("Config.py"):
    print("Config.py不存在，请先确保该文件存在")
    sys.exit(1)

# 导入配置
import Config

def get_position(prompt):
    """让用户通过鼠标点击获取位置"""
    print(f"{prompt}，请将鼠标移动到该位置并按下回车键...")
    input()  # 等待用户按回车
    x, y = pyautogui.position()
    print(f"位置已记录: ({x}, {y})")
    return (x, y)

def main():
    """主定位函数"""
    print("=== 大众点评搜索界面定位工具 ===")
    print("请按照提示依次定位各个元素")
    print("定位过程中请勿移动或调整模拟器窗口")
    
    # 定位模拟器边界
    Config.positions["simulator_top_left"] = get_position("请定位模拟器左上角")
    Config.positions["simulator_bottom_right"] = get_position("请定位模拟器右下角")
    
    # 定位基本元素
    Config.positions["city_dropdown_button"] = get_position("请定位城市下拉按钮")
    Config.positions["city_search_box"] = get_position("请定位城市搜索框")
    Config.positions["city_result"] = get_position("请定位城市搜索结果（选中后的位置）")
    Config.positions["food_button"] = get_position("请定位美食按钮")
    Config.positions["food_ranking_button"] = get_position("请定位美食排行按钮")
    Config.positions["category_dropdown"] = get_position("请定位细分品类下拉按钮")
    
    # 定位19个细分品类
    print("\n=== 定位19个细分品类 ===")
    print("请先点击细分品类下拉按钮展开列表")
    input("准备好后按回车继续...")
    
    categories = []
    for i in range(19):
        categories.append(get_position(f"请定位第{i+1}个细分品类"))
    
    Config.positions["categories"] = categories
    
    # 保存配置
    print("\n所有位置已定位完成，正在保存配置...")
    Config.save_config()
    print("配置已保存到Config.py文件")

if __name__ == "__main__":
    main() 