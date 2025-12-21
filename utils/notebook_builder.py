"""
Сборка Jupyter Notebook из ячеек.
"""

import json
import os

def build_and_save_notebook(cells, output_dir, filename):
    """
    Создаёт ноутбук из списка ячеек и сохраняет его.
    
    Args:
        cells (list): Список ячеек ноутбука
        output_dir (str): Директория для сохранения
        filename (str): Имя файла
    
    Returns:
        str: Путь к сохранённому файлу
    """
    # Полная структура ноутбука
    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.10.12"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }
    
    # Создаем директорию
    os.makedirs(output_dir, exist_ok=True)
    
    # Формируем полный путь
    if not filename.endswith('.ipynb'):
        filename += '.ipynb'
    
    filepath = os.path.join(output_dir, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(notebook, f, ensure_ascii=False, indent=2)
        
        return filepath
        
    except Exception as e:
        print(f"❌ Ошибка сохранения ноутбука: {e}")
        return None