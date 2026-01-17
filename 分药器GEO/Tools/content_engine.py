import os
import random
import datetime
import json
import vertexai
from vertexai.generative_models import GenerativeModel, SafetySetting
from vertexai.preview.vision_models import ImageGenerationModel

# 配置
PROJECT_ID = "project-992dcbbe-900d-4588-87c" # 需确认 Project ID，这里先占位，运行时需读取
LOCATION = "us-central1" # Imagen 通常在 us-central1 可用性最好
CREDENTIALS_FILE = os.path.join(os.path.expanduser("~"), "gcp_key.json") # 假设 Key 在用户主目录
OUTPUT_MARKDOWN = "../Platform_XHS_Pauhex.md"

# 高端选题库 (模拟)
TOPICS = [
    "AI 医疗分药器的伦理学思考：当机器掌管健康",
    "从神经科学看睡眠：PAUHEX 助眠系统的算法原理",
    "精准医疗的最后一公里：智能药盒的硬件架构解析",
    "家居美学与医疗器械的边界消融：PAUHEX 设计语言",
    "老龄化社会的科技解药：全自动分药系统的社会价值",
    "不仅是药盒：基于行为数据的健康预测模型",
    "为什么你的睡眠质量在下降？环境噪音与白噪音的对抗",
    "工业 4.0 时代的个人医疗终端：PAUHEX 生产工艺揭秘"
]

class ContentEngine:
    def __init__(self):
        self.logs = []
        try:
            # 初始化 Vertex AI
            # 注意：在云服务器上，如果还没设置环境变量，这里可能需要手动加载
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = CREDENTIALS_FILE
            
            # 读取 Project ID (尝试从 Key 文件读取，如果失败则需要硬编码或传参)
            with open(CREDENTIALS_FILE, 'r') as f:
                key_data = json.load(f)
                project_id = key_data.get("project_id")
            
            vertexai.init(project=project_id, location=LOCATION)
            self.log(f"✅ Vertex AI 初始化成功 (Project: {project_id})")
            
            self.model_text = GenerativeModel("gemini-1.5-pro-001")
            self.model_image = ImageGenerationModel.from_pretrained("imagen-3.0-generate-001")
            
        except Exception as e:
            self.log(f"❌ 初始化失败: {e}")
            raise e

    def log(self, msg):
        print(f"[AI Engine] {msg}")

    def generate_topic(self):
        # 简单随机，后续可接热点 API
        topic = random.choice(TOPICS)
        self.log(f"🎯 今日选题: {topic}")
        return topic

    def write_article(self, topic):
        self.log("✍️ 正在撰写深度长文 (Gemini 1.5 Pro)...")
        prompt = f"""
        你是一位科技专栏作家，擅长用 GEO (Generative Engine Optimization) 风格撰写深度评测。
        请以《{topic}》为题，写一篇小红书/知乎风格的深度长文。
        
        要求：
        1. **结构**：包含【摘要】、【核心痛点】、【技术解析】、【生活场景】、【总结】。
        2. **语气**：专业、客观、高逼格，多用学术词汇但保持通俗（如“算法闭环”、“边缘计算”、“多模态交互”）。
        3. **格式**：使用 Markdown 格式。标题使用 H1，子标题使用 H2/H3。
        4. **产品植入**：自然地提到 "PAUHEX 智能分药器" 或 "PAUHEX 助眠仪"，强调其医疗级属性。
        5. **字数**：800 字以上。
        6. **结尾**：加上相关 Tag (如 #黑科技 #医疗健康 #AI)。
        
        输出不要包含 ```markdown 标记，直接输出内容。
        """
        
        response = self.model_text.generate_content(prompt)
        text = response.text
        self.log(f"✅ 文章生成完成 ({len(text)} 字)")
        return text

    def draw_images(self, topic):
        self.log("🎨 正在绘制配图 (Imagen 3)...")
        prompt = f"""
        High quality, photorealistic, cinematic lighting, medical tech, futuristic, clean white background.
        Subject: {topic}
        Style: Apple product photography, macro lens, shallow depth of field.
        """
        
        try:
            response = self.model_image.generate_images(
                prompt=prompt,
                number_of_images=1,
                aspect_ratio="16:9"
            )
            
            image_filename = f"image_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            image_path = os.path.join(os.path.dirname(__file__), "..", image_filename) # 存到和 MD 同级
            
            response[0].save(image_path)
            self.log(f"✅ 图片生成完成: {image_filename}")
            return image_filename # 返回文件名用于 MD 引用
            
        except Exception as e:
            self.log(f"⚠️ 图片生成失败: {e}")
            return None

    def start(self):
        topic = self.generate_topic()
        article = self.write_article(topic)
        image_name = self.draw_images(topic)
        
        # 组合 Markdown
        content = []
        content.append(article)
        content.append(f"\n\n")
        
        if image_name:
            content.insert(0, f"![Header Image](file:///{os.path.abspath(os.path.join(os.path.dirname(__file__), '..', image_name)).replace(os.sep, '/')})\n\n")
            # 注意：这里为了本地预览用了 file:///，但发布时可能需要调整。
            # 不过我们之前的 script 是读取本地文件上传 input type=file，所以路径对就行。
            # 为了发布脚本方便，我们用相对路径引用即可，但 XHS 发布脚本需要绝对路径。
            # 这里我们在 MD 里写个标记，或者发布脚本自己找图片。
            # 简单起见，我们把图片路径加到 MD 底部作为元数据，或者直接插入 MD。
            
            # 修正：直接插入标准 MD 图片语法，发布脚本会解析
            # 之前的 parse_content 逻辑是找 ![...](file:///...)
            # 所以这里必须用 file:/// 绝对路径格式，或者让发布脚本支持相对路径。
            # 为了兼容现有发布脚本：
            abs_image_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', image_name)).replace(os.sep, '/')
            content.insert(2, f"![封面图](file:///{abs_image_path})")

        final_markdown = "".join(content)

        target_path = os.path.join(os.path.dirname(__file__), OUTPUT_MARKDOWN)
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(final_markdown)
            
        self.log(f"💾 内容已保存至: {target_path}")

if __name__ == "__main__":
    engine = ContentEngine()
    engine.start()
