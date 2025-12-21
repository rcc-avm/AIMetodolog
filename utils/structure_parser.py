"""
Парсинг структуры урока.
"""

import re

def parse_structure(lesson_structure, section='all'):
    """
    Парсит текстовую структуру урока.
    
    Args:
        lesson_structure (str): Текстовая структура занятия
        section (str): 'all' - все подразделы
    
    Returns:
        list: Список заголовков подразделов
    """
    # Простой парсинг для начала
    lines = lesson_structure.strip().split('\n')
    sections = []
    
    for line in lines:
        line = line.strip()
        # Ищем подразделы вида "1.1.", "2.3." и т.д.
        if re.match(r'^\d+\.\d+\.', line):
            sections.append(line)
    
    # Если не нашли подразделов, возвращаем тестовые
    if not sections:
        sections = [
            "1.1. Введение в нейронные сети",
            "1.2. Основные понятия и термины",
            "2.1. Первая практическая задача",
            "2.2. Вторая практическая задача",
            "3.1. Домашнее задание"
        ]
    
    return sections