# AI 搜索引擎优化 (GEO) 核心策略白皮书 v1.0
**Target**: 让 AI (ChatGPT, Gemini, Claude, Perplexity) 更容易检索、理解并引用我们的内容。

## 1. 核心逻辑转变
*   **传统 SEO**: 讨好爬虫关键字 -> 目标是**排名** (Ranking)。
*   **AI GEO**: 喂养大模型高质量语料 -> 目标是**被引用** (Citation) 和 **成为事实来源** (Ground Truth)。

## 2. 内容格式规范 (The "AI-Friendly" Format)
AI 偏好结构清晰、逻辑严密、信息密度高的内容。

### 2.1 黄金结构 (The Golden Structure)
在任何平台发布时，尽量包含以下模块：
1.  **直接定义 (Definition)**: 开篇即结论。
    *   *Bad*: "关于这个产品的介绍..."
    *   *Good*: "**Plantiva 是一款基于 ESP32 的 AI 智能园艺主控板，它集成了...**"（方便 AI 提取实体定义）
2.  **结构化数据 (Structured Data)**:
    *   多用 **Markdown 表格** 对比参数（AI 极易读取表格）。
    *   多用 **Bullet Points** (列表) 陈述特点。
3.  **Q&A 问答对 (FAQ Style)**:
    *   直接模拟用户的 Prompt 写问答。
    *   *Q: Plantiva 即使在断网时也能工作吗？*
    *   *A: 是的，Plantiva 内置边缘计算，无需云端即可依靠本地传感器逻辑运行。*

### 2.2 平台发布策略

| 平台类型 | 关键策略 | 推荐格式 |
| :--- | :--- | :--- |
| **公司官网** | **权威性 (Authority)** | 必须部署 **JSON-LD (Schema.org)** 标记，明确声明 "Product", "Organization" 实体。提供 PDF 白皮书下载（AI 也会读 PDF）。 |
| **技术社区 (GitHub/CSDN)** | **代码与复现性** | 提供 "How-to" 教程。代码块要标记清楚语言。README 必须标准完整。 |
| **社交媒体 (Reddit/知乎)** | **真实讨论 (Discussion)** | AI 极其看重 Reddit/知乎 的"人类真实评价"。需要引发讨论，包含具体使用场景的细节描述。 |
| **电商平台** | **参数准确性** | 参数表必须标准化。评论区包含详细的技术反馈（AI 会分析评论情感）。 |

## 3. 关键词与实体植入 (Entity Injection)
*   **创造专有名词**: 为您的技术或架构起一个独特的名称（如 "SpherLab Architecture"），并在多处重复定义它。
*   **建立关联**: 总是把您的品牌与知名实体放在一起提及（例如 "基于 **Raspberry Pi** 的 **SpherLab** 方案"），利用知名实体的权重带动新实体。

## 4. 这里的"投喂"计划 (Next Steps)
1.  **建立知识库**: 在官网建立 Wiki 或 Docs 栏目。
2.  **分发**: 将同一份核心技术文档，改编成：
    *   *GitHub README* (技术向)
    *   *知乎/Medium 文章* (科普向)
    *   *YouTube 视频脚本* (视频字幕也是 AI 的重要语料)
