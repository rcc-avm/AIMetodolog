"""
Функции для версионирования и сохранения проекта в Google Drive.
"""

import os
import shutil
import json
from datetime import datetime

def mount_google_drive():
    """
    Монтирует Google Drive в Colab.
    Возвращает путь к Drive или None при ошибке.
    """
    try:
        from google.colab import drive
        drive.mount('/content/drive', force_remount=False)
        return '/content/drive/MyDrive'
    except ImportError:
        print("⚠️  Не в среде Colab или google.colab не доступен")
        return None
    except Exception as e:
        print(f"❌ Ошибка монтирования Google Drive: {e}")
        return None

def get_next_version(base_path, prefix="aimetodolog_v"):
    """
    Определяет следующий номер версии.
    """
    os.makedirs(base_path, exist_ok=True)
    
    existing_versions = []
    for item in os.listdir(base_path):
        if item.startswith(prefix):
            try:
                version_num = int(item[len(prefix):])
                existing_versions.append(version_num)
            except ValueError:
                continue
    
    if not existing_versions:
        next_version = 1
    else:
        next_version = max(existing_versions) + 1
    
    return os.path.join(base_path, f"{prefix}{next_version}")

def save_version_to_drive(project_path, drive_base_path, version=None):
    """
    Сохраняет текущую версию проекта в Google Drive.
    
    Args:
        project_path: Путь к исходному проекту
        drive_base_path: Базовая директория в Drive
        version: Номер версии (None для автоопределения)
    
    Returns:
        str: Путь к сохраненной версии
    """
    print(f"💾 Сохранение версии проекта из: {project_path}")
    
    # Создаем базовую директорию в Drive
    os.makedirs(drive_base_path, exist_ok=True)
    
    # Определяем путь для сохранения
    if version is None:
        target_path = get_next_version(drive_base_path)
    else:
        target_path = os.path.join(drive_base_path, f"aimetodolog_v{version}")
    
    print(f"   Целевой путь: {target_path}")
    
    try:
        # Копируем проект
        if os.path.exists(target_path):
            print(f"   Версия уже существует, перезаписываем...")
            shutil.rmtree(target_path)
        
        # Копируем с сохранением метаданных
        shutil.copytree(
            project_path, 
            target_path,
            ignore=shutil.ignore_patterns('*.pyc', '__pycache__', '.ipynb_checkpoints'),
            dirs_exist_ok=True
        )
        
        # Создаем файл метаданных версии
        metadata = {
            "project_name": "aimetodolog",
            "version": os.path.basename(target_path),
            "saved_at": datetime.now().isoformat(),
            "source_path": project_path,
            "files_count": sum([len(files) for r, d, files in os.walk(target_path)])
        }
        
        metadata_file = os.path.join(target_path, "version_metadata.json")
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Проект сохранен в: {target_path}")
        print(f"   Файлов: {metadata['files_count']}")
        
        return target_path
        
    except Exception as e:
        print(f"❌ Ошибка сохранения версии: {e}")
        return None