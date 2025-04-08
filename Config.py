import pyperclip
import pyautogui
import time

# 基础配置
search_city = "成都"  # 要搜索的城市
main_ranking_scroll_times = 9  # 主榜单下滑次数
category_ranking_scroll_times = 3  # 细分品类榜单下滑次数

# 坐标配置
positions = {
    "simulator_top_left": (606, 198),
    "simulator_bottom_right": (907, 844),
    "city_dropdown_button": (647, 246),
    "city_search_box": (704, 249),
    "city_result": (688, 285),
    "food_button": (641, 333),
    "food_ranking_button": (641, 295),
    "category_dropdown": (888, 284),
    "categories": [(717, 337), (783, 337), (861, 338), (651, 374), (723, 373), (791, 372), (853, 376), (648, 415), (727, 411), (785, 409), (853, 411), (650, 448), (722, 450), (790, 449), (853, 448), (649, 482), (713, 480), (788, 483), (864, 484)],
}

# 获取模拟器中心点坐标
def get_simulator_center():
    """计算并返回模拟器窗口的中心点坐标"""
    left, top = positions["simulator_top_left"]
    right, bottom = positions["simulator_bottom_right"]
    center_x = left + (right - left) // 2
    center_y = top + (bottom - top) // 2
    return (center_x, center_y)

# 下滑函数
def scroll_down():
    """执行一次下滑（滚轮下滑4次，每次500距离）"""
    # 先将鼠标移动到模拟器中心
    center = get_simulator_center()
    pyautogui.moveTo(center[0], center[1])
    time.sleep(0.5)  # 给一点时间让鼠标到位
    
    # 然后执行滚动
    for _ in range(4):
        pyautogui.scroll(-500)  # 负值表示向下滚动
        time.sleep(0.5)  # 短暂停顿避免过快滚动
