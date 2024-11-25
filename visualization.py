import json
import os
import sys
import matplotlib.pyplot as plt
import matplotlib
import tkinter.messagebox as messagebox
from datetime import datetime

# 设置matplotlib支持中文显示
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def resource_path(relative_path):
    """获取资源的绝对路径，适用于开发和PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# 定义数据文件路径
DATA_PATH = resource_path("user_data.json")

def load_user_data():
    """加载用户数据"""
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, 'r', encoding='utf-8') as file:
            return json.load(file)
    return {}

def visualize_data(settings):
    """可视化用户数据"""
    data = load_user_data()
    sessions = data.get("sessions", [])
    
    if not sessions or len(sessions) < 2:
        messagebox.showinfo("提示", "没有足够的用户数据可视化。\n至少需要2组数据。")
        return

    # 获取当前会话和上一个会话的数据
    current_session = sessions[-1]  # 最新的会话
    previous_session = sessions[-2]  # 上一个会话

    # 提取数据
    current_longest_focus = current_session["longest_focus"]
    current_distract_count = current_session["distract_count"]
    previous_longest_focus = previous_session["longest_focus"]
    previous_distract_count = previous_session["distract_count"]

    # 生产力评分历史
    productivity_scores = [
        s["work_time"] / (s["settings"]["work_minutes"] * 60) * 100 - s["distract_count"]
        for s in sessions
    ]

    # 创建图表
    plt.figure(figsize=(10,16))

    # 第一个子图：最长专注时间比较
    plt.subplot(3, 1, 1)
    plt.bar(["本轮专注", "上次专注"], [current_longest_focus, previous_longest_focus], color=['blue', 'orange'])
    plt.title('最长专注时间比较', fontsize=14)
    plt.ylabel('专注时间 (分钟)', fontsize=12)
    plt.grid(axis='y')

    # 第二个子图：总分心次数比较
    plt.subplot(3, 1, 2)
    plt.bar(["本轮分心", "上次分心"], [current_distract_count, previous_distract_count], color=['red', 'green'])
    plt.title('总分心次数比较', fontsize=14)
    plt.ylabel('分心次数', fontsize=12)
    plt.grid(axis='y')

    # 第三个子图：生产力评分历史
    plt.subplot(3, 1, 3)
    plt.plot(productivity_scores, marker='o', color='green')
    plt.title('生产力评分历史', fontsize=14)
    plt.xlabel('会话', fontsize=12)
    plt.ylabel('生产力评分', fontsize=12)
    plt.grid()

    plt.tight_layout()
    plt.show() 