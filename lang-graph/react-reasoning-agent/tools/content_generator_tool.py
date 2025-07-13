"""
基于LLM的通用内容生成工具 - 整合其他工具输出并生成详细结构化内容
"""

from typing import Any, Dict, List, Optional

from langchain_core.tools import tool


@tool
def generate_detailed_content(
    topic: str,
    content_type: str = "report",
    sections: Optional[str] = None,
    detail_level: str = "detailed",
    source_materials: Optional[str] = None,
    language: str = "chinese"
) -> Dict[str, Any]:
    """
    基于源材料生成详细的结构化内容

    Args:
        topic: 主题或项目名称
        content_type: 内容类型 (report/analysis/plan/guide/proposal/research)
        sections: 需要包含的章节 (逗号分隔或JSON格式)
        detail_level: 详细程度 (basic/detailed/comprehensive)
        source_materials: 源材料内容 (其他工具的输出结果)
        language: 语言 (chinese/english)

    Returns:
        包含生成内容的字典
    """
    try:
        # 解析章节要求
        sections_list = _parse_sections(sections)

        # 生成内容大纲
        outline = _generate_content_outline(
            topic, content_type, sections_list, detail_level)

        # 构建提示词并生成内容
        content = _generate_content_with_llm(
            topic=topic,
            content_type=content_type,
            outline=outline,
            detail_level=detail_level,
            source_materials=source_materials,
            language=language
        )

        return {
            "status": "success",
            "message": "内容生成成功",
            "topic": topic,
            "content_type": content_type,
            "detail_level": detail_level,
            "language": language,
            "content": content,
            "word_count": len(content.split()),
            "sections_count": len(outline),
            "outline": outline,
            "has_source_materials": bool(source_materials)
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"内容生成失败: {str(e)}",
            "error": str(e)
        }


def _parse_sections(sections: Optional[str]) -> List[str]:
    """解析章节要求"""
    if not sections:
        return []

    import json

    try:
        # 尝试解析JSON格式
        if sections.strip().startswith('[') or sections.strip().startswith('{'):
            parsed = json.loads(sections)
            if isinstance(parsed, list):
                return parsed
            elif isinstance(parsed, dict):
                return list(parsed.keys())
    except json.JSONDecodeError:
        pass

    # 按逗号分隔
    return [s.strip() for s in sections.split(',') if s.strip()]


def _generate_content_outline(topic: str, content_type: str, sections: List[str], detail_level: str) -> List[str]:
    """生成内容大纲"""

    # 根据内容类型生成默认大纲
    outline_templates = {
        "report": ["概述", "背景分析", "现状调研", "问题识别", "解决方案", "实施建议", "预期效果", "结论"],
        "analysis": ["背景介绍", "数据分析", "趋势分析", "影响因素", "风险评估", "机会识别", "建议措施"],
        "plan": ["项目概述", "目标设定", "现状分析", "策略制定", "实施计划", "资源配置", "风险管理", "监控评估"],
        "guide": ["基础知识", "准备工作", "详细步骤", "注意事项", "常见问题", "最佳实践", "进阶技巧"],
        "proposal": ["项目背景", "问题描述", "解决方案", "技术方案", "实施计划", "预算估算", "团队配置", "风险控制"],
        "research": ["研究背景", "文献综述", "研究方法", "数据收集", "结果分析", "讨论", "结论与建议"]
    }

    # 如果用户指定了章节，使用用户指定的
    if sections:
        return sections

    # 否则使用默认模板
    default_outline = outline_templates.get(
        content_type, outline_templates["report"])

    # 根据详细程度调整章节数量
    if detail_level == "basic":
        return default_outline[:4]  # 只取前4个章节
    elif detail_level == "comprehensive":
        return default_outline  # 使用所有章节
    else:  # detailed
        return default_outline[:6]  # 取前6个章节


def _generate_content_with_llm(
    topic: str,
    content_type: str,
    outline: List[str],
    detail_level: str,
    source_materials: Optional[str],
    language: str
) -> str:
    """使用LLM生成详细内容"""

    # 如果没有LLM可用，使用模板生成
    try:
        from agents import llm
        if not llm:
            return _generate_template_content(topic, content_type, outline, detail_level, source_materials, language)
    except ImportError:
        return _generate_template_content(topic, content_type, outline, detail_level, source_materials, language)

    # 构建系统提示词
    system_prompt = _build_system_prompt(content_type, detail_level, language)

    # 构建用户提示词
    user_prompt = _build_user_prompt(
        topic, outline, source_materials, language)

    try:
        from langchain_core.messages import HumanMessage, SystemMessage

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        # 调用LLM生成内容
        response = llm.invoke(messages)
        return str(response.content).strip()

    except Exception as e:
        print(f"⚠️ LLM调用失败: {e}")
        # 回退到模板生成
        return _generate_template_content(topic, content_type, outline, detail_level, source_materials, language)


def _build_system_prompt(content_type: str, detail_level: str, language: str) -> str:
    """构建系统提示词"""

    content_type_descriptions = {
        "report": "专业报告",
        "analysis": "深度分析",
        "plan": "详细计划",
        "guide": "实用指南",
        "proposal": "项目提案",
        "research": "研究报告"
    }

    detail_level_descriptions = {
        "basic": "简洁明了，重点突出",
        "detailed": "详细全面，逻辑清晰",
        "comprehensive": "深入透彻，覆盖全面"
    }

    language_settings = {
        "chinese": "中文",
        "english": "English"
    }

    content_desc = content_type_descriptions.get(content_type, "专业文档")
    detail_desc = detail_level_descriptions.get(detail_level, "详细全面")
    lang_desc = language_settings.get(language, "中文")

    system_prompt = f"""你是一个专业的{content_desc}撰写专家。请根据用户提供的主题、大纲和源材料，生成一份{detail_desc}的{content_desc}。

## 撰写要求：

### 内容质量
- 专业性强：使用专业术语和行业标准
- 逻辑清晰：结构合理，层次分明
- 内容丰富：每个章节都要有实质性内容
- 实用性强：提供可行的建议和方案

### 格式要求
- 使用Markdown格式
- 标题层级清晰（# ## ###）
- 适当使用列表、表格等格式
- 添加必要的强调和重点标记

### 详细程度
- {detail_desc}：确保每个章节都有充分的内容
- 包含具体的数据、案例、步骤和建议
- 避免空洞的套话，提供实质性信息

### 语言要求
- 使用{lang_desc}撰写
- 语言专业、准确、流畅
- 符合{content_desc}的撰写规范

### 源材料处理
- 如果提供了源材料，要充分利用和扩展
- 对源材料进行分析、整理和深化
- 补充相关的背景信息和专业见解
- 确保内容的完整性和连贯性

请严格按照用户指定的大纲结构生成内容，确保每个章节都有丰富、专业、实用的内容。"""

    return system_prompt


def _build_user_prompt(topic: str, outline: List[str], source_materials: Optional[str], language: str) -> str:
    """构建用户提示词"""

    # 基础信息
    user_prompt = f"""请为以下主题生成详细内容：

## 主题
{topic}

## 要求的章节大纲
{chr(10).join([f"{i+1}. {section}" for i, section in enumerate(outline)])}
"""

    # 添加源材料（如果有）
    if source_materials and source_materials.strip():
        user_prompt += f"""

## 源材料
以下是收集到的相关信息，请基于这些材料进行扩展和深化：

```
{source_materials}
```

请充分利用上述源材料，进行分析、整理和扩展，生成更加丰富和专业的内容。
"""
    else:
        user_prompt += """

## 内容要求
由于没有提供源材料，请基于主题和章节大纲，生成专业、详细的内容。请确保：
- 每个章节都有实质性的内容
- 包含相关的行业知识和最佳实践
- 提供具体的建议和指导
- 内容逻辑清晰，结构合理
"""

    user_prompt += f"""

## 输出格式
请严格按照以下格式输出：

```markdown
# {topic}

*生成时间: [当前时间]*

## [章节1名称]
[详细内容...]

## [章节2名称]
[详细内容...]

...
```

请确保每个章节都有丰富、专业、实用的内容，避免空洞的描述。"""

    return user_prompt


def _generate_template_content(
    topic: str,
    content_type: str,
    outline: List[str],
    detail_level: str,
    source_materials: Optional[str],
    language: str
) -> str:
    """生成模板内容（LLM不可用时的回退方案）"""

    from datetime import datetime

    content_parts = []

    # 添加标题和时间戳
    content_parts.append(f"# {topic}")
    content_parts.append("")
    timestamp = datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")
    content_parts.append(f"*生成时间: {timestamp}*")
    content_parts.append("")

    # 如果有源材料，先添加材料摘要
    if source_materials and source_materials.strip():
        content_parts.append("## 信息来源")
        content_parts.append("")
        content_parts.append("基于以下收集的信息进行分析和扩展：")
        content_parts.append("")
        content_parts.append("```")
        content_parts.append(
            source_materials[:500] + "..." if len(source_materials) > 500 else source_materials)
        content_parts.append("```")
        content_parts.append("")

    # 为每个章节生成内容
    for section in outline:
        content_parts.append(f"## {section}")
        content_parts.append("")

        section_content = _generate_section_template(
            topic, section, source_materials, detail_level)
        content_parts.append(section_content)
        content_parts.append("")

    return "\n".join(content_parts)


def _generate_section_template(topic: str, section: str, source_materials: Optional[str], detail_level: str) -> str:
    """生成章节模板内容"""

    # 基础内容模板
    base_content = f"""
针对{topic}的{section}，我们需要从以下几个方面进行分析：

### 核心要点
- **现状评估**：分析当前的实际情况和发展水平
- **关键因素**：识别影响{section}的主要因素
- **挑战识别**：明确面临的主要挑战和困难
- **机会分析**：发现潜在的机会和发展空间

### 具体分析
在{section}方面，{topic}需要重点关注以下内容：

1. **深入研究**：对相关领域进行深入的调研和分析
2. **最佳实践**：参考行业内的成功案例和最佳实践
3. **创新思维**：结合创新理念，提出有效的解决方案
4. **实施策略**：制定具体可行的实施策略和行动计划

### 建议措施
基于以上分析，建议采取以下措施：
- 建立完善的评估和监控机制
- 制定详细的实施计划和时间表
- 配置必要的资源和人力支持
- 建立有效的沟通和协调机制
    """.strip()

    # 如果有源材料，尝试整合
    if source_materials and source_materials.strip():
        base_content += f"""

### 基于现有信息的分析
根据收集到的相关信息，在{section}方面需要特别注意：

- 结合实际情况，制定针对性的策略
- 充分利用现有资源和优势
- 关注潜在的风险和挑战
- 建立持续改进的机制
        """.strip()

    # 根据详细程度调整内容长度
    if detail_level == "basic":
        return base_content[:300] + "..."
    elif detail_level == "comprehensive":
        base_content += f"""

### 深度分析
从更深层次来看，{section}涉及多个维度的考虑：

**技术维度**：关注技术的先进性、可靠性和适用性
**经济维度**：考虑成本效益、投入产出比和可持续性
**管理维度**：注重组织架构、流程优化和人员配置
**风险维度**：识别潜在风险，制定应对策略

### 实施路径
建议采用分阶段、渐进式的实施方式：
1. 前期准备和规划阶段
2. 试点实施和验证阶段  
3. 全面推广和优化阶段
4. 持续改进和创新阶段

### 成功要素
确保{section}成功的关键要素包括：
- 明确的目标和期望
- 充分的资源投入
- 有效的组织和管理
- 持续的监控和评估
        """.strip()

    return base_content
