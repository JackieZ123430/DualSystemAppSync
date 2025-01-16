import os
import shutil
import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext
from tkinter import simpledialog
import configparser


# 初始化主窗口
root = tk.Tk()
root.title("双系统共享程序工具")
root.geometry("1500x1100")  # 调整窗口大小

# 配置文件路径
config_file = "system_config.ini"

# 全局变量
appdata_selected = False


# 检查管理员权限
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


# 确保以管理员身份运行
def request_admin_permission():
    if not is_admin():
        messagebox.showwarning("管理员权限", "当前脚本没有管理员权限，请重新以管理员身份运行！")
        sys.exit()


# 创建符号链接
def create_symbolic_link(source, dest):
    try:
        os.symlink(source, dest)
        return True
    except FileExistsError:
        messagebox.showinfo("信息", f"符号链接已存在：{dest}")
        return True
    except Exception as e:
        output_text.insert(tk.END, f"创建符号链接失败：{e}\n")
        return False


# 显示信息功能
def display_info():
    global appdata_selected
    system1 = system1_entry.get()
    user_name1 = user_name1_entry.get()

    if not system1 or not user_name1:
        messagebox.showerror("错误", "请先填写1系统盘符和1系统用户！")
        return

    app_name = app_name_entry.get()
    if not app_name:
        messagebox.showerror("错误", "请输入程序名称！")
        return

    base_path = os.path.join(system1, "Users", user_name1)
    if appdata_selected:
        # AppData路径
        program_path = os.path.join(base_path, "AppData", "Local", app_name)
        shortcut_path = os.path.join(base_path, "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs", app_name)
    else:
        # Program Files路径
        program_path = os.path.join(system1, "Program Files", app_name)
        shortcut_path = os.path.join(system1, "Program Files (x86)", app_name)

    output_text.insert(tk.END, f"程序文件夹路径: {program_path}\n")
    output_text.insert(tk.END, f"快捷方式文件夹路径: {shortcut_path}\n")


# 执行操作功能
def execute_operation():
    global appdata_selected
    system1 = system1_entry.get()
    system2 = system2_entry.get()
    user_name1 = user_name1_entry.get()
    user_name2 = user_name2_entry.get()

    if not system1 or not system2 or not user_name1 or not user_name2:
        messagebox.showerror("错误", "请填写完整的盘符和用户目录！")
        return

    user_folder1 = os.path.join(system1, "Users", user_name1)
    user_folder2 = os.path.join(system2, "Users", user_name2)

    app_name = app_name_entry.get()
    if not app_name:
        messagebox.showerror("错误", "请输入程序名称！")
        return

    appdata_option = appdata_var.get()
    if appdata_option == 1:  # 如果程序在 AppData 文件夹
        source_appdata = os.path.join(user_folder1, "AppData", "Local", app_name)
        dest_appdata = os.path.join(user_folder2, "AppData", "Local", app_name)
        if create_symbolic_link(source_appdata, dest_appdata):
            output_text.insert(tk.END, f"创建符号链接成功：{source_appdata} -> {dest_appdata}\n")
        else:
            return

    # 复制快捷方式
    source_shortcut = os.path.join(user_folder1, "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs", app_name)
    dest_shortcut = os.path.join(user_folder2, "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs", app_name)
    try:
        shutil.copytree(source_shortcut, dest_shortcut, dirs_exist_ok=True)
        output_text.insert(tk.END, f"快捷方式复制完成：{source_shortcut} -> {dest_shortcut}\n")
    except FileNotFoundError:
        output_text.insert(tk.END, f"未找到快捷方式目录：{source_shortcut}\n")
        shortcut_dir = filedialog.askdirectory(title="选择快捷方式目录")
        if shortcut_dir:
            try:
                shutil.copytree(shortcut_dir, dest_shortcut, dirs_exist_ok=True)
                output_text.insert(tk.END, f"快捷方式复制完成：{shortcut_dir} -> {dest_shortcut}\n")
            except Exception as e:
                output_text.insert(tk.END, f"复制快捷方式失败：{e}\n")
    except Exception as e:
        output_text.insert(tk.END, f"复制快捷方式失败：{e}\n")


# 设置系统盘符和用户目录
def set_system_directories():
    system1 = system1_entry.get()
    system2 = system2_entry.get()
    user_name1 = user_name1_entry.get()
    user_name2 = user_name2_entry.get()

    if not system1 or not system2 or not user_name1 or not user_name2:
        messagebox.showerror("错误", "请填写所有字段！")
        return
    
    with open(config_file, 'w') as f:
        f.write(f"1系统盘符={system1}\n")
        f.write(f"1系统用户={user_name1}\n")
        f.write(f"2系统盘符={system2}\n")
        f.write(f"2系统用户={user_name2}\n")
    
    messagebox.showinfo("成功", "系统盘符和用户目录已保存！")


# 载入系统配置
def load_system_config():
    if os.path.exists(config_file):
        config = configparser.ConfigParser()
        config.read(config_file)

        system1_entry.delete(0, tk.END)
        system1_entry.insert(0, config.get('SYSTEM', '1系统盘符'))
        
        user_name1_entry.delete(0, tk.END)
        user_name1_entry.insert(0, config.get('SYSTEM', '1系统用户'))
        
        system2_entry.delete(0, tk.END)
        system2_entry.insert(0, config.get('SYSTEM', '2系统盘符'))
        
        user_name2_entry.delete(0, tk.END)
        user_name2_entry.insert(0, config.get('SYSTEM', '2系统用户'))
    else:
        messagebox.showerror("错误", "配置文件不存在！")


# 生成系统配置
def generate_system_config():
    if not os.path.exists(config_file):
        config = configparser.ConfigParser()
        config.add_section('SYSTEM')
        config.set('SYSTEM', '1系统盘符', system1_entry.get())
        config.set('SYSTEM', '1系统用户', user_name1_entry.get())
        config.set('SYSTEM', '2系统盘符', system2_entry.get())
        config.set('SYSTEM', '2系统用户', user_name2_entry.get())
        
        with open(config_file, 'w') as configfile:
            config.write(configfile)

        messagebox.showinfo("成功", "配置文件生成成功！")
    else:
        messagebox.showinfo("信息", "配置文件已存在！")


# 关于作者
def about_author():
    messagebox.showinfo("关于作者", "Edit By JackieZhang\n\nGitHub: https://github.com/users/JackieZ123430/projects/2")


# 主菜单
menubar = tk.Menu(root)

# 文件菜单
filemenu = tk.Menu(menubar, tearoff=0)
filemenu.add_command(label="载入系统配置", command=load_system_config)
filemenu.add_command(label="生成系统配置", command=generate_system_config)
menubar.add_cascade(label="文件", menu=filemenu)

# 关于菜单
aboutmenu = tk.Menu(menubar, tearoff=0)
aboutmenu.add_command(label="关于作者", command=about_author)
menubar.add_cascade(label="关于", menu=aboutmenu)

root.config(menu=menubar)

# 系统盘符和用户目录设置框
frame1 = tk.LabelFrame(root, text="系统盘符和用户目录", padx=10, pady=10)
frame1.pack(fill="x", padx=10, pady=10)

tk.Label(frame1, text="1系统盘符 (例如 F:):", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=5)
system1_entry = tk.Entry(frame1, font=("Arial", 12), width=40)
system1_entry.grid(row=0, column=1, padx=10, pady=5)

tk.Label(frame1, text="1系统用户名称:", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=5)
user_name1_entry = tk.Entry(frame1, font=("Arial", 12), width=40)
user_name1_entry.grid(row=1, column=1, padx=10, pady=5)

tk.Label(frame1, text="2系统盘符 (例如 C:):", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=5)
system2_entry = tk.Entry(frame1, font=("Arial", 12), width=40)
system2_entry.grid(row=2, column=1, padx=10, pady=5)

tk.Label(frame1, text="2系统用户名称:", font=("Arial", 12)).grid(row=3, column=0, padx=10, pady=5)
user_name2_entry = tk.Entry(frame1, font=("Arial", 12), width=40)
user_name2_entry.grid(row=3, column=1, padx=10, pady=5)

save_button = tk.Button(frame1, text="保存系统目录", command=set_system_directories, font=("Arial", 12))
save_button.grid(row=4, column=0, columnspan=2, pady=10)

# 程序操作框
frame2 = tk.LabelFrame(root, text="程序操作", padx=10, pady=10)
frame2.pack(fill="x", padx=10, pady=10)

tk.Label(frame2, text="程序名称:", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=5)
app_name_entry = tk.Entry(frame2, font=("Arial", 12), width=40)
app_name_entry.grid(row=0, column=1, padx=10, pady=5)

appdata_var = tk.IntVar()
appdata_check = tk.Checkbutton(frame2, text="程序是否在 AppData 文件夹", variable=appdata_var, font=("Arial", 12))
appdata_check.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

info_button = tk.Button(frame2, text="显示信息", command=display_info, font=("Arial", 12))
info_button.grid(row=2, column=0, padx=10, pady=10)

execute_button = tk.Button(frame2, text="执行操作", command=execute_operation, font=("Arial", 12))
execute_button.grid(row=2, column=1, padx=10, pady=10)

# 操作日志框
frame3 = tk.LabelFrame(root, text="操作日志", padx=10, pady=10)
frame3.pack(fill="both", expand=True, padx=10, pady=10)

output_text = scrolledtext.ScrolledText(frame3, width=80, height=20, font=("Arial", 12))
output_text.pack(fill="both", expand=True, padx=10, pady=10)

# 启动 GUI
root.mainloop()
