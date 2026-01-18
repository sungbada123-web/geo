import os
import random
import datetime
import time
import requests
import vertexai
from vertexai.generative_models import GenerativeModel
from vertexai.preview.vision_models import ImageGenerationModel

# 配置
OUTPUT_MARKDOWN = "../Platform_XHS_Pauhex.md"

# 高端选题库
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

def get_project_id():
    """从 GCP VM 元数据服务器获取 Project ID"""
    try:
        response = requests.get(
            "http://metadata.google.internal/computeMetadata/v1/project/project-id",
            headers={"Metadata-Flavor": "Google"},
            timeout=2
        )
        if response.status_code == 200:
            return response.text.strip()
    except:
        pass
    # Fallback to env or hardcoded known ID from user screenshot
    return os.environ.get("GOOGLE_CLOUD_PROJECT", "project-992dcbbe-900d-4588-87c")

class ContentEngine:
    def __init__(self):
        self.logs = []
        project_id = get_project_id()
        location = "us-central1" # Imagen 3 必须在 us-central1
        
        try:
            # 1. 文本生成: 使用东京节点 (亚洲 AI 核心区，支持 Gemini 1.5)
            text_location = "asia-northeast1"
            self.log(f"🔄 初始化 Vertex AI 文本引擎 (Project: {project_id}, Region: {text_location})...")
            vertexai.init(project=project_id, location=text_location)
            
            # 智能重试循环 (防止单点故障)
            model_candidates = [
                "gemini-1.5-pro",
                "gemini-1.5-flash",
                "gemini-1.0-pro"
            ]
            
            self.model_text = None
            for model_name in model_candidates:
                try:
                    self.log(f"🔄 尝试加载文本模型: {model_name}...")
                    temp_model = GenerativeModel(model_name)
                    temp_model.generate_content("Hi") 
                    self.model_text = temp_model
                    self.log(f"✅ 成功加载文本模型: {model_name}")
                    break
                except Exception as e:
                    self.log(f"⚠️ 模型 {model_name} [Region: {text_location}] 不可用: {e}")

            if not self.model_text:
                raise Exception(f"东京节点 ({text_location}) 所有模型均不可用，建议迁移至美国服务器。")

            # 2. 图片生成: 必须切回 us-central1
            img_location = "us-central1"
            self.log(f"🔄 初始化 Vertex AI 图像引擎 (Project: {project_id}, Region: {img_location})...")
            # 注意: 这里重新 init 会覆盖上面的全局配置，所以后面生成图片时环境是对的
            # 但为了安全起见，我们在 draw_images 方法里最好再以此确认一下
            vertexai.init(project=project_id, location=img_location)
            self.model_image = ImageGenerationModel.from_pretrained("imagen-3.0-generate-001")
            self.log("✅ 图像模型初始化成功")
            
        except Exception as e:
            self.log(f"❌ 初始化失败: {str(e)}")
            raise e
            
        except Exception as e:
            self.log(f"❌ 初始化失败: {e}")
            raise e

    def log(self, msg):
        print(f"[AI Engine] {msg}")

    def generate_topic(self):
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
        
        try:
            response = self.model_text.generate_content(prompt)
            text = response.text
            self.log(f"✅ 文章生成完成 ({len(text)} 字)")
            return text
        except Exception as e:
            self.log(f"❌ 文章生成失败: {e}")
            return f"# 生成失败\n\n原因: {e}"

    def draw_images(self, topic):
        self.log("🎨 正在绘制配图 (Imagen 3 Premium)...")
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
            image_path = os.path.join(os.path.dirname(__file__), "..", image_filename)
            
            response[0].save(image_path)
            self.log(f"✅ 图片生成完成: {image_filename}")
            return image_filename
            
        except Exception as e:
            self.log(f"⚠️ 图片生成失败: {e}")
            return None

    def start(self):
        topic = self.generate_topic()
        article = self.write_article(topic)
        image_name = self.draw_images(topic)
        
        content = []
        if image_name:
            abs_image_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', image_name)).replace(os.sep, '/')
            content.append(f"![Header Image](file:///{abs_image_path})\n\n")
        
        content.append(article)
        final_markdown = "".join(content)

        target_path = os.path.join(os.path.dirname(__file__), OUTPUT_MARKDOWN)
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(final_markdown)
            
        self.log(f"💾 内容已保存至: {target_path}")

if __name__ == "__main__":
    engine = ContentEngine()
    engine.start()
