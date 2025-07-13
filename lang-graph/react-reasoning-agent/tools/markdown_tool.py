"""
Markdown生成工具 - 支持创建专业的markdown报告和文档
"""

import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from langchain_core.tools import tool


@tool
def create_markdown_report(
    title: str,
    content: str,
    save_file: Optional[str] = None,
    template: str = "business"
) -> Dict[str, Any]:
    """
    创建markdown报告

    Args:
        title: 报告标题
        content: 报告内容（JSON字符串格式）
        save_file: 保存文件名（可选）
        template: 模板类型（business/simple/detailed）
    """
    try:
        import json

        # 解析内容
        if isinstance(content, str):
            try:
                content_dict = json.loads(content)
            except json.JSONDecodeError:
                # 如果不是JSON，作为普通文本处理
                content_dict = {"content": content}
        else:
            content_dict = content

        # 生成markdown内容
        markdown_content = _generate_markdown_content(
            title, content_dict, template)

        # 保存到文件
        if save_file:
            if not save_file.endswith('.md'):
                save_file += '.md'

            with open(save_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            return {
                "status": "success",
                "message": f"Markdown报告已保存到 {save_file}",
                "file_path": save_file,
                "content": markdown_content,
                "word_count": len(markdown_content.split()),
                "line_count": len(markdown_content.split('\n'))
            }

        return {
            "status": "success",
            "message": "Markdown报告生成成功",
            "content": markdown_content,
            "word_count": len(markdown_content.split()),
            "line_count": len(markdown_content.split('\n'))
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Markdown报告生成失败: {str(e)}",
            "error": str(e)
        }


@tool
def create_business_trip_report(
    title: str,
    trip_data: str,
    save_file: Optional[str] = None,
    include_charts: bool = True,
    include_summary: bool = True
) -> Dict[str, Any]:
    """
    创建专业的商务出差分析报告

    Args:
        title: 报告标题
        trip_data: 出差数据（JSON字符串格式）
        save_file: 保存文件名（可选）
        include_charts: 是否包含图表（文本图表）
        include_summary: 是否包含执行摘要
    """
    try:
        import json

        # 解析数据
        if isinstance(trip_data, str):
            try:
                data = json.loads(trip_data)
            except json.JSONDecodeError:
                return {
                    "status": "error",
                    "message": "无效的JSON数据格式"
                }
        else:
            data = trip_data

        # 生成专业的商务出差报告
        markdown_content = _generate_business_trip_template(
            title, data, include_charts, include_summary)

        # 保存到文件
        if save_file:
            if not save_file.endswith('.md'):
                save_file += '.md'

            with open(save_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            return {
                "status": "success",
                "message": f"商务出差报告已保存到 {save_file}",
                "file_path": save_file,
                "content": markdown_content,
                "word_count": len(markdown_content.split()),
                "section_count": markdown_content.count('## '),
                "chart_count": markdown_content.count('```mermaid') + markdown_content.count('📊')
            }

        return {
            "status": "success",
            "message": "商务出差报告生成成功",
            "content": markdown_content,
            "word_count": len(markdown_content.split()),
            "section_count": markdown_content.count('## ')
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"商务出差报告生成失败: {str(e)}",
            "error": str(e)
        }


@tool
def create_markdown_table(
    headers: str,
    rows: str,
    alignment: Optional[str] = None,
    caption: Optional[str] = None
) -> Dict[str, Any]:
    """
    创建markdown表格

    Args:
        headers: 表头列表（JSON字符串格式）
        rows: 数据行列表（JSON字符串格式）
        alignment: 对齐方式列表（JSON字符串格式）
        caption: 表格标题
    """
    try:
        import json

        # 解析参数
        headers_list = json.loads(headers) if isinstance(
            headers, str) else headers
        rows_list = json.loads(rows) if isinstance(rows, str) else rows
        alignment_list = json.loads(alignment) if alignment else None

        if not headers_list or not rows_list:
            return {
                "status": "error",
                "message": "表头和数据行不能为空"
            }

        # 生成表格
        table_lines = []

        # 表格标题
        if caption:
            table_lines.append(f"**{caption}**\n")

        # 表头
        table_lines.append("| " + " | ".join(headers_list) + " |")

        # 分隔线
        if alignment_list:
            alignment_map = {
                'left': ':--',
                'center': ':-:',
                'right': '--:'
            }
            separators = [alignment_map.get(align, '---')
                          for align in alignment_list]
        else:
            separators = ['---'] * len(headers_list)

        table_lines.append("| " + " | ".join(separators) + " |")

        # 数据行
        for row in rows_list:
            # 确保行长度与表头一致
            padded_row = row + [''] * (len(headers_list) - len(row))
            table_lines.append(
                "| " + " | ".join(padded_row[:len(headers_list)]) + " |")

        markdown_table = "\n".join(table_lines)

        return {
            "status": "success",
            "message": "Markdown表格生成成功",
            "table": markdown_table,
            "headers": headers_list,
            "row_count": len(rows_list),
            "column_count": len(headers_list)
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Markdown表格生成失败: {str(e)}",
            "error": str(e)
        }


@tool
def create_enhanced_markdown_table(
    headers: str,
    rows: str,
    table_style: str = "standard",
    alignment: Optional[str] = None,
    caption: Optional[str] = None,
    highlight_rows: Optional[str] = None
) -> Dict[str, Any]:
    """
    创建增强版markdown表格，支持更多样式和功能

    Args:
        headers: 表头列表（JSON字符串格式）
        rows: 数据行列表（JSON字符串格式）
        table_style: 表格样式（standard/colored/bordered/compact）
        alignment: 对齐方式列表（JSON字符串格式）
        caption: 表格标题
        highlight_rows: 需要高亮的行索引（JSON字符串格式）
    """
    try:
        import json

        # 解析参数
        headers_list = json.loads(headers) if isinstance(
            headers, str) else headers
        rows_list = json.loads(rows) if isinstance(rows, str) else rows
        alignment_list = json.loads(alignment) if alignment else None
        highlight_rows_list = json.loads(
            highlight_rows) if highlight_rows else []

        if not headers_list or not rows_list:
            return {
                "status": "error",
                "message": "表头和数据行不能为空"
            }

        # 生成增强表格
        table_lines = []

        # 表格标题
        if caption:
            if table_style == "colored":
                table_lines.append(f"### 📊 {caption}")
            else:
                table_lines.append(f"**{caption}**")
            table_lines.append("")

        # 表头
        if table_style == "bordered":
            table_lines.append(
                "┌" + "─" * (sum(len(h) + 3 for h in headers_list) - 1) + "┐")
            table_lines.append("│ " + " │ ".join(headers_list) + " │")
            table_lines.append(
                "├" + "─" * (sum(len(h) + 3 for h in headers_list) - 1) + "┤")
        else:
            table_lines.append("| " + " | ".join(headers_list) + " |")

        # 分隔线
        if table_style != "bordered":
            if alignment_list:
                alignment_map = {
                    'left': ':--',
                    'center': ':-:',
                    'right': '--:'
                }
                separators = [alignment_map.get(
                    align, '---') for align in alignment_list]
            else:
                separators = ['---'] * len(headers_list)

            table_lines.append("| " + " | ".join(separators) + " |")

        # 数据行
        for i, row in enumerate(rows_list):
            # 确保行长度与表头一致
            padded_row = row + [''] * (len(headers_list) - len(row))
            row_data = padded_row[:len(headers_list)]

            # 高亮行处理
            if i in highlight_rows_list:
                if table_style == "colored":
                    row_data = [f"**{cell}**" for cell in row_data]
                else:
                    row_data = [f"*{cell}*" for cell in row_data]

            if table_style == "bordered":
                table_lines.append("│ " + " │ ".join(row_data) + " │")
            else:
                table_lines.append("| " + " | ".join(row_data) + " |")

        if table_style == "bordered":
            table_lines.append(
                "└" + "─" * (sum(len(h) + 3 for h in headers_list) - 1) + "┘")

        markdown_table = "\n".join(table_lines)

        return {
            "status": "success",
            "message": "增强版Markdown表格生成成功",
            "table": markdown_table,
            "style": table_style,
            "headers": headers_list,
            "row_count": len(rows_list),
            "column_count": len(headers_list),
            "highlighted_rows": highlight_rows_list
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"增强版Markdown表格生成失败: {str(e)}",
            "error": str(e)
        }


@tool
def format_markdown_content(
    content: str,
    format_type: str = "standard",
    add_toc: bool = False,
    add_timestamp: bool = True
) -> Dict[str, Any]:
    """
    格式化markdown内容

    Args:
        content: 原始内容
        format_type: 格式类型 (standard/github/business)
        add_toc: 是否添加目录
        add_timestamp: 是否添加时间戳
    """
    try:
        formatted_content = content

        # 添加时间戳
        if add_timestamp:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            formatted_content = f"*生成时间: {timestamp}*\n\n" + formatted_content

        # 添加目录
        if add_toc:
            toc = _generate_table_of_contents(content)
            if toc:
                formatted_content = toc + "\n\n" + formatted_content

        # 应用格式化样式
        if format_type == "business":
            formatted_content = _apply_business_formatting(formatted_content)
        elif format_type == "github":
            formatted_content = _apply_github_formatting(formatted_content)

        return {
            "status": "success",
            "message": "Markdown内容格式化成功",
            "formatted_content": formatted_content,
            "original_length": len(content),
            "formatted_length": len(formatted_content)
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Markdown内容格式化失败: {str(e)}",
            "error": str(e)
        }


@tool
def create_text_chart(
    chart_type: str,
    data: str,
    title: Optional[str] = None,
    labels: Optional[str] = None
) -> Dict[str, Any]:
    """
    创建文本图表（ASCII艺术风格）

    Args:
        chart_type: 图表类型（bar/pie/line）
        data: 数据列表（JSON字符串格式）
        title: 图表标题
        labels: 数据标签（JSON字符串格式）
    """
    try:
        import json

        # 解析数据
        data_list = json.loads(data) if isinstance(data, str) else data
        labels_list = json.loads(labels) if labels else None

        if not data_list:
            return {
                "status": "error",
                "message": "数据不能为空"
            }

        # 生成图表
        if chart_type == "bar":
            chart_content = _generate_bar_chart(data_list, labels_list, title)
        elif chart_type == "pie":
            chart_content = _generate_pie_chart(data_list, labels_list, title)
        elif chart_type == "line":
            chart_content = _generate_line_chart(data_list, labels_list, title)
        else:
            return {
                "status": "error",
                "message": f"不支持的图表类型: {chart_type}"
            }

        return {
            "status": "success",
            "message": f"{chart_type}图表生成成功",
            "chart": chart_content,
            "type": chart_type,
            "data_points": len(data_list)
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"图表生成失败: {str(e)}",
            "error": str(e)
        }


def _generate_markdown_content(title: str, content: Dict[str, Any], template: str) -> str:
    """生成markdown内容"""

    lines = []

    # 标题
    lines.append(f"# {title}")
    lines.append("")

    # 时间戳
    timestamp = datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")
    lines.append(f"*生成时间: {timestamp}*")
    lines.append("")

    if template == "business":
        return _generate_business_template(lines, content)
    elif template == "detailed":
        return _generate_detailed_template(lines, content)
    else:
        return _generate_simple_template(lines, content)


def _generate_business_template(lines: List[str], content: Dict[str, Any]) -> str:
    """生成商业模板"""

    # 执行摘要
    if "summary" in content:
        lines.append("## 📋 执行摘要")
        lines.append("")
        lines.append(content["summary"])
        lines.append("")

    # 分析结果
    if "analysis" in content:
        lines.append("## 📊 分析结果")
        lines.append("")
        analysis = content["analysis"]
        if isinstance(analysis, dict):
            for key, value in analysis.items():
                lines.append(f"### {key}")
                lines.append("")
                if isinstance(value, list):
                    for item in value:
                        lines.append(f"- {item}")
                else:
                    lines.append(str(value))
                lines.append("")
        else:
            lines.append(str(analysis))
            lines.append("")

    # 成本明细
    if "costs" in content:
        lines.append("## 💰 成本明细")
        lines.append("")
        costs = content["costs"]
        if isinstance(costs, dict):
            for category, amount in costs.items():
                lines.append(f"- **{category}**: {amount}")
        else:
            lines.append(str(costs))
        lines.append("")

    # 风险评估
    if "risks" in content:
        lines.append("## ⚠️ 风险评估")
        lines.append("")
        risks = content["risks"]
        if isinstance(risks, list):
            for risk in risks:
                lines.append(f"- {risk}")
        else:
            lines.append(str(risks))
        lines.append("")

    # 建议
    if "recommendations" in content:
        lines.append("## 💡 建议")
        lines.append("")
        recommendations = content["recommendations"]
        if isinstance(recommendations, list):
            for i, rec in enumerate(recommendations, 1):
                lines.append(f"{i}. {rec}")
        else:
            lines.append(str(recommendations))
        lines.append("")

    # 结论
    if "conclusion" in content:
        lines.append("## 🎯 结论")
        lines.append("")
        lines.append(content["conclusion"])
        lines.append("")

    # 其他内容
    for key, value in content.items():
        if key not in ["summary", "analysis", "costs", "risks", "recommendations", "conclusion"]:
            lines.append(f"## {key}")
            lines.append("")
            if isinstance(value, dict):
                for subkey, subvalue in value.items():
                    lines.append(f"### {subkey}")
                    lines.append("")
                    lines.append(str(subvalue))
                    lines.append("")
            elif isinstance(value, list):
                for item in value:
                    lines.append(f"- {item}")
                lines.append("")
            else:
                lines.append(str(value))
                lines.append("")

    return "\n".join(lines)


def _generate_detailed_template(lines: List[str], content: Dict[str, Any]) -> str:
    """生成详细模板"""

    for key, value in content.items():
        lines.append(f"## {key}")
        lines.append("")

        if isinstance(value, dict):
            for subkey, subvalue in value.items():
                lines.append(f"### {subkey}")
                lines.append("")
                lines.append(str(subvalue))
                lines.append("")
        elif isinstance(value, list):
            for item in value:
                lines.append(f"- {item}")
            lines.append("")
        else:
            lines.append(str(value))
            lines.append("")

    return "\n".join(lines)


def _generate_simple_template(lines: List[str], content: Dict[str, Any]) -> str:
    """生成简单模板"""

    for key, value in content.items():
        lines.append(f"## {key}")
        lines.append("")
        lines.append(str(value))
        lines.append("")

    return "\n".join(lines)


def _generate_table_of_contents(content: str) -> str:
    """生成目录"""

    lines = content.split('\n')
    toc_lines = ["## 目录", ""]

    for line in lines:
        if line.startswith('## '):
            title = line[3:].strip()
            anchor = title.lower().replace(' ', '-')
            toc_lines.append(f"- [{title}](#{anchor})")
        elif line.startswith('### '):
            title = line[4:].strip()
            anchor = title.lower().replace(' ', '-')
            toc_lines.append(f"  - [{title}](#{anchor})")

    return "\n".join(toc_lines) if len(toc_lines) > 2 else ""


def _apply_business_formatting(content: str) -> str:
    """应用商业格式化"""

    # 添加一些商业格式化样式
    content = content.replace("## 📋", "## 📋 Executive Summary")
    content = content.replace("## 📊", "## 📊 Analysis Results")
    content = content.replace("## 💰", "## 💰 Cost Breakdown")
    content = content.replace("## ⚠️", "## ⚠️ Risk Assessment")
    content = content.replace("## 💡", "## 💡 Recommendations")
    content = content.replace("## 🎯", "## 🎯 Conclusion")

    return content


def _apply_github_formatting(content: str) -> str:
    """应用GitHub格式化"""

    # 添加GitHub风格的格式化
    lines = content.split('\n')
    formatted_lines = []

    for line in lines:
        if line.startswith('# '):
            formatted_lines.append(line)
            formatted_lines.append("=" * (len(line) - 2))
        elif line.startswith('## '):
            formatted_lines.append(line)
            formatted_lines.append("-" * (len(line) - 3))
        else:
            formatted_lines.append(line)

    return '\n'.join(formatted_lines)


def _generate_business_trip_template(title: str, data: Dict[str, Any], include_charts: bool, include_summary: bool) -> str:
    """生成专业的商务出差报告模板"""

    lines = []
    timestamp = datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")

    # 报告标题和基本信息
    lines.extend([
        f"# {title}",
        "",
        f"**📅 报告生成时间**: {timestamp}",
        f"**📍 出差目的地**: {data.get('destination', 'N/A')}",
        f"**🗓️ 出差时间**: {data.get('travel_dates', 'N/A')}",
        f"**👥 出差人数**: {data.get('travelers', 'N/A')}",
        "",
        "---",
        ""
    ])

    # 执行摘要
    if include_summary and 'summary' in data:
        lines.extend([
            "## 📋 执行摘要",
            "",
            "### 关键信息",
            ""
        ])

        summary = data['summary']
        if isinstance(summary, dict):
            for key, value in summary.items():
                lines.append(f"- **{key}**: {value}")
        else:
            lines.append(str(summary))

        lines.extend(["", "---", ""])

    # 航班信息
    if 'flights' in data:
        lines.extend([
            "## ✈️ 航班信息",
            "",
            "### 推荐航班选择",
            ""
        ])

        flights = data['flights']
        if isinstance(flights, dict):
            for key, value in flights.items():
                lines.append(f"**{key}**: {value}")
                lines.append("")
        elif isinstance(flights, list):
            for i, flight in enumerate(flights, 1):
                lines.append(f"### 选项 {i}")
                if isinstance(flight, dict):
                    for key, value in flight.items():
                        lines.append(f"- **{key}**: {value}")
                else:
                    lines.append(f"- {flight}")
                lines.append("")

        lines.extend(["---", ""])

    # 成本分析
    if 'costs' in data:
        lines.extend([
            "## 💰 成本分析",
            "",
            "### 详细成本明细",
            ""
        ])

        costs = data['costs']
        if isinstance(costs, dict):
            total_cost = 0
            for category, details in costs.items():
                if isinstance(details, dict):
                    lines.append(f"#### {category}")
                    for item, amount in details.items():
                        lines.append(f"- {item}: {amount}")
                        # 尝试提取数字进行总计
                        try:
                            if isinstance(amount, (int, float)):
                                total_cost += amount
                            elif isinstance(amount, str):
                                import re
                                numbers = re.findall(r'[\d,]+\.?\d*', amount)
                                if numbers:
                                    total_cost += float(
                                        numbers[0].replace(',', ''))
                        except:
                            pass
                else:
                    lines.append(f"- **{category}**: {details}")
                lines.append("")

            if total_cost > 0:
                lines.extend([
                    "### 💵 总成本概览",
                    f"",
                    f"**总计**: ¥{total_cost:,.2f}",
                    ""
                ])

        lines.extend(["---", ""])

    # 风险评估
    if 'risks' in data:
        lines.extend([
            "## ⚠️ 风险评估",
            "",
            "### 潜在风险因素",
            ""
        ])

        risks = data['risks']
        if isinstance(risks, dict):
            for category, risk_list in risks.items():
                lines.append(f"#### {category}")
                if isinstance(risk_list, list):
                    for risk in risk_list:
                        lines.append(f"- {risk}")
                else:
                    lines.append(f"- {risk_list}")
                lines.append("")
        elif isinstance(risks, list):
            for risk in risks:
                lines.append(f"- {risk}")

        lines.extend(["", "---", ""])

    # 天气分析
    if 'weather' in data:
        lines.extend([
            "## 🌤️ 天气分析",
            "",
            "### 天气状况与建议",
            ""
        ])

        weather = data['weather']
        if isinstance(weather, dict):
            for key, value in weather.items():
                lines.append(f"**{key}**: {value}")
                lines.append("")
        else:
            lines.append(str(weather))

        lines.extend(["", "---", ""])

    # 优化建议
    if 'recommendations' in data:
        lines.extend([
            "## 💡 优化建议",
            "",
            "### 成本节省与效率提升",
            ""
        ])

        recommendations = data['recommendations']
        if isinstance(recommendations, dict):
            for category, rec_list in recommendations.items():
                lines.append(f"#### {category}")
                if isinstance(rec_list, list):
                    for i, rec in enumerate(rec_list, 1):
                        lines.append(f"{i}. {rec}")
                else:
                    lines.append(f"- {rec_list}")
                lines.append("")
        elif isinstance(recommendations, list):
            for i, rec in enumerate(recommendations, 1):
                lines.append(f"{i}. {rec}")

        lines.extend(["", "---", ""])

    # 时间规划
    if 'schedule' in data:
        lines.extend([
            "## 📅 时间规划",
            "",
            "### 行程安排与工作影响",
            ""
        ])

        schedule = data['schedule']
        if isinstance(schedule, dict):
            for key, value in schedule.items():
                lines.append(f"**{key}**: {value}")
                lines.append("")
        else:
            lines.append(str(schedule))

        lines.extend(["", "---", ""])

    # 结论
    if 'conclusion' in data:
        lines.extend([
            "## 🎯 结论与决策建议",
            "",
            "### 最终建议",
            ""
        ])

        conclusion = data['conclusion']
        if isinstance(conclusion, dict):
            for key, value in conclusion.items():
                lines.append(f"**{key}**: {value}")
                lines.append("")
        else:
            lines.append(str(conclusion))

        lines.extend(["", "---", ""])

    # 附加信息
    additional_sections = ['analysis', 'comparisons', 'alternatives', 'notes']
    for section in additional_sections:
        if section in data:
            section_title = {
                'analysis': '📊 详细分析',
                'comparisons': '⚖️ 方案对比',
                'alternatives': '🔄 备选方案',
                'notes': '📝 备注信息'
            }.get(section, section.title())

            lines.extend([
                f"## {section_title}",
                "",
            ])

            section_data = data[section]
            if isinstance(section_data, dict):
                for key, value in section_data.items():
                    lines.append(f"### {key}")
                    if isinstance(value, list):
                        for item in value:
                            lines.append(f"- {item}")
                    else:
                        lines.append(str(value))
                    lines.append("")
            elif isinstance(section_data, list):
                for item in section_data:
                    lines.append(f"- {item}")
                lines.append("")
            else:
                lines.append(str(section_data))
                lines.append("")

            lines.extend(["---", ""])

    # 生成简单的文本图表（如果需要）
    if include_charts and 'chart_data' in data:
        lines.extend([
            "## 📊 数据可视化",
            "",
            "### 成本分布图",
            ""
        ])

        chart_data = data['chart_data']
        if isinstance(chart_data, dict):
            # 生成简单的柱状图
            max_value = max(chart_data.values()) if chart_data.values() else 1
            for label, value in chart_data.items():
                bar_length = int((value / max_value) * 20)
                bar = "█" * bar_length
                lines.append(f"{label:15} │{bar:20} {value}")

        lines.extend(["", "---", ""])

    # 报告结尾
    lines.extend([
        "",
        "---",
        "",
        f"**📄 报告生成**: {timestamp}",
        f"**🔧 生成工具**: 智能商务出差分析系统",
        "",
        "*本报告基于实时数据生成，建议在出行前再次确认相关信息*"
    ])

    return "\n".join(lines)


def _generate_bar_chart(data: List[Union[int, float]], labels: Optional[List[str]], title: Optional[str]) -> str:
    """生成文本柱状图"""

    lines = []

    if title:
        lines.extend([
            f"### 📊 {title}",
            "",
            "```",
        ])
    else:
        lines.append("```")

    if not data:
        lines.extend(["暂无数据", "```"])
        return "\n".join(lines)

    max_value = max(data)
    max_bar_length = 30

    for i, value in enumerate(data):
        label = labels[i] if labels and i < len(labels) else f"项目{i+1}"
        bar_length = int((value / max_value) *
                         max_bar_length) if max_value > 0 else 0
        bar = "█" * bar_length

        # 格式化数值
        if isinstance(value, float):
            value_str = f"{value:.2f}"
        else:
            value_str = str(value)

        lines.append(f"{label:12} │{bar:<30} {value_str}")

    lines.append("```")
    return "\n".join(lines)


def _generate_pie_chart(data: List[Union[int, float]], labels: Optional[List[str]], title: Optional[str]) -> str:
    """生成文本饼图"""

    lines = []

    if title:
        lines.extend([
            f"### 🥧 {title}",
            "",
            "```",
        ])
    else:
        lines.append("```")

    if not data:
        lines.extend(["暂无数据", "```"])
        return "\n".join(lines)

    total = sum(data)
    pie_chars = ["█", "▓", "▒", "░", "▪", "▫", "◆", "◇", "●", "○"]

    for i, value in enumerate(data):
        label = labels[i] if labels and i < len(labels) else f"项目{i+1}"
        percentage = (value / total) * 100 if total > 0 else 0
        char = pie_chars[i % len(pie_chars)]

        # 格式化数值
        if isinstance(value, float):
            value_str = f"{value:.2f}"
        else:
            value_str = str(value)

        lines.append(f"{char} {label:12} {value_str:>8} ({percentage:5.1f}%)")

    lines.append("```")
    return "\n".join(lines)


def _generate_line_chart(data: List[Union[int, float]], labels: Optional[List[str]], title: Optional[str]) -> str:
    """生成文本折线图"""

    lines = []

    if title:
        lines.extend([
            f"### 📈 {title}",
            "",
            "```",
        ])
    else:
        lines.append("```")

    if not data:
        lines.extend(["暂无数据", "```"])
        return "\n".join(lines)

    # 简化的折线图显示
    max_value = max(data)
    min_value = min(data)
    height = 10  # 图表高度

    # 归一化数据
    if max_value != min_value:
        normalized_data = [(value - min_value) /
                           (max_value - min_value) * height for value in data]
    else:
        normalized_data = [height // 2] * len(data)

    # 生成图表
    for y in range(height, -1, -1):
        line = ""
        for x, norm_value in enumerate(normalized_data):
            if abs(norm_value - y) < 0.5:
                line += "●"
            elif y == 0:
                line += "─"
            else:
                line += " "

        # 添加Y轴标签
        if max_value != min_value:
            y_value = min_value + (y / height) * (max_value - min_value)
            lines.append(f"{y_value:6.1f} │{line}")
        else:
            lines.append(f"{max_value:6.1f} │{line}")

    # 添加X轴标签
    if labels:
        x_labels = "       │"
        for label in labels[:len(data)]:
            x_labels += label[0] if label else "?"
        lines.append(x_labels)

    lines.append("```")
    return "\n".join(lines)
