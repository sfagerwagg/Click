import tkinter as tk
import pyautogui
from PIL import Image, ImageDraw
from PIL import Image, ImageTk
import time
import threading
class CoordinateData:
    def __init__(self, position, wait_time=0, click_count=1, click_interval=0):
        self.position = position
        self.wait_time = wait_time
        self.click_count = click_count
        self.click_interval = click_interval
        
class MouseTrackerApp:
    # 初始化应用
    def __init__(self, root):
        self.mask_windows = {}  # 存储遮罩层窗口的字典
        self.is_running = False  # 控制点击执行的标志
        self.is_looping = False  # 控制循环执行的标志

        self.root = root
        self.root.title("鼠标位置跟踪器")
        
  
        button_frame = tk.Frame(root)
        button_frame.pack(side=tk.TOP, padx=5, pady=5, anchor='w')


        self.execute_button = tk.Button(button_frame, text="执行点击操作", command=self.toggle_execution)
        self.execute_button.pack(side=tk.LEFT, padx=5)

        self.loop_button = tk.Button(button_frame, text="循环执行", command=self.toggle_looping)
        self.loop_button.pack(side=tk.LEFT, padx=5)
        
        
        # 创建操作方法的标签们
        label1 = tk.Label(root, text="操作方法", fg="blue", anchor='w')  # 设置文本颜色为蓝色，左对齐
        label1.pack(pady=5, anchor='w')

        label2 = tk.Label(root, text="1.实现多次连点不需要设置点击间隔时间，点击间隔时间默认为0ms", anchor='w')
        label2.pack(pady=5, anchor='w')

        label3 = tk.Label(root, text="2.按下 'a' 键记录鼠标坐标点，按下 'z' 键打印所有坐标点", anchor='w')
        label3.pack(pady=5, anchor='w')

        label4 = tk.Label(root, text="3.按下 'q' 控制台显示当前坐标点，按下 'p' 键/鼠标右键，停止执行", anchor='w')
        label4.pack(pady=5, anchor='w')
        
        label41 = tk.Label(root, text="4.建议每个点创建后点击锁定按钮", anchor='w')
        label41.pack(pady=5, anchor='w')

        label5 = tk.Label(root, text="温馨提示", fg="red", anchor='w')  # 设置文本颜色为红色，左对齐
        label5.pack(pady=5, anchor='w')

        label6 = tk.Label(root, text="如果点击进入死循环，'p'键失灵无法暂停，建议重启电脑", anchor='w')
        label6.pack(pady=5, anchor='w')
        #添加横线
        line = tk.Frame(root, height=2, bg="black")
        line.pack(fill=tk.X, padx=1, pady=1)
        
        label7 = tk.Label(root, text="作者：zfb，联系方式：xxxxxx", anchor='w')
        label7.pack(pady=1, anchor='w')
        
        #添加横线
        line = tk.Frame(root, height=2, bg="black")
        line.pack(fill=tk.X, padx=1, pady=1)
        
        
        self.coordinates_frame = tk.Frame(root)
        self.coordinates_frame.pack()
        
        self.coordinates = {}  # 存储坐标点的字典
        self.button_dict = {}  # 存储删除按钮的字典
        self.root.bind('<Key>', self.on_key_press)  # 绑定键盘事件
        self.root.bind('<Button-3>', self.stop_execution_click)  # 绑定鼠标右键事件
        
  
    # 键盘事件处理函数
    def on_key_press(self, event):
        if event.char == 'a':  # 如果按下 'a' 键
            current_mouse_pos = pyautogui.position()  # 获取当前鼠标位置
            index = len(self.coordinates) + 1  # 确定新坐标点的索引
            self.coordinates[index] = current_mouse_pos  # 将坐标点存入字典
            self.create_coordinate_entry(index, current_mouse_pos)  # 创建显示坐标点的条目
        elif event.char == 'z':  # 如果按下 'z' 键
            self.print_coordinates()  # 打印所有坐标点信息
        elif event.char == 'q':  # 如果按下 'q' 键
            self.draw_point()
        elif event.char == 'p':  # 如果按下 'p' 键
            self.is_running = False  # 停止执行点击操作
            self.stop_loop = True  # 停止循环
    
    # 创建显示坐标点的条目
    def create_coordinate_entry(self, index, position):
        frame = tk.Frame(self.coordinates_frame)  # 创建一个新的框架
        frame.pack(pady=5)  # 设置框架的填充
        
        label = tk.Label(frame, text=f"点 {index}: {position}")  # 创建显示坐标点信息的标签
        label.pack(side=tk.LEFT)  # 设置标签的布局
        
        delete_button = tk.Button(frame, text="删除", command=lambda idx=index: self.delete_coordinate(idx))  # 创建删除按钮
        delete_button.pack(side=tk.LEFT, padx=5)  # 设置删除按钮的布局
        
        # 输入框用来输入等待时间（秒数）
        wait_label = tk.Label(frame, text="等待")
        wait_label.pack(side=tk.LEFT)
        
        wait_entry = tk.Entry(frame)
        wait_entry.pack(side=tk.LEFT, padx=5)
        
        wait_label = tk.Label(frame, text="秒")
        wait_label.pack(side=tk.LEFT)

        # 输入框用来输入点击次数
        click_count_label = tk.Label(frame, text="点击次数")
        click_count_label.pack(side=tk.LEFT)
        
        click_count_entry = tk.Entry(frame)
        click_count_entry.pack(side=tk.LEFT, padx=5)
        
        # 输入框用来输入点击间隔时间（毫秒）
        click_interval_label = tk.Label(frame, text="点击间隔(ms)")
        click_interval_label.pack(side=tk.LEFT)
        
        click_interval_entry = tk.Entry(frame)
        click_interval_entry.pack(side=tk.LEFT, padx=5)
        
          # 锁定按钮
        lock_button = tk.Button(frame, text="锁定", command=lambda entry=wait_entry, count_entry=click_count_entry, interval_entry=click_interval_entry: self.toggle_lock(entry, count_entry, interval_entry))
        lock_button.pack(side=tk.LEFT, padx=5)
        
        self.button_dict[index] = (delete_button, wait_entry, click_count_entry, click_interval_entry)  # 将删除按钮和输入框存入按钮字典
    
    # 执行点击操作
    def execute_clicks(self):
        self.is_running = True
        self.stop_loop = False
        while self.is_running:
            for idx, pos in self.coordinates.items():
                if not self.is_running:  # 如果停止标志为False，则退出
                    break
                
                wait_entry = self.button_dict[idx][1]  # 获取对应点位的等待时间输入框
                wait_time = int(wait_entry.get()) if wait_entry.get().strip().isdigit() else 0  # 获取等待时间（秒数）
            
                click_count_entry = self.button_dict[idx][2]  # 获取点击次数输入框
                click_count = int(click_count_entry.get()) if click_count_entry.get().strip().isdigit() else 1  # 获取点击次数
                
                click_interval_entry = self.button_dict[idx][3]  # 获取点击间隔时间输入框
                click_interval = int(click_interval_entry.get()) if click_interval_entry.get().strip().isdigit() else 0  # 获取点击间隔时间（毫秒）
                
                for _ in range(click_count):
                    if not self.is_running:  # 如果停止标志为False，则退出
                        break
                    # 移动鼠标并点击
                    pyautogui.moveTo(pos.x-5, pos.y-5)
                    pyautogui.click(pos.x-5, pos.y-5, button='left')
                    print(f"点击了点 {idx}: {pos.x}, {pos.y}")
                    print("等待时间：", click_interval)
                    time.sleep(click_interval / 1000)  # 等待点击间隔时间
                
                # 等待指定时间
                time.sleep(wait_time)
                
            if not self.is_looping or self.stop_loop:
                break
    
    # 切换执行点击操作
    def toggle_execution(self):
        if self.is_running:
            self.is_running = False
            self.execute_button.config(text="执行点击操作")
        else:
            threading.Thread(target=self.execute_clicks).start()
            self.execute_button.config(text="停止点击操作")
    
    # 切换循环执行
    def toggle_looping(self):
        self.is_looping = not self.is_looping
        self.loop_button.config(text="停止循环" if self.is_looping else "循环执行")
    
    # 删除坐标点
    def delete_coordinate(self, index):
        if index in self.coordinates:  # 如果索引存在于坐标字典中
            del self.coordinates[index]  # 删除坐标点
            self.button_dict[index][0].destroy()  # 销毁对应的删除按钮
            self.button_dict[index][1].destroy()  # 销毁对应的等待时间输入框
            self.button_dict[index][2].destroy()  # 销毁对应的点击次数输入框
            self.button_dict[index][3].destroy()  # 销毁对应的点击间隔时间输入框
            del self.button_dict[index]  # 从按钮字典中删除按钮
            self.update_coordinates_labels()  # 更新显示的坐标点条目
             
            # 销毁遮罩层窗口
            self.destroy_mask_window(index)
    
    # 更新显示的坐标点条目
    def update_coordinates_labels(self):
        for widget in self.coordinates_frame.winfo_children():  # 清除之前显示的所有坐标点条目
            widget.destroy()
        
        for idx, pos in self.coordinates.items():  # 重新创建更新后的所有坐标点条目
            self.create_coordinate_entry(idx, pos)
    
    # 打印所有坐标点信息
    def print_coordinates(self):
        print("当前所有坐标点：")
        for idx, pos in self.coordinates.items():
            print(f"点 {idx}: {pos.x}, {pos.y}")
    
    # 销毁遮罩层窗口
    def destroy_mask_window(self, index):
        mask_window = self.mask_windows.get(index)
        if mask_window:
            mask_window.destroy()
            del self.mask_windows[index]
    
    # 绘制圆圈和文本
    def draw_point(self):
        for idx, pos in self.coordinates.items():
            # 创建红点
            size = 5
            img = Image.new('RGBA', (size, size), (255, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            draw.ellipse((0, 0, size, size), fill=(255, 0, 0, 255))

            # 保存红点图像为PNG文件
            img.save('red_dot.png')

            # 创建遮罩层窗口
            mask = tk.Toplevel(self.root)
            mask.attributes('-topmost', True)
            mask.overrideredirect(True)
            mask.geometry(f'{size+15}x{size+15}+{pos.x}+{pos.y}')
            mask.attributes('-transparentcolor', 'white')

            # 在遮罩层上绘制红点和文本
            canvas = tk.Canvas(mask, width=size+15, height=size+15, bg='white')
            canvas.pack()
            
            # 使用PIL库打开红点图像，并转换为PhotoImage格式
            red_dot_image = Image.open('red_dot.png')
            red_dot_image = ImageTk.PhotoImage(red_dot_image)
            
            # 在Canvas上创建红点和文本
            canvas.create_image(0, 0, anchor='nw', image=red_dot_image)
             
            # 计算文本的位置，使其显示在遮罩层窗口的中心
            text_x = (size + 15) // 2
            text_y = (size + 15) // 2
            
            # 在Canvas上创建文本
            canvas.create_text(text_x, text_y, text=f"{idx}", anchor='center', font=("Helvetica", 12), fill='black')

            # 保持图片对象的引用，避免被垃圾回收
            canvas.image = red_dot_image
            # 保存遮罩层窗口的引用，方便后续销毁
            self.mask_windows[idx] = mask

     # 鼠标右键事件处理函数
    def stop_execution_click(self, event):
        self.is_running = False
        self.stop_loop = True
        self.execute_button.config(text="执行点击操作")
    # 切换锁定状态
    def toggle_lock(self, *entries):
        for entry in entries:
            state = entry["state"]
            if state == "normal":
                entry.config(state="disabled")
            else:
                entry.config(state="normal")
    
     # 鼠标右键事件处理函数
    def stop_execution_click(self, event):
        self.is_running = False
        self.stop_loop = True
        self.execute_button.config(text="执行点击操作")
    # 运行应用
    def run(self):
        self.root.mainloop()  # 运行主程序的主循环

if __name__ == "__main__":
    root = tk.Tk()  # 创建 tkinter 应用的根窗口
    app = MouseTrackerApp(root)  # 创建鼠标位置跟踪器应用
    app.run()  # 运行应用的主循环
