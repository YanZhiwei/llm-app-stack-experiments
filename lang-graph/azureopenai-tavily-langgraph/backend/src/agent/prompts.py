from datetime import datetime


# Get current date in a readable format
def get_current_date():
    return datetime.now().strftime("%B %d, %Y")


query_writer_instructions = """您的目标是生成复杂且多样化的网络搜索查询。这些查询旨在用于一个高级的自动化网络研究工具，该工具能够分析复杂结果、跟踪链接并综合信息。

重要语言规则：
- 如果用户问题使用中文，请生成中文搜索查询
- 如果用户问题使用英文，请生成英文搜索查询
- 如果用户问题使用其他语言，请生成相应语言的搜索查询
- 查询语言必须与用户问题的语言保持一致

说明：
- 始终优先使用单个搜索查询，只有当原始问题请求多个方面或元素且一个查询不够时才添加另一个查询。
- 每个查询应该专注于原始问题的一个特定方面。
- 不要生成超过 {number_queries} 个查询。
- 查询应该是多样化的，如果主题很广泛，生成超过1个查询。
- 不要生成多个相似的查询，1个就足够了。
- 查询应确保收集最新的信息。当前日期是 {current_date}。

格式：
- 将您的响应格式化为包含以下两个确切键的JSON对象：
   - "rationale": 简要说明为什么这些查询是相关的（使用与用户问题相同的语言）
   - "query": 搜索查询列表（使用与用户问题相同的语言）

示例：

中文主题：人工智能在医疗诊断中的应用
```json
{{
    "rationale": "为了全面了解人工智能在医疗诊断中的应用，我们需要查询AI医疗技术、医学影像分析、机器学习医疗应用等不同方面的信息。",
    "query": ["人工智能医疗诊断技术", "AI医学影像分析应用", "机器学习医疗诊断系统"]
}}
```

英文主题：Apple stock revenue growth vs iPhone sales growth 2024
```json
{{
    "rationale": "To accurately answer this growth comparison question, we need specific data points on Apple's stock performance and iPhone sales metrics. These queries target the precise financial information needed: company revenue trends, product-specific unit sales data, and stock price movements within the same fiscal period for direct comparison.",
    "query": ["Apple total revenue growth fiscal year 2024", "iPhone unit sales growth fiscal year 2024", "Apple stock price growth fiscal year 2024"]
}}
```

上下文：{research_topic}"""


web_searcher_instructions = """进行有针对性的Google搜索，收集关于"{research_topic}"的最新、可信信息，并将其综合成可验证的文本工件。

说明：
- 查询应确保收集最新的信息。当前日期是 {current_date}。
- 进行多次、多样化的搜索以收集全面的信息。
- 整合关键发现，同时仔细跟踪每个特定信息片段的来源。
- 输出应该基于您的搜索结果写成一份总结或报告。
- 只包含在搜索结果中找到的信息，不要编造任何信息。

研究主题：
{research_topic}
"""

reflection_instructions = """您是一位专家研究助手，正在分析关于"{research_topic}"的摘要。

说明：
- 识别知识空白或需要深入探索的领域，并生成后续查询（1个或多个）。
- 如果提供的摘要足以回答用户的问题，请不要生成后续查询。
- 如果存在知识空白，生成一个有助于扩展您理解的后续查询。
- 专注于技术细节、实施细节或未完全涵盖的新兴趋势。

要求：
- 确保后续查询是自包含的，并包含网络搜索所需的必要上下文。

输出格式：
- 将您的响应格式化为包含以下确切键的JSON对象：
   - "is_sufficient": true 或 false
   - "knowledge_gap": 描述缺少什么信息或需要澄清什么
   - "follow_up_queries": 写一个具体的问题来解决这个空白

示例：
```json
{{
    "is_sufficient": true, // 或 false
    "knowledge_gap": "摘要缺乏关于性能指标和基准的信息", // 如果 is_sufficient 为 true 则为 ""
    "follow_up_queries": ["用于评估[特定技术]的典型性能基准和指标是什么？"] // 如果 is_sufficient 为 true 则为 []
}}
```

仔细反思摘要以识别知识空白并产生后续查询。然后，按照此JSON格式产生您的输出：

摘要：
{summaries}
"""

answer_instructions = """基于提供的摘要生成用户问题的高质量答案。

说明：
- 当前日期是 {current_date}。
- 您是多步骤研究过程的最后一步，不要提及您是最后一步。
- 您可以访问从前面的步骤收集的所有信息。
- 您可以访问用户的问题。
- 基于提供的摘要和用户的问题生成用户问题的高质量答案。
- 在答案中正确包含您从摘要中使用的来源，使用markdown格式（例如 [apnews](https://vertexaisearch.cloud.google.com/id/1-0)）。这是必须的。

用户上下文：
- {research_topic}

摘要：
{summaries}"""
