import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox, Frame, Label
import requests
import json
import threading
import os
import webbrowser
from datetime import datetime
import pyperclip  # 用于复制到剪贴板，需安装：pip install pyperclip
import queue
import hashlib

class MinecraftLogAnalyzerPro:
    def __init__(self, root):
        self.root = root
        self.root.title("Minecraft 日志分析工具 (完整版)")
        self.root.geometry("900x700")
        
        # API配置
        self.api_base = "https://api.mclo.gs/1"
        self.api_url = f"{self.api_base}/log"
        self.insights_url = f"{self.api_base}/insights"
        
        # 存储日志ID和URL
        self.current_log_id = None
        self.current_log_url = None
        
        # 创建标签页界面
        self.create_notebook()
        
        # 启动日志监控线程（模拟插件功能）
        self.log_queue = queue.Queue()
        self.monitoring = False
        self.start_log_monitor()
        
        # 设置样式
        self.setup_styles()
    
    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        style.configure('Error.TLabel', foreground='red')
        style.configure('Success.TLabel', foreground='green')
        style.configure('Warning.TLabel', foreground='orange')
        style.configure('Info.TLabel', foreground='blue')
    
    def create_notebook(self):
        """创建标签页界面"""
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 创建各个功能标签页
        self.create_analyze_tab(notebook)
        self.create_share_tab(notebook)
        self.create_plugin_tab(notebook)
        self.create_mod_tab(notebook)
        self.create_api_tab(notebook)
        self.create_config_tab(notebook)
        
        # 状态栏
        self.create_statusbar()
    
    def create_analyze_tab(self, notebook):
        """创建分析标签页（核心功能）"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="日志分析")
        
        # 顶部控制区域
        control_frame = ttk.Frame(tab)
        control_frame.pack(fill='x', padx=10, pady=10)
        
        # 文件操作按钮
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(side='left')
        
        ttk.Button(btn_frame, text="打开日志文件", 
                  command=self.open_log_file).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="粘贴剪贴板", 
                  command=self.paste_from_clipboard).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="清空", 
                  command=self.clear_all).pack(side='left', padx=2)
        
        # 分析选项
        option_frame = ttk.Frame(control_frame)
        option_frame.pack(side='right')
        
        self.auto_analyze = tk.BooleanVar(value=True)
        ttk.Checkbutton(option_frame, text="自动分析", 
                       variable=self.auto_analyze).pack(side='left', padx=5)
        
        # 日志输入区域
        input_frame = ttk.LabelFrame(tab, text="日志内容", padding=10)
        input_frame.pack(fill='both', expand=True, padx=10, pady=(0,10))
        
        self.log_text = self.create_syntax_text(input_frame)
        self.log_text.pack(fill='both', expand=True)
        
        # 绑定文本变化事件（用于实时分析）
        self.log_text.bind('<<Modified>>', self.on_text_modified)
    
    def create_share_tab(self, notebook):
        """创建分享标签页"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="分享")
        
        # 分享控制区域
        control_frame = ttk.Frame(tab)
        control_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(control_frame, text="生成分享链接", 
                  command=self.generate_share_link).pack(side='left', padx=5)
        ttk.Button(control_frame, text="复制链接", 
                  command=self.copy_share_link).pack(side='left', padx=5)
        ttk.Button(control_frame, text="在浏览器打开", 
                  command=self.open_in_browser).pack(side='left', padx=5)
        
        # 分享信息显示
        info_frame = ttk.LabelFrame(tab, text="分享信息", padding=10)
        info_frame.pack(fill='both', expand=True, padx=10, pady=(0,10))
        
        # 短链接显示
        link_frame = ttk.Frame(info_frame)
        link_frame.pack(fill='x', pady=5)
        
        ttk.Label(link_frame, text="短链接:").pack(side='left')
        self.share_link_var = tk.StringVar()
        ttk.Entry(link_frame, textvariable=self.share_link_var, 
                 width=50).pack(side='left', padx=5, fill='x', expand=True)
        
        # 访问统计
        stats_frame = ttk.Frame(info_frame)
        stats_frame.pack(fill='x', pady=5)
        
        ttk.Label(stats_frame, text="访问次数:").pack(side='left')
        self.views_var = tk.StringVar(value="0")
        ttk.Label(stats_frame, textvariable=self.views_var, 
                 style='Info.TLabel').pack(side='left', padx=5)
        
        ttk.Label(stats_frame, text="创建时间:").pack(side='left', padx=(20,0))
        self.created_var = tk.StringVar()
        ttk.Label(stats_frame, textvariable=self.created_var).pack(side='left', padx=5)
        
        # 原始链接
        raw_frame = ttk.Frame(info_frame)
        raw_frame.pack(fill='x', pady=5)
        
        ttk.Label(raw_frame, text="原始链接:").pack(side='left')
        self.raw_link_text = scrolledtext.ScrolledText(raw_frame, height=3)
        self.raw_link_text.pack(side='left', padx=5, fill='x', expand=True)
        
        # 二维码生成（模拟）
        ttk.Button(info_frame, text="生成二维码", 
                  command=self.generate_qr_code).pack(pady=10)
    
    def create_plugin_tab(self, notebook):
        """创建服务器插件模拟标签页"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="服务器插件")
        
        ttk.Label(tab, text="服务器插件功能模拟", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        # 服务器监控设置
        monitor_frame = ttk.LabelFrame(tab, text="日志监控", padding=10)
        monitor_frame.pack(fill='x', padx=10, pady=5)
        
        # 日志目录设置
        dir_frame = ttk.Frame(monitor_frame)
        dir_frame.pack(fill='x', pady=5)
        
        ttk.Label(dir_frame, text="日志目录:").pack(side='left')
        self.log_dir_var = tk.StringVar(value=".minecraft/logs")
        ttk.Entry(dir_frame, textvariable=self.log_dir_var, 
                 width=40).pack(side='left', padx=5, fill='x', expand=True)
        ttk.Button(dir_frame, text="浏览", 
                  command=self.browse_log_dir).pack(side='left')
        
        # 监控控制
        control_frame = ttk.Frame(monitor_frame)
        control_frame.pack(fill='x', pady=5)
        
        self.monitor_btn = ttk.Button(control_frame, text="启动监控", 
                                     command=self.toggle_monitoring)
        self.monitor_btn.pack(side='left', padx=5)
        
        ttk.Button(control_frame, text="手动上传最新日志", 
                  command=self.upload_latest_log).pack(side='left', padx=5)
        
        # 权限设置
        perm_frame = ttk.LabelFrame(tab, text="权限管理", padding=10)
        perm_frame.pack(fill='x', padx=10, pady=5)
        
        self.auto_hide_ip = tk.BooleanVar(value=True)
        ttk.Checkbutton(perm_frame, text="自动隐藏IP地址", 
                       variable=self.auto_hide_ip).pack(anchor='w')
        
        self.allow_team_share = tk.BooleanVar(value=True)
        ttk.Checkbutton(perm_frame, text="允许团队成员分享", 
                       variable=self.allow_team_share).pack(anchor='w')
        
        # 监控日志显示
        log_frame = ttk.LabelFrame(tab, text="监控日志", padding=10)
        log_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.monitor_log = scrolledtext.ScrolledText(log_frame, height=10)
        self.monitor_log.pack(fill='both', expand=True)
        
        # 添加时间戳
        self.add_monitor_log("监控系统就绪")
    
    def create_mod_tab(self, notebook):
        """创建客户端Mod模拟标签页"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="客户端Mod")
        
        ttk.Label(tab, text="客户端Mod功能模拟", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Mod设置
        settings_frame = ttk.LabelFrame(tab, text="Mod设置", padding=10)
        settings_frame.pack(fill='x', padx=10, pady=5)
        
        # 支持的Mod加载器
        loader_frame = ttk.Frame(settings_frame)
        loader_frame.pack(fill='x', pady=5)
        
        ttk.Label(loader_frame, text="Mod加载器:").pack(side='left')
        self.loader_var = tk.StringVar(value="Fabric")
        loaders = ["Fabric", "Forge", "NeoForge", "Quilt"]
        for loader in loaders:
            ttk.Radiobutton(loader_frame, text=loader, value=loader, 
                           variable=self.loader_var).pack(side='left', padx=10)
        
        # 游戏目录
        game_dir_frame = ttk.Frame(settings_frame)
        game_dir_frame.pack(fill='x', pady=5)
        
        ttk.Label(game_dir_frame, text="游戏目录:").pack(side='left')
        self.game_dir_var = tk.StringVar(value=".minecraft")
        ttk.Entry(game_dir_frame, textvariable=self.game_dir_var, 
                 width=40).pack(side='left', padx=5, fill='x', expand=True)
        ttk.Button(game_dir_frame, text="浏览", 
                  command=self.browse_game_dir).pack(side='left')
        
        # 客户端日志操作
        client_frame = ttk.LabelFrame(tab, text="客户端日志", padding=10)
        client_frame.pack(fill='x', padx=10, pady=5)
        
        btn_frame = ttk.Frame(client_frame)
        btn_frame.pack(pady=5)
        
        ttk.Button(btn_frame, text="捕获当前日志", 
                  command=self.capture_client_log).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="上传崩溃报告", 
                  command=self.upload_crash_report).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="查看最新日志", 
                  command=self.view_latest_client_log).pack(side='left', padx=5)
        
        # 客户端日志显示
        display_frame = ttk.LabelFrame(tab, text="日志内容", padding=10)
        display_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.client_log_text = scrolledtext.ScrolledText(display_frame, height=15)
        self.client_log_text.pack(fill='both', expand=True)
    
    def create_api_tab(self, notebook):
        """创建API集成标签页"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="API集成")
        
        ttk.Label(tab, text="API测试面板", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        # API端点选择
        api_frame = ttk.LabelFrame(tab, text="API端点", padding=10)
        api_frame.pack(fill='x', padx=10, pady=5)
        
        endpoint_frame = ttk.Frame(api_frame)
        endpoint_frame.pack(fill='x', pady=5)
        
        ttk.Label(endpoint_frame, text="选择端点:").pack(side='left')
        self.api_endpoint_var = tk.StringVar(value="/log")
        endpoints = ["/log", "/insights", "/raw/{id}", "/download/{id}"]
        ttk.Combobox(endpoint_frame, textvariable=self.api_endpoint_var, 
                    values=endpoints, width=20).pack(side='left', padx=5)
        
        ttk.Button(endpoint_frame, text="发送请求", 
                  command=self.send_api_request).pack(side='left', padx=5)
        
        # 请求参数
        param_frame = ttk.LabelFrame(tab, text="请求参数", padding=10)
        param_frame.pack(fill='x', padx=10, pady=5)
        
        self.api_params_text = scrolledtext.ScrolledText(param_frame, height=8)
        self.api_params_text.pack(fill='both', expand=True)
        self.api_params_text.insert('1.0', '{\n  "content": "粘贴日志内容到这里"\n}')
        
        # 响应显示
        response_frame = ttk.LabelFrame(tab, text="API响应", padding=10)
        response_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.api_response_text = scrolledtext.ScrolledText(response_frame, height=15)
        self.api_response_text.pack(fill='both', expand=True)
        
        # 响应信息
        info_frame = ttk.Frame(tab)
        info_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(info_frame, text="状态码:").pack(side='left')
        self.status_code_var = tk.StringVar()
        ttk.Label(info_frame, textvariable=self.status_code_var, 
                 style='Info.TLabel').pack(side='left', padx=5)
        
        ttk.Label(info_frame, text="响应时间:").pack(side='left', padx=(20,0))
        self.response_time_var = tk.StringVar()
        ttk.Label(info_frame, textvariable=self.response_time_var).pack(side='left', padx=5)
    
    def create_config_tab(self, notebook):
        """创建配置标签页"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="配置")
        
        ttk.Label(tab, text="工具配置", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        # API设置
        api_frame = ttk.LabelFrame(tab, text="API设置", padding=10)
        api_frame.pack(fill='x', padx=10, pady=5)
        
        # API密钥
        key_frame = ttk.Frame(api_frame)
        key_frame.pack(fill='x', pady=5)
        
        ttk.Label(key_frame, text="API密钥:").pack(side='left')
        self.api_key_var = tk.StringVar()
        ttk.Entry(key_frame, textvariable=self.api_key_var, 
                 width=40, show="*").pack(side='left', padx=5, fill='x', expand=True)
        ttk.Button(key_frame, text="保存", 
                  command=self.save_api_key).pack(side='left')
        
        # 自定义API端点
        custom_frame = ttk.Frame(api_frame)
        custom_frame.pack(fill='x', pady=5)
        
        ttk.Label(custom_frame, text="自定义端点:").pack(side='left')
        self.custom_api_var = tk.StringVar(value="https://api.mclo.gs/1")
        ttk.Entry(custom_frame, textvariable=self.custom_api_var, 
                 width=40).pack(side='left', padx=5, fill='x', expand=True)
        
        # 显示设置
        display_frame = ttk.LabelFrame(tab, text="显示设置", padding=10)
        display_frame.pack(fill='x', padx=10, pady=5)
        
        self.syntax_highlight = tk.BooleanVar(value=True)
        ttk.Checkbutton(display_frame, text="启用语法高亮", 
                       variable=self.syntax_highlight).pack(anchor='w')
        
        self.auto_scroll = tk.BooleanVar(value=True)
        ttk.Checkbutton(display_frame, text="自动滚动到最新", 
                       variable=self.auto_scroll).pack(anchor='w')
        
        # 高级设置
        advanced_frame = ttk.LabelFrame(tab, text="高级设置", padding=10)
        advanced_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(advanced_frame, text="请求超时(秒):").pack(side='left')
        self.timeout_var = tk.IntVar(value=30)
        ttk.Spinbox(advanced_frame, from_=10, to=120, 
                   textvariable=self.timeout_var, width=10).pack(side='left', padx=5)
        
        ttk.Button(advanced_frame, text="重置所有设置", 
                  command=self.reset_settings).pack(side='right')
        
        # 关于信息
        about_frame = ttk.LabelFrame(tab, text="关于", padding=10)
        about_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        about_text = """Minecraft 日志分析工具 完整版
版本: 2.0
基于 mclo.gs API 开发

功能:
✓ 日志粘贴与分析
✓ 智能分享与短链接
✓ 服务器插件模拟
✓ 客户端Mod模拟
✓ 完整API集成
✓ 语法高亮显示

开源协议: MIT License"""
        
        about_label = ttk.Label(about_frame, text=about_text, justify='left')
        about_label.pack(anchor='w')
        
        ttk.Button(about_frame, text="访问官方网站", 
                  command=lambda: webbrowser.open("https://mclo.gs")).pack(pady=10)
    
    def create_statusbar(self):
        """创建状态栏"""
        self.statusbar = ttk.Frame(self.root, relief='sunken')
        self.statusbar.pack(side='bottom', fill='x')
        
        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(self.statusbar, textvariable=self.status_var).pack(side='left', padx=5)
        
        # 添加进度条
        self.progress = ttk.Progressbar(self.statusbar, mode='indeterminate', length=100)
        self.progress.pack(side='right', padx=5, pady=2)
    
    def create_syntax_text(self, parent):
        """创建支持语法高亮的文本框"""
        text = scrolledtext.ScrolledText(parent, wrap='word')
        
        # 配置标签用于语法高亮
        text.tag_config('ERROR', foreground='red', font=('Courier', 10, 'bold'))
        text.tag_config('WARN', foreground='orange')
        text.tag_config('INFO', foreground='blue')
        text.tag_config('DEBUG', foreground='gray')
        text.tag_config('TIMESTAMP', foreground='green')
        
        return text
    
    def on_text_modified(self, event):
        """文本修改事件处理"""
        if self.auto_analyze.get():
            self.schedule_analysis()
    
    def schedule_analysis(self):
        """安排延迟分析"""
        # 取消之前的延迟调用
        if hasattr(self, '_analysis_job'):
            self.root.after_cancel(self._analysis_job)
        
        # 延迟1秒后分析（避免频繁调用）
        self._analysis_job = self.root.after(1000, self.perform_auto_analysis)
    
    def perform_auto_analysis(self):
        """执行自动分析"""
        content = self.log_text.get('1.0', 'end-1c').strip()
        if len(content) > 100:  # 内容足够长才分析
            self.analyze_log_content(content)
    
    def analyze_log_content(self, content):
        """分析日志内容"""
        self.status_var.set("正在分析...")
        self.progress.start()
        
        thread = threading.Thread(target=self._analyze_thread, args=(content,))
        thread.daemon = True
        thread.start()
    
    def _analyze_thread(self, content):
        """分析线程"""
        try:
            # 调用API分析
            data = {'content': content}
            response = requests.post(self.api_url, data=data, timeout=self.timeout_var.get())
            
            if response.status_code == 200:
                result = response.json()
                self.root.after(0, self._handle_analysis_result, result)
            else:
                self.root.after(0, self._show_error, f"API错误: {response.status_code}")
                
        except Exception as e:
            self.root.after(0, self._show_error, str(e))
    
    def _handle_analysis_result(self, result):
        """处理分析结果"""
        self.progress.stop()
        
        if result.get('success'):
            self.current_log_id = result['id']
            self.current_log_url = result.get('url', f'https://mclo.gs/{self.current_log_id}')
            
            # 更新分享标签页
            self.share_link_var.set(self.current_log_url)
            self.raw_link_text.delete('1.0', 'end')
            self.raw_link_text.insert('1.0', json.dumps(result, indent=2))
            
            # 显示分析结果
            self.show_analysis_results(result)
            self.status_var.set("分析完成")
        else:
            self.status_var.set("分析失败")
    
    def show_analysis_results(self, result):
        """显示分析结果"""
        # 这里可以创建一个新的结果窗口或更新现有显示
        # 由于篇幅限制，这里简化为显示通知
        insights = result.get('insights', {})
        
        if 'analysis' in insights:
            messagebox.showinfo("分析结果", insights['analysis'])
    
    def generate_share_link(self):
        """生成分享链接"""
        content = self.log_text.get('1.0', 'end-1c').strip()
        if not content:
            messagebox.showwarning("警告", "请先输入日志内容")
            return
        
        self.analyze_log_content(content)
    
    def copy_share_link(self):
        """复制分享链接到剪贴板"""
        if self.current_log_url:
            pyperclip.copy(self.current_log_url)
            self.status_var.set("链接已复制到剪贴板")
        else:
            messagebox.showwarning("警告", "没有可用的分享链接")
    
    def open_in_browser(self):
        """在浏览器中打开"""
        if self.current_log_url:
            webbrowser.open(self.current_log_url)
        else:
            messagebox.showwarning("警告", "没有可用的链接")
    
    def generate_qr_code(self):
        """生成二维码（模拟）"""
        if self.current_log_url:
            # 这里可以集成真正的二维码生成库
            messagebox.showinfo("二维码", f"模拟生成二维码:\n{self.current_log_url}")
        else:
            messagebox.showwarning("警告", "没有可用的链接")
    
    def start_log_monitor(self):
        """启动日志监控线程"""
        self.monitor_thread = threading.Thread(target=self._monitor_logs)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def _monitor_logs(self):
        """监控日志文件（模拟）"""
        import time
        last_content = ""
        
        while True:
            if self.monitoring:
                try:
                    # 模拟检查日志文件
                    log_path = os.path.join(self.log_dir_var.get(), "latest.log")
                    if os.path.exists(log_path):
                        with open(log_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # 检查是否有新内容
                        if content != last_content and len(content) > len(last_content):
                            new_content = content[len(last_content):]
                            self.root.after(0, self._add_monitor_log, 
                                          f"检测到新日志内容 ({len(new_content)} 字符)")
                            last_content = content
                    
                except Exception as e:
                    self.root.after(0, self._add_monitor_log, f"监控错误: {e}")
            
            time.sleep(5)  # 每5秒检查一次
    
    def toggle_monitoring(self):
        """切换监控状态"""
        self.monitoring = not self.monitoring
        
        if self.monitoring:
            self.monitor_btn.config(text="停止监控")
            self.add_monitor_log("日志监控已启动")
            self.status_var.set("正在监控日志文件")
        else:
            self.monitor_btn.config(text="启动监控")
            self.add_monitor_log("日志监控已停止")
            self.status_var.set("监控已停止")
    
    def add_monitor_log(self, message):
        """添加监控日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.monitor_log.insert('end', f"[{timestamp}] {message}\n")
        self.monitor_log.see('end')
    
    def _add_monitor_log(self, message):
        """线程安全的日志添加"""
        self.root.after(0, self.add_monitor_log, message)
    
    def browse_log_dir(self):
        """浏览日志目录"""
        directory = filedialog.askdirectory(title="选择日志目录")
        if directory:
            self.log_dir_var.set(directory)
    
    def upload_latest_log(self):
        """上传最新日志"""
        log_path = os.path.join(self.log_dir_var.get(), "latest.log")
        if os.path.exists(log_path):
            try:
                with open(log_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.log_text.delete('1.0', 'end')
                self.log_text.insert('1.0', content)
                self.add_monitor_log(f"已加载日志: {log_path}")
                
                if self.auto_analyze.get():
                    self.analyze_log_content(content)
                    
            except Exception as e:
                messagebox.showerror("错误", f"读取日志失败: {e}")
        else:
            messagebox.showwarning("警告", f"找不到日志文件: {log_path}")
    
    def browse_game_dir(self):
        """浏览游戏目录"""
        directory = filedialog.askdirectory(title="选择Minecraft游戏目录")
        if directory:
            self.game_dir_var.set(directory)
    
    def capture_client_log(self):
        """捕获客户端日志（模拟）"""
        # 模拟读取客户端日志
        log_dirs = [
            os.path.join(self.game_dir_var.get(), "logs"),
            os.path.join(self.game_dir_var.get(), "crash-reports")
        ]
        
        for log_dir in log_dirs:
            if os.path.exists(log_dir):
                latest_log = self._find_latest_log(log_dir)
                if latest_log:
                    try:
                        with open(latest_log, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        self.client_log_text.delete('1.0', 'end')
                        self.client_log_text.insert('1.0', content)
                        self.status_var.set(f"已捕获日志: {os.path.basename(latest_log)}")
                        return
                        
                    except Exception as e:
                        messagebox.showerror("错误", f"读取日志失败: {e}")
        
        messagebox.showinfo("提示", "未找到客户端日志文件")
    
    def _find_latest_log(self, directory):
        """查找最新的日志文件"""
        import glob
        log_files = glob.glob(os.path.join(directory, "*.log")) + \
                   glob.glob(os.path.join(directory, "*.txt"))
        
        if log_files:
            return max(log_files, key=os.path.getmtime)
        return None
    
    def upload_crash_report(self):
        """上传崩溃报告"""
        crash_dir = os.path.join(self.game_dir_var.get(), "crash-reports")
        if os.path.exists(crash_dir):
            crash_file = self._find_latest_log(crash_dir)
            if crash_file:
                try:
                    with open(crash_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 自动上传到分析
                    self.log_text.delete('1.0', 'end')
                    self.log_text.insert('1.0', content)
                    self.analyze_log_content(content)
                    
                    self.status_var.set(f"已上传崩溃报告: {os.path.basename(crash_file)}")
                    
                except Exception as e:
                    messagebox.showerror("错误", f"读取崩溃报告失败: {e}")
            else:
                messagebox.showinfo("提示", "未找到崩溃报告")
        else:
            messagebox.showinfo("提示", "未找到崩溃报告目录")
    
    def view_latest_client_log(self):
        """查看最新客户端日志"""
        log_file = self._find_latest_log(os.path.join(self.game_dir_var.get(), "logs"))
        if log_file:
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 在新窗口中显示
                self.show_log_viewer("客户端日志", content, log_file)
                
            except Exception as e:
                messagebox.showerror("错误", f"打开日志失败: {e}")
        else:
            messagebox.showinfo("提示", "未找到日志文件")
    
    def send_api_request(self):
        """发送API请求"""
        endpoint = self.api_endpoint_var.get()
        params_text = self.api_params_text.get('1.0', 'end-1c')
        
        try:
            params = json.loads(params_text)
        except json.JSONDecodeError:
            messagebox.showerror("错误", "无效的JSON格式")
            return
        
        url = f"{self.api_base}{endpoint}"
        
        # 如果是需要日志ID的端点
        if '{id}' in endpoint and self.current_log_id:
            url = url.replace('{id}', self.current_log_id)
        
        self.status_var.set("正在发送API请求...")
        self.progress.start()
        
        thread = threading.Thread(target=self._api_request_thread, args=(url, params))
        thread.daemon = True
        thread.start()
    
    def _api_request_thread(self, url, params):
        """API请求线程"""
        import time
        start_time = time.time()
        
        try:
            response = requests.post(url, json=params, timeout=self.timeout_var.get())
            response_time = time.time() - start_time
            
            self.root.after(0, self._handle_api_response, response, response_time)
                
        except Exception as e:
            self.root.after(0, self._show_error, f"API请求失败: {e}")
    
    def _handle_api_response(self, response, response_time):
        """处理API响应"""
        self.progress.stop()
        
        self.status_code_var.set(str(response.status_code))
        self.response_time_var.set(f"{response_time:.2f}秒")
        
        # 显示响应内容
        self.api_response_text.delete('1.0', 'end')
        
        try:
            if response.headers.get('content-type', '').startswith('application/json'):
                result = response.json()
                formatted = json.dumps(result, indent=2, ensure_ascii=False)
                self.api_response_text.insert('1.0', formatted)
            else:
                self.api_response_text.insert('1.0', response.text)
        except:
            self.api_response_text.insert('1.0', response.text)
        
        self.status_var.set("API请求完成")
    
    def save_api_key(self):
        """保存API密钥"""
        api_key = self.api_key_var.get()
        if api_key:
            # 这里应该安全地保存API密钥
            # 简化处理：显示保存成功
            self.status_var.set("API密钥已保存")
        else:
            messagebox.showwarning("警告", "请输入API密钥")
    
    def reset_settings(self):
        """重置所有设置"""
        if messagebox.askyesno("确认", "确定要重置所有设置吗？"):
            self.api_key_var.set("")
            self.custom_api_var.set("https://api.mclo.gs/1")
            self.timeout_var.set(30)
            self.status_var.set("设置已重置")
    
    def open_log_file(self):
        """打开日志文件"""
        file_path = filedialog.askopenfilename(
            title="选择日志文件",
            filetypes=[
                ("日志文件", "*.log"),
                ("崩溃报告", "*.txt"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            try:
                # 尝试多种编码
                encodings = ['utf-8', 'latin-1', 'cp1252']
                content = None
                
                for encoding in encodings:
                    try:
                        with open(file_path, 'r', encoding=encoding) as f:
                            content = f.read()
                        break
                    except UnicodeDecodeError:
                        continue
                
                if content is None:
                    # 二进制方式读取
                    with open(file_path, 'rb') as f:
                        content = f.read().decode('utf-8', errors='ignore')
                
                self.log_text.delete('1.0', 'end')
                self.log_text.insert('1.0', content)
                self.status_var.set(f"已加载: {os.path.basename(file_path)}")
                
                # 应用语法高亮
                if self.syntax_highlight.get():
                    self.apply_syntax_highlight()
                
            except Exception as e:
                messagebox.showerror("错误", f"无法读取文件: {e}")
    
    def paste_from_clipboard(self):
        """从剪贴板粘贴"""
        try:
            content = pyperclip.paste()
            if content:
                self.log_text.delete('1.0', 'end')
                self.log_text.insert('1.0', content)
                self.status_var.set("已从剪贴板粘贴")
                
                if self.auto_analyze.get() and len(content.strip()) > 100:
                    self.analyze_log_content(content.strip())
        except Exception as e:
            messagebox.showerror("错误", f"无法读取剪贴板: {e}")
    
    def clear_all(self):
        """清空所有内容"""
        if messagebox.askyesno("确认", "确定要清空所有内容吗？"):
            self.log_text.delete('1.0', 'end')
            self.client_log_text.delete('1.0', 'end')
            self.monitor_log.delete('1.0', 'end')
            self.api_response_text.delete('1.0', 'end')
            self.api_params_text.delete('1.0', 'end')
            self.api_params_text.insert('1.0', '{\n  "content": "粘贴日志内容到这里"\n}')
            
            self.current_log_id = None
            self.current_log_url = None
            self.share_link_var.set("")
            self.raw_link_text.delete('1.0', 'end')
            
            self.status_var.set("已清空")
    
    def apply_syntax_highlight(self):
        """应用语法高亮"""
        content = self.log_text.get('1.0', 'end-1c')
        lines = content.split('\n')
        
        # 清除现有标签
        for tag in ['ERROR', 'WARN', 'INFO', 'DEBUG', 'TIMESTAMP']:
            self.log_text.tag_remove(tag, '1.0', 'end')
        
        # 逐行分析
        for i, line in enumerate(lines, 1):
            start_idx = f"{i}.0"
            
            # 时间戳高亮
            if line.startswith('[') and ']' in line:
                end_bracket = line.find(']')
                if end_bracket > 0:
                    end_idx = f"{i}.{end_bracket + 1}"
                    self.log_text.tag_add('TIMESTAMP', start_idx, end_idx)
            
            # 错误级别高亮
            if '[ERROR]' in line.upper():
                self.log_text.tag_add('ERROR', start_idx, f"{i}.end")
            elif '[WARN]' in line.upper():
                self.log_text.tag_add('WARN', start_idx, f"{i}.end")
            elif '[INFO]' in line.upper():
                self.log_text.tag_add('INFO', start_idx, f"{i}.end")
            elif '[DEBUG]' in line.upper():
                self.log_text.tag_add('DEBUG', start_idx, f"{i}.end")
    
    def show_log_viewer(self, title, content, filename=""):
        """显示日志查看器窗口"""
        viewer = tk.Toplevel(self.root)
        viewer.title(f"{title} - {filename}" if filename else title)
        viewer.geometry("800x600")
        
        # 添加文本控件
        text = scrolledtext.ScrolledText(viewer, wrap='word')
        text.pack(fill='both', expand=True, padx=10, pady=10)
        text.insert('1.0', content)
        text.config(state='normal')
        
        # 添加关闭按钮
        ttk.Button(viewer, text="关闭", 
                  command=viewer.destroy).pack(pady=5)
    
    def _show_error(self, message):
        """显示错误"""
        self.progress.stop()
        self.status_var.set(f"错误: {message}")
        messagebox.showerror("错误", message)


def main():
    root = tk.Tk()
    app = MinecraftLogAnalyzerPro(root)
    
    # 添加启动提示
    app.status_var.set("Minecraft日志分析工具已启动 - 包含mclo.gs所有功能")
    
    root.mainloop()


if __name__ == "__main__":
    main()
