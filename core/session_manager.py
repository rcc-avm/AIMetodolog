"""
Менеджер сессии: хранит состояние проекта.
"""

import json
import os
from datetime import datetime

class SessionManager:
    """
    Управляет состоянием сессии: диалог, структура, ячейки.
    """
    
    def __init__(self, generation_mode=None):
        """
        Инициализация менеджера сессии.
        
        Args:
            generation_mode: Режим генерации (full/sections/subsections)
        """
        import config
        
        # Основные данные
        self.summarized_dialog = ""
        self.lesson_structure = ""
        self.generation_mode = generation_mode or config.DEFAULT_GENERATION_MODE
        
        # Накопленные ячейки
        self.cells = []
        
        # Директории
        self.output_dir = config.OUTPUT_DIR
        self.log_dir = config.LOG_DIR
        
        # Метаданные
        self.created_at = datetime.now()
        self.session_id = f"session_{self.created_at.strftime('%Y%m%d_%H%M%S')}"
    
    def add_cells(self, new_cells):
        """
        Добавляет ячейки в сессию.
        
        Args:
            new_cells: Список или словарь с ячейками
        """
        if isinstance(new_cells, list):
            self.cells.extend(new_cells)
            print(f"📝 Добавлено {len(new_cells)} ячеек. Всего: {len(self.cells)}")
        elif isinstance(new_cells, dict):
            self.cells.append(new_cells)
            print(f"📝 Добавлена 1 ячейка. Всего: {len(self.cells)}")
    
    def clear_cells(self):
        """Очищает все ячейки."""
        self.cells = []
        print("🗑️  Все ячейки очищены")
    
    def save_session(self, filename=None):
        """
        Сохраняет сессию в JSON файл.
        
        Returns:
            str: Путь к сохраненному файлу или None при ошибке
        """
        if filename is None:
            filename = f"{self.session_id}.json"
        
        session_data = {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "generation_mode": self.generation_mode,
            "summarized_dialog": self.summarized_dialog,
            "lesson_structure": self.lesson_structure,
            "cells_count": len(self.cells)
        }
        
        os.makedirs(self.output_dir, exist_ok=True)
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
            
            print(f"💾 Сессия сохранена: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ Ошибка сохранения сессии: {e}")
            return None