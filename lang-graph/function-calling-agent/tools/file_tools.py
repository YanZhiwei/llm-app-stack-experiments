"""
文件操作工具 - 读写文件和目录操作
"""

from langchain_core.tools import tool
import os


@tool
def write_file(filename: str, content: str) -> str:
    """将内容写入文件"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"成功将内容写入文件: {filename}"
    except Exception as e:
        return f"写入文件失败: {str(e)}"


@tool
def read_file(filename: str) -> str:
    """读取文件内容"""
    try:
        if not os.path.exists(filename):
            return f"文件不存在: {filename}"
        
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 如果文件太大，只返回前1000个字符
        if len(content) > 1000:
            return f"文件内容 (前1000字符): {content[:1000]}...\n\n文件总长度: {len(content)} 字符"
        else:
            return f"文件内容: {content}"
    except Exception as e:
        return f"读取文件失败: {str(e)}"


@tool
def list_files(directory: str = ".") -> str:
    """列出指定目录下的文件和文件夹"""
    try:
        if not os.path.exists(directory):
            return f"目录不存在: {directory}"
        
        items = []
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isdir(item_path):
                items.append(f"📁 {item}/")
            else:
                size = os.path.getsize(item_path)
                items.append(f"📄 {item} ({size} bytes)")
        
        return f"目录 '{directory}' 的内容:\n" + "\n".join(items)
    except Exception as e:
        return f"列出文件失败: {str(e)}" 