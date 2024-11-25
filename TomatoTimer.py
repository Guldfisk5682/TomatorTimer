import tkinter as tk
import math
import os
import sys
import json
from settings import get_user_settings, load_user_inputs
from visualization import visualize_data
from recommendation import suggest_settings
import tkinter.messagebox as messagebox  # 导入消息框模块

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)
# ---------------------------- CONSTANTS ------------------------------- #
PINK = "#e2979c"
RED = "#e7305b"
GREEN = "#9bdeac"
YELLOW = "#f7f5dd"
FONT_NAME = "Courier"

# 默认设置
SETTINGS = {
    "work_type": "Focus Session",
    "work_minutes": 25,
    "short_break": 5,
    "long_break": 20
}

# 加载用户设置
user_settings = load_user_inputs()
if user_settings:
    SETTINGS = user_settings[-1]
    #加载最新的用户设置

WORK_MIN = SETTINGS["work_minutes"]
SHORT_BREAK_MIN = SETTINGS["short_break"]
LONG_BREAK_MIN = SETTINGS["long_break"]

# ---------------------------- 初始默认设置 ------------------------------- #
reps = 0    #番茄循环数
timer = None
distract_count = 0    #分心次数
longest_focus = 0    #最长专注时间
current_focus_time = 0    #当前专注时间

# 添加 DATA_PATH 定义
DATA_PATH = resource_path("user_data.json")

# ---------------------------- FUNCTIONS ------------------------------- #
def open_settings():
    """打开设置窗口并更新设置"""
    global SETTINGS, WORK_MIN, SHORT_BREAK_MIN, LONG_BREAK_MIN
    new_settings = get_user_settings()
    if new_settings:  # 确保有返回数据
        SETTINGS = new_settings
        WORK_MIN = SETTINGS["work_minutes"]
        SHORT_BREAK_MIN = SETTINGS["short_break"]
        LONG_BREAK_MIN = SETTINGS["long_break"]

def load_user_data():
    """加载用户数据，如果不存在则返回空字典"""
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, 'r', encoding='utf-8') as file:
            return json.load(file)
    return {"sessions": []}

def save_user_data(data):
    """保存用户数据到 user_data.json"""
    existing_data = load_user_data()
    existing_data.setdefault("sessions", []).append({
        "work_time": data.get("work_time", 0),
        "distract_count": data.get("distract_count", 0),
        "longest_focus": data.get("longest_focus", 0),
        "settings": data.get("settings", {})
    })
    '''使用setdefault方法确保existing_data中存在sessions键，如果不存在则初始化为空列表。
    然后，将当前会话的数据作为一个字典添加到sessions列表中。
    这里使用data.get方法来安全地获取传入的data字典中的各项值，如果某个键不存在，则使用默认值（如0或空字典）。'''
    with open(DATA_PATH, 'w', encoding='utf-8') as file:
        json.dump(existing_data, file, indent=4, ensure_ascii=False)
        '''dump()方法将Python对象转换为JSON格式，并写入文件。
        indent=4表示每行缩进4个空格，ensure_ascii=False表示不强制使用ASCII编码。'''

def distract():
    """记录一次分心，并更新最长专注时间"""
    global distract_count, longest_focus, current_focus_time
    distract_count += 1
    if current_focus_time > longest_focus:
        longest_focus = current_focus_time
    save_user_data({
        "work_time": WORK_MIN * 60 - current_focus_time,
        "distract_count": distract_count,
        "longest_focus": longest_focus,
        "settings": SETTINGS
    })
    
    # 更新标签显示为“分心了”
    timer_label.config(text="分心了", fg="orange")
    
    # 2秒后将标签文本恢复为当前的工作类型
    window.after(2000, lambda: timer_label.config(text=SETTINGS["work_type"], fg=GREEN))

def reset_timer():
    """重置计时器并保存当前数据"""
    if timer:
        window.after_cancel(timer)
    global reps, distract_count, longest_focus, current_focus_time
    # 保存当前数据到 user_data.json
    save_user_data({
        "work_time": WORK_MIN * 60 - current_focus_time,
        "distract_count": distract_count,
        "longest_focus": longest_focus,
        "settings": SETTINGS
    })
    # 重置全局变量
    reps = 0
    distract_count = 0
    longest_focus = 0
    current_focus_time = 0
    # 重置UI元素
    canvas.itemconfig(timer_countdown, text="00:00")
    timer_label.config(text="个性化番茄钟", fg=GREEN)
    checkbox.config(text="")

def cancel_timer():
    """取消当前计时并重置所有相关变量"""
    if timer:
        window.after_cancel(timer)
    global reps, distract_count, longest_focus, current_focus_time
    reps = 0
    distract_count = 0
    longest_focus = 0
    current_focus_time = 0
    # 重置UI元素
    canvas.itemconfig(timer_countdown, text="00:00")
    timer_label.config(text="个性化番茄钟", fg=GREEN)
    checkbox.config(text="")

def start_timer():
    """开始计时，根据当前的循环次数决定是工作还是休息"""
    global reps, current_focus_time
    reps += 1
    current_focus_time = WORK_MIN * 60

    work_sec = WORK_MIN * 60
    short_break_sec = SHORT_BREAK_MIN * 60
    long_break_sec = LONG_BREAK_MIN * 60

    if reps in [1, 3, 5, 7]:
        timer_label.config(text=SETTINGS["work_type"], fg=GREEN)
        countdown(work_sec)
    elif reps == 8:
        timer_label.config(text="Relaxation Time", fg=RED)
        countdown(long_break_sec)   
    elif reps in [2, 4, 6]:
        timer_label.config(text="Break", fg=PINK)
        countdown(short_break_sec)        

# ---------------------------- 倒计时机制 ------------------------------- # 
def countdown(count):
    """倒计时机制，每秒减少一次计时"""
    
    # 计算剩余时间的分钟和秒数
    count_min = math.floor(count / 60)  # 将总秒数转换为分钟
    count_sec = count % 60               # 计算剩余的秒数

    # 如果秒数小于10，前面补零以保持格式一致
    if count_sec < 10:
        count_sec = f"0{count_sec}"

    # 更新画布上的倒计时显示
    canvas.itemconfig(timer_countdown, text=f"{count_min}:{count_sec}")
    
    # 如果倒计时还未结束，继续递归调用countdown函数
    if count > 0:
        global timer  # 声明全局变量timer，用于存储定时器的ID
        timer = window.after(1000, countdown, count - 1)  # 每1000毫秒（1秒）调用一次countdown函数，传入剩余时间减1
    else:
        # 如果倒计时结束，根据当前的循环次数决定下一步操作
        if reps < 8:
            start_timer()  # 如果循环次数小于8，开始下一个计时
        else:
            timer_label.config(text="完成番茄钟!")  # 如果循环次数达到8，显示“完成番茄钟!”

    # 计算已完成的工作会话数量，并更新勾选框的显示
    marks = ""  # 初始化勾选标记字符串
    work_sessions = math.floor(reps / 2)  # 每两个工作会话增加一个勾选标记
    for i in range(work_sessions):
        marks += "✔"  # 添加勾选标记
    checkbox.config(text=marks)  # 更新勾选框的文本显示

def show_visualization():
    """调用可视化函数并传递设置"""
    visualize_data(SETTINGS)

# ---------------------------- UI 界面 ------------------------------- #
window = tk.Tk()
window.title("个性化番茄钟")
window.state('zoomed')  # 强制最大化窗口
window.minsize(width=300, height=550)
window.config(padx=60, pady=80, bg=YELLOW)

# 设置所有列和行的权重，确保内容居中显示
for i in range(8):  # 7列以容纳所有按钮
    window.grid_columnconfigure(i, weight=1)
for i in range(4):  # 4行
    window.grid_rowconfigure(i, weight=1)

# Timer Label 
timer_label = tk.Label(text="个性化番茄钟", bg=YELLOW, fg=GREEN, font=(FONT_NAME, 35, "bold"))
timer_label.grid(row=0, column=3, pady=(0, 20), sticky='n')

# Timer Canvas 显示番茄图标和倒计时
canvas = tk.Canvas(width=200, height=224, bg=YELLOW, highlightthickness=0)
background_img = tk.PhotoImage(file=resource_path("tomato.png"))
canvas.create_image(100, 112, image=background_img)
timer_countdown = canvas.create_text(100, 130, text="00:00", fill="white", font=(FONT_NAME, 35, "bold"))
canvas.grid(row=1, column=3, pady=(0, 20), sticky='n')

# 按钮布局：将所有按钮放在画布下方的框架中，并保持紧凑
button_frame = tk.Frame(window, bg=YELLOW)
button_frame.grid(row=2, column=0, columnspan=7, pady=10)

# 取消按钮
cancel_button = tk.Button(button_frame, text="取消", command=cancel_timer)
cancel_button.grid(row=0, column=0, padx=5, pady=5)

# 设置按钮
settings_button = tk.Button(button_frame, text="设置", command=open_settings)
settings_button.grid(row=0, column=1, padx=5, pady=5)

# Start 按钮
start_button = tk.Button(button_frame, text="Start", command=start_timer)
start_button.grid(row=0, column=2, padx=5, pady=5)

# Reset 按钮
reset_button = tk.Button(button_frame, text="Reset", command=reset_timer)
reset_button.grid(row=0, column=3, padx=5, pady=5)

# 分心按钮
distract_button = tk.Button(button_frame, text="分心", command=distract)
distract_button.grid(row=0, column=4, padx=5, pady=5)

# 可视化按钮
visualize_button = tk.Button(button_frame, text="可视化", command=show_visualization)
visualize_button.grid(row=0, column=5, padx=5, pady=5)

# 建议按钮
suggest_button = tk.Button(button_frame, text="建议", command=suggest_settings)
suggest_button.grid(row=0, column=6, padx=5, pady=5)

# 退出按钮
exit_button = tk.Button(button_frame, text="退出", command=window.quit)
exit_button.grid(row=0, column=7, padx=5, pady=5)

# Checkbox，用于显示已完成的番茄数量
checkbox = tk.Label(bg=YELLOW, fg=GREEN, font=(FONT_NAME, 20, "bold"))
checkbox.grid(row=3, column=3, pady=(20, 0), sticky='s')

window.mainloop()