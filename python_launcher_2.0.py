import tkinter as tk
from tkinter import messagebox, filedialog
import subprocess
import os
import sys
import json

# 配置文件路径
CONFIG_FILE = "program_launcher_config.json"

# 默认程序列表（如果配置文件不存在则使用这些）
default_programs = [
    {
        "name": "示例Python脚本",
        "path": "example_script.py",
        "type": "python",
        "venv": "",  # 虚拟环境路径（可选）
        "args": "",  # 命令行参数（可选）
        "default": True
    },
    {
        "name": "另一个Python程序",
        "path": "another_script.py",
        "type": "python",
        "venv": "",
        "args": "",
        "default": False
    }
]

def load_config():
    """加载配置文件"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            messagebox.showerror("错误", "配置文件损坏，使用默认配置")
            return default_programs
    return default_programs

def save_config(programs):
    """保存配置文件"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(programs, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        messagebox.showerror("错误", f"保存配置失败: {str(e)}")
        return False

class ProgramLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Python程序启动器")
        self.root.geometry("500x400")
        
        # 加载程序列表
        self.programs = load_config()
        
        # 创建选择框
        self.vars = []
        tk.Label(root, text="请选择要启动的Python程序:", font=("Arial", 12)).pack(pady=10)
        
        # 创建滚动区域
        frame = tk.Frame(root)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        canvas = tk.Canvas(frame)
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 添加程序选择框
        for i, program in enumerate(self.programs):
            var = tk.BooleanVar(value=program.get("default", False))
            self.vars.append(var)
            
            # 创建每个程序的框架
            program_frame = tk.Frame(self.scrollable_frame)
            program_frame.pack(fill="x", pady=2)
            
            cb = tk.Checkbutton(program_frame, text=program["name"], variable=var, 
                               font=("Arial", 10))
            cb.pack(side=tk.LEFT)
            
            # 显示程序路径
            path_label = tk.Label(program_frame, text=program["path"], fg="gray")
            path_label.pack(side=tk.LEFT, padx=10)
            
            # 编辑按钮
            edit_btn = tk.Button(program_frame, text="编辑", 
                                command=lambda idx=i: self.edit_program(idx))
            edit_btn.pack(side=tk.RIGHT)
        
        # 创建按钮框架
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="运行选中程序", command=self.launch_programs, 
                 bg="lightgreen", font=("Arial", 10)).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="添加程序", command=self.add_program,
                 font=("Arial", 10)).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="保存配置", command=self.save_configuration,
                 font=("Arial", 10)).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="取消", command=root.quit,
                 font=("Arial", 10)).pack(side=tk.LEFT, padx=10)
    
    def edit_program(self, index):
        """编辑程序配置"""
        program = self.programs[index]
        
        edit_window = tk.Toplevel(self.root)
        edit_window.title("编辑程序")
        edit_window.geometry("400x300")
        
        tk.Label(edit_window, text="程序名称:").pack(pady=5)
        name_var = tk.StringVar(value=program["name"])
        name_entry = tk.Entry(edit_window, textvariable=name_var, width=40)
        name_entry.pack(pady=5)
        
        tk.Label(edit_window, text="程序路径:").pack(pady=5)
        path_var = tk.StringVar(value=program["path"])
        path_entry = tk.Entry(edit_window, textvariable=path_var, width=40)
        path_entry.pack(pady=5)
        
        tk.Button(edit_window, text="浏览...", 
                 command=lambda: self.browse_file(path_var)).pack(pady=5)
        
        tk.Label(edit_window, text="虚拟环境路径(可选):").pack(pady=5)
        venv_var = tk.StringVar(value=program.get("venv", ""))
        venv_entry = tk.Entry(edit_window, textvariable=venv_var, width=40)
        venv_entry.pack(pady=5)
        
        tk.Button(edit_window, text="浏览虚拟环境...", 
                 command=lambda: self.browse_venv(venv_var)).pack(pady=5)
        
        tk.Label(edit_window, text="命令行参数(可选):").pack(pady=5)
        args_var = tk.StringVar(value=program.get("args", ""))
        args_entry = tk.Entry(edit_window, textvariable=args_var, width=40)
        args_entry.pack(pady=5)
        
        default_var = tk.BooleanVar(value=program.get("default", False))
        default_cb = tk.Checkbutton(edit_window, text="默认选中", variable=default_var)
        default_cb.pack(pady=5)
        
        def save_changes():
            self.programs[index] = {
                "name": name_var.get(),
                "path": path_var.get(),
                "type": "python",  # 默认为Python程序
                "venv": venv_var.get(),
                "args": args_var.get(),
                "default": default_var.get()
            }
            edit_window.destroy()
            # 刷新界面
            self.refresh_ui()
        
        tk.Button(edit_window, text="保存", command=save_changes).pack(pady=10)
        tk.Button(edit_window, text="取消", command=edit_window.destroy).pack(pady=5)
    
    def browse_file(self, path_var):
        """浏览文件"""
        filename = filedialog.askopenfilename(
            title="选择Python程序",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )
        if filename:
            path_var.set(filename)
    
    def browse_venv(self, venv_var):
        """浏览虚拟环境目录"""
        directory = filedialog.askdirectory(title="选择虚拟环境目录")
        if directory:
            # 检查是否是有效的虚拟环境
            python_exe = os.path.join(directory, "Scripts", "python.exe")
            if os.path.exists(python_exe):
                venv_var.set(python_exe)
            else:
                messagebox.showwarning("警告", "未找到虚拟环境中的python.exe")
    
    def add_program(self):
        """添加新程序"""
        self.programs.append({
            "name": "新程序",
            "path": "",
            "type": "python",
            "venv": "",
            "args": "",
            "default": False
        })
        self.edit_program(len(self.programs) - 1)
    
    def save_configuration(self):
        """保存配置"""
        if save_config(self.programs):
            messagebox.showinfo("成功", "配置已保存")
    
    def refresh_ui(self):
        """刷新界面"""
        # 销毁当前窗口并重新创建
        self.root.destroy()
        root = tk.Tk()
        app = ProgramLauncher(root)
        root.mainloop()
    
    def launch_programs(self):
        """运行选中的程序"""
        launched = False
        for i, program in enumerate(self.programs):
            if self.vars[i].get():  # 如果被选中
                try:
                    # 构建命令
                    if program["type"] == "python":
                        # 如果有虚拟环境，使用虚拟环境的Python解释器
                        if program.get("venv") and os.path.exists(program["venv"]):
                            python_exe = program["venv"]
                        else:
                            python_exe = sys.executable  # 使用当前Python解释器
                        
                        # 构建命令参数
                        cmd = [python_exe, program["path"]]
                        if program.get("args"):
                            cmd.extend(program["args"].split())
                        
                        # 运行程序
                        subprocess.Popen(cmd)
                    else:
                        # 对于非Python程序，直接运行
                        subprocess.Popen(program["path"], shell=True)
                    
                    launched = True
                except Exception as e:
                    messagebox.showerror("错误", f"无法启动 {program['name']}: {str(e)}")
        
        if launched:
            messagebox.showinfo("成功", "已启动选中的程序")
        else:
            messagebox.showinfo("信息", "未选择任何程序")
        
        self.root.quit()

def main():
    # 创建GUI界面
    root = tk.Tk()
    app = ProgramLauncher(root)
    root.mainloop()

if __name__ == "__main__":
    main()
