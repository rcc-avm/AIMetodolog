"""
Вспомогательные функции для проекта.
Функции диалога, форматирования текста, логирования.
"""

import textwrap
import os
from datetime import datetime

def format_text(text, width=None):
    """Форматирует текст для красивого вывода."""
    if width is None:
        width = 120
    
    lines = str(text).split('\n')
    formatted_lines = []
    
    for line in lines:
        if line.strip() == '':
            formatted_lines.append('')
        else:
            wrapped = textwrap.fill(line, width=width)
            formatted_lines.append(wrapped)
    
    return '\n'.join(formatted_lines)

def text_to_list_lines(text):
    """Преобразует текст в список непустых строк."""
    lines_list = text.split("\n")
    return [line for line in lines_list if line.strip() != '']

def log_to_file(content, prefix="log", log_dir=None):
    """Логирует содержимое в файл для отладки."""
    if log_dir is None:
        import config
        log_dir = config.LOG_DIR
    
    os.makedirs(log_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(log_dir, f"{prefix}_{timestamp}.txt")
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(str(content))
        return filename
    except Exception as e:
        print(f"⚠️ Ошибка записи лога: {e}")
        return None

def print_header(title, width=80):
    """Печатает заголовок секции в красивом формате."""
    print("\n" + "=" * width)
    print(f" {title} ".center(width, '='))
    print("=" * width)