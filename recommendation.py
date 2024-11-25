import json
import os
import sys
from sklearn.linear_model import LinearRegression
import numpy as np
import tkinter as tk
import tkinter.messagebox as messagebox
import tkinter.simpledialog as simpledialog

def resource_path(relative_path):
    """获取资源的绝对路径，适用于开发和PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# 定义数据文件路径
DATA_PATH = resource_path("user_data.json")
USER_INPUT_PATH = resource_path("user_input.json")

def load_user_data():
    """加载用户数据"""
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, 'r', encoding='utf-8') as file:
            return json.load(file)
    return {}

def list_work_types():
    """列出所有可用的工作类型"""
    data = load_user_data()
    work_types = set()
    for session in data.get("sessions", []):
        work_types.add(session["settings"]["work_type"])
    return sorted(list(work_types))

def create_type_selection_window():
    """创建工作类型选择窗口"""
    # 获取工作类型列表
    work_types = list_work_types()
    if not work_types:
        messagebox.showinfo("提示", "未找到任何工作类型数据。")
        return

    # 创建选择窗口
    selection_window = tk.Toplevel()
    selection_window.title("选择工作类型")
    selection_window.geometry("300x400")
    selection_window.config(bg="#f7f5dd")
    
    # 创建滚动框架
    canvas = tk.Canvas(selection_window, bg="#f7f5dd")
    scrollbar = tk.Scrollbar(selection_window, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#f7f5dd")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # 为每个工作类型创建按钮
    def analyze_type(work_type):
        selection_window.destroy()
        analyze_work_type(work_type)

    for work_type in work_types:
        tk.Button(
            scrollable_frame,
            text=work_type,
            command=lambda t=work_type: analyze_type(t),
            width=20,
            bg="#e2979c",
            fg="white",
            font=("Arial", 12)
        ).pack(pady=5)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

def analyze_work_type(work_type):
    """分析特定工作类型的数据并提供建议"""
    data = load_user_data()
    sessions = data.get("sessions", [])
    
    # 筛选选定工作类型的数据
    type_sessions = [s for s in sessions if s["settings"]["work_type"] == work_type]
    
    if len(type_sessions) < 3:
        messagebox.showinfo("提示", f"工作类型 '{work_type}' 的数据不足，无法提供建议。\n至少需要3组数据。")
        return
    
    # 准备训练数据
    X = np.array([s["work_time"] for s in type_sessions]).reshape(-1, 1)
    y = np.array([s["longest_focus"] for s in type_sessions])
    
    # 训练线性回归模型
    model = LinearRegression()
    model.fit(X, y)
    
    # 计算建议的专注时间
    avg_work_time = np.mean([s["work_time"] for s in type_sessions])
    suggested_time = int(model.predict([[avg_work_time]])[0])
    
    # 计算平均分心次数
    avg_distractions = np.mean([s["distract_count"] for s in type_sessions])
    
    # 显示详细建议
    messagebox.showinfo(
        "个性化建议",
        f"工作类型: {work_type}\n\n"
        f"建议的专注时间: {suggested_time} 分钟\n"
        f"平均专注时间: {int(avg_work_time/60)} 分钟\n"
        f"平均分心次数: {avg_distractions:.1f} 次\n\n"
        f"分析基于 {len(type_sessions)} 组历史数据\n\n"
        f"建议：\n"
        f"设置专注时间为 {suggested_time} 分钟"
    )

def suggest_settings():
    """显示工作类型选择窗口"""
    data = load_user_data()
    if not data.get("sessions"):
        messagebox.showinfo("提示", "没有用户数据，无法提供建议。")
        return
    
    if len(data["sessions"]) < 3:
        messagebox.showinfo("提示", "数据不足，无法提供建议。\n至少需要3组数据才能进行分析。")
        return
    
    create_type_selection_window()