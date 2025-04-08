import pyautogui
import pyperclip
import time
import os
import sys
from datetime import datetime
import importlib
from PIL import Image, ImageGrab
import platform

# 确保Config.py存在
if not os.path.exists("Config.py"):
    print("Config.py不存在，请先运行Locate.py进行定位")
    sys.exit(1)

# 导入配置
import Config

# 检查位置是否已经定位
if None in [Config.positions["simulator_top_left"], Config.positions["simulator_bottom_right"]]:
    print("位置尚未完全定位，请先运行Locate.py进行定位")
    sys.exit(1)

# 创建保存截图的根目录
results_dir = "搜索结果截图"
if not os.path.exists(results_dir):
    os.makedirs(results_dir)

def click_position(position, description="位置"):
    """点击指定坐标"""
    print(f"点击{description}: {position}")
    pyautogui.click(position[0], position[1])
    time.sleep(1)  # 点击后稍作等待

def copy_and_paste(text):
    """将文本复制到剪贴板并粘贴"""
    print(f"粘贴文本: {text}")
    pyperclip.copy(text)
    time.sleep(0.5)
    
    # 根据操作系统选择不同的粘贴热键
    if platform.system() == "Darwin":  # macOS
        pyautogui.hotkey('command', 'v')
    else:  # Windows/Linux
        pyautogui.hotkey('ctrl', 'v')
    
    time.sleep(1)

def take_screenshot(save_path):
    """截取模拟器窗口的截图并保存"""
    left, top = Config.positions["simulator_top_left"]
    right, bottom = Config.positions["simulator_bottom_right"]
    
    # 截取指定区域
    screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))
    screenshot.save(save_path)
    print(f"截图已保存: {save_path}")
    time.sleep(0.5)

def main():
    """主搜索逻辑"""
    print("=== 大众点评搜索自动化脚本 ===")
    print(f"搜索城市: {Config.search_city}")
    print(f"主榜单下滑次数: {Config.main_ranking_scroll_times}")
    print(f"细分品类榜单下滑次数: {Config.category_ranking_scroll_times}")
    
    # 每次运行时创建带时间戳的文件夹
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_dir = os.path.join(results_dir, f"{Config.search_city}_{timestamp}")
    os.makedirs(session_dir)
    
    # 1. 点击城市下拉按钮(点击两次确认焦点)
    click_position(Config.positions["city_dropdown_button"], "城市下拉按钮")
    click_position(Config.positions["city_dropdown_button"], "城市下拉按钮")
    time.sleep(1)
    
    # 2. 点击城市搜索框
    click_position(Config.positions["city_search_box"], "城市搜索框")
    time.sleep(1)
    
    # 3-4. 复制搜索城市到剪贴板并粘贴
    copy_and_paste(Config.search_city)
    time.sleep(1)
    
    # 5. 点击城市结果
    click_position(Config.positions["city_result"], "城市搜索结果")
    time.sleep(2)  # 等待城市切换完成
    
    # 6. 点击美食按钮
    click_position(Config.positions["food_button"], "美食按钮")
    time.sleep(2)
    
    # 7. 点击美食排行按钮
    click_position(Config.positions["food_ranking_button"], "美食排行按钮")
    click_position(Config.positions["food_ranking_button"], "美食排行按钮")
    click_position(Config.positions["food_ranking_button"], "美食排行按钮")
    time.sleep(3)  # 等待页面加载
    
    # 8. 主榜单截屏和下滑
    main_ranking_dir = os.path.join(session_dir, "主榜单")
    os.makedirs(main_ranking_dir)
    print(f"\n开始采集主榜单数据，将保存到 {main_ranking_dir}")
    
    # 第一次截图
    take_screenshot(os.path.join(main_ranking_dir, "0.png"))
    
    # 循环滚动和截图
    for i in range(Config.main_ranking_scroll_times):
        print(f"主榜单下滑 ({i+1}/{Config.main_ranking_scroll_times})")
        Config.scroll_down()  # 执行下滑
        take_screenshot(os.path.join(main_ranking_dir, f"{i+1}.png"))
    
    # 9-12. 遍历19个细分品类
    for category_index in range(19):
        # 9. 点击细分品类下拉
        click_position(Config.positions["category_dropdown"], "细分品类下拉")
        time.sleep(1)
        
        # 10. 点击具体细分品类
        category_position = Config.positions["categories"][category_index]
        click_position(category_position, f"细分品类 {category_index+1}/19")
        time.sleep(3)  # 等待页面加载
        
        # 创建该细分品类的文件夹
        category_dir = os.path.join(session_dir, f"细分榜单{category_index+1}")
        os.makedirs(category_dir)
        print(f"\n开始采集细分品类 {category_index+1}/19 数据，将保存到 {category_dir}")
        
        # 第一次截图
        take_screenshot(os.path.join(category_dir, "0.png"))
        
        # 循环滚动和截图
        for i in range(Config.category_ranking_scroll_times):
            print(f"细分品类下滑 ({i+1}/{Config.category_ranking_scroll_times})")
            Config.scroll_down()  # 执行下滑
            take_screenshot(os.path.join(category_dir, f"{i+1}.png"))
    
    print("\n所有数据采集完成!")
    print(f"数据已保存到: {session_dir}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"程序运行出错: {e}")
        import traceback
        traceback.print_exc() 