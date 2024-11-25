import json
import os
import sys
import tkinter as tk
from tkinter import simpledialog
import tkinter.messagebox as messagebox

def resource_path(relative_path):
    """ 获取资源的绝对路径，适用于开发和PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

USER_INPUT_PATH = resource_path("user_input.json")

def load_user_inputs():
    """ 加载用户的设置输入 """
    if os.path.exists(USER_INPUT_PATH):
        with open(USER_INPUT_PATH, 'r', encoding='utf-8') as file:
            return json.load(file)
    return []

def save_user_input(data):
    """ 保存用户的设置输入，最多保存最近5组 """
    inputs = load_user_inputs()
    inputs.append(data)
    if len(inputs) > 5:
        inputs = inputs[-5:]
    with open(USER_INPUT_PATH, 'w', encoding='utf-8') as file:
        json.dump(inputs, file, indent=4, ensure_ascii=False)

def get_user_settings():
    """ 显示设置窗口，获取用户输入并返回设置数据 """
    settings_window = tk.Toplevel()
    settings_window.title("设置")
    settings_window.geometry("300x300")
    settings_window.config(bg="#f7f5dd")
    settings_window.grab_set()

    tk.Label(settings_window, text="工作类型：", bg="#f7f5dd").grid(row=0, column=0, padx=10, pady=10, sticky='e')
    work_type_entry = tk.Entry(settings_window)
    work_type_entry.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(settings_window, text="专注时间（分钟）：", bg="#f7f5dd").grid(row=1, column=0, padx=10, pady=10, sticky='e')
    work_minutes_entry = tk.Entry(settings_window)
    work_minutes_entry.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(settings_window, text="短休息时间（分钟）：", bg="#f7f5dd").grid(row=2, column=0, padx=10, pady=10, sticky='e')
    short_break_entry = tk.Entry(settings_window)
    short_break_entry.grid(row=2, column=1, padx=10, pady=10)

    tk.Label(settings_window, text="长休息时间（分钟）：", bg="#f7f5dd").grid(row=3, column=0, padx=10, pady=10, sticky='e')
    long_break_entry = tk.Entry(settings_window)
    long_break_entry.grid(row=3, column=1, padx=10, pady=10)

    settings_data = {}

    def submit_settings():
        """ 提交用户输入并保存 """
        work_type = work_type_entry.get()
        try:
            work_minutes = int(work_minutes_entry.get())
            short_break = int(short_break_entry.get())
            long_break = int(long_break_entry.get())
        except ValueError:
            messagebox.showerror("输入错误", "时间请输入整数值。")
            return

        settings_data["work_type"] = work_type
        settings_data["work_minutes"] = work_minutes
        settings_data["short_break"] = short_break
        settings_data["long_break"] = long_break

        save_user_input(settings_data)
        settings_window.destroy()

    submit_button = tk.Button(settings_window, text="提交", command=submit_settings, bg="#e2979c")
    submit_button.grid(row=4, column=0, columnspan=2, pady=20)

    settings_window.wait_window()
    return settings_data