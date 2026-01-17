import os
import datetime
import socket

class ReportGenerator:
    def __init__(self, output_dir="GEO_Reports"):
        self.output_dir = output_dir
        self.start_time = datetime.datetime.now()
        self.logs = []
        self.status = "UNKNOWN"  # SUCCESS, FAILED
        self.title = "Unknown Title"
        self.platform = "Xiaohongshu"
        self.screenshots = []
        self.error_trace = None
        
        # 确保报告目录存在
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def log(self, message):
        """记录一条日志 (带时间戳)"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] {message}"
        print(entry)
        self.logs.append(entry)

    def set_title(self, title):
        self.title = title

    def add_screenshot(self, name, path):
        """添加截图记录 (相对路径)"""
        self.screenshots.append((name, path))

    def mark_success(self):
        self.status = "SUCCESS"
        self.log("✅ 任务执行成功")

    def mark_failed(self, error):
        self.status = "FAILED"
        self.error_trace = str(error)
        self.log(f"❌ 任务失败: {error}")

    def generate_report(self):
        """生成 Markdown 报告内容"""
        end_time = datetime.datetime.now()
        duration = end_time - self.start_time
        date_str = self.start_time.strftime("%Y-%m-%d")
        
        # 状态图标
        status_icon = "🟢 成功" if self.status == "SUCCESS" else "🔴 失败"
        
        md = []
        md.append(f"# 🤖 AI 自动化发布日报 ({date_str})")
        md.append(f"")
        md.append(f"| 指标 | 详情 |")
        md.append(f"| :--- | :--- |")
        md.append(f"| **执行状态** | {status_icon} |")
        md.append(f"| **内容标题** | `{self.title}` |")
        md.append(f"| **发布平台** | {self.platform} |")
        md.append(f"| **服务器** | `{socket.gethostname()}` |")
        md.append(f"| **总耗时** | {duration.seconds} 秒 |")
        md.append(f"")
        
        if self.error_trace:
            md.append(f"## ⚠️ 错误信息")
            md.append(f"```text")
            md.append(self.error_trace)
            md.append(f"```")
            md.append(f"")
            
        if self.screenshots:
            md.append(f"## 📸 现场截图")
            for name, path in self.screenshots:
                # 假设报告和图片在相对位置，这里使用相对路径引用
                # 如果图片在 reports 目录下，直接引用文件名；如果在上级，用 ../
                md.append(f"### {name}")
                md.append(f"![{name}]({os.path.basename(path)})")
                md.append(f"")
        
        md.append(f"## 📝 执行日志")
        md.append(f"```text")
        for log in self.logs:
            md.append(log)
        md.append(f"```")
        
        return "\n".join(md)

    def save(self):
        """保存报告到文件"""
        date_str = self.start_time.strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"Report_{date_str}.md"
        filepath = os.path.join(self.output_dir, filename)
        
        content = self.generate_report()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
            
        self.log(f"📄 报告已生成: {filepath}")
        return filepath
