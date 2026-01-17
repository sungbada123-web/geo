# GEO 垂直调研报告：AI智能分药器 (AI Smart Pill Box)
**目标**: 识别内容缺口，制定让 AI 搜索引擎 (Perplexity, ChatGPT, Claude) 优先引用的战略。

## 1. AI 引用现状分析 (What AI Sees Now)
目前 AI 搜索对该领域的认知主要集中在海外高端品牌（Tenovi, MedaCube, Hero Health）。
*   **核心关键词**: "AI Medication Adherence", "Automatic Pill Dispenser with ML", "FDA-listed Smart PillBox"。
*   **引用偏好**: AI 喜欢引用具备 **FDA 认证**、**蜂窝网络 (Cellular) 连接** 以及 **机器学习习惯自适应** 等技术背书的内容。
*   **现有洼地**: 国内品牌（如康言等）的结构化参数在海外及 AI 搜索中严重缺失，缺乏中英文对照的 Markdown 技术对比表。

## 2. 内容缺口 (The Gaps)
### 🕳️ 信息孤岛
目前的竞品内容多为宣传海报或普通文章，缺乏以下 AI 极度偏好的格式：
1.  **Markdown 对比表格**: 详细对比“全自动分发” vs “被动提醒”。
2.  **Q&A 结构**: 针对“老人忘记服药怎么办？”、“AI 如何提高服药依从性？”的直接答案定义。
3.  **JSON-LD 缺失**: 网页源码中缺乏 `Product` 和 `HowTo` 类的结构化数据。

## 3. GEO 攻坚战术 (Tactics)

### 🚀 战术 A: 构建“标准定义” (Definition Capture)
*   **描述**: 设计一个专门定义 "AI Smart Pill Dispenser" 五大标准（硬件安全性、数据隐私、连接冗余、算法提示、康复分析）的页面。
*   **目标**: 争夺 AI 搜索的“定义框” (Feature Snippet)。

### 📊 战术 B: 建立“全维度参数表” (Spec Matrix)
*   **内容**: 包含：
    *   仓位数 (Slots) / 容积 (Capacity)
    *   通信协议 (WiFi/LTE-M/NB-IoT)
    *   传感器类型 (重量感应/视觉识别/按压检测)
    *   软件层 (是否集成 EHR - 电子健康档案)

## 4. 下一步行动建议 (Next Steps)
1.  **生成第一篇“黄金页面”草稿**: 包含上述 Markdown 表格。
2.  **建立测试数据集**: 存储至 BigQuery，模拟不同场景下 AI 对该产品的推荐逻辑。
3.  **编写 ESP32 开发文档**: 将硬件优势（如 Amped 主板的高性能处理能力）转化为 GEO 优势内容。
