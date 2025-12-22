"""
Функции для версионирования и сохранения проекта в Google Drive.
Поддерживает как Google Colab, так и локальное выполнение.
"""

import os
import shutil
import json
from datetime import datetime

def is_colab():
    """
    Определяет, выполняется ли код в Google Colab.
    """
    return 'COLAB_GPU' in os.environ

def mount_google_drive():
    """
    Монтирует Google Drive в Colab.
    Возвращает путь к Drive или None при ошибке.
    """
    if not is_colab():
        print("ℹ️  Функция mount_google_drive доступна только в Google Colab")
        return None
    
    try:
        from google.colab import drive
        drive.mount('/content/drive', force_remount=False)
        return '/content/drive/MyDrive'
    except ImportError:
        print("⚠️  Модуль google.colab не доступен")
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
    Сохраняет текущую версию проекта в Google Drive (только в Colab).
    В локальном режиме сохраняет в локальную директорию drive_backup.
    
    Args:
        project_path: Путь к исходному проекту
        drive_base_path: Базовая директория в Drive (для Colab) или локальный путь
        version: Номер версии (None для автоопределения)
    
    Returns:
        str: Путь к сохраненной версии или None при ошибке
    """
    if not is_colab():
        # В локальном режиме используем локальную директорию для бекапа
        local_backup_dir = os.path.join(os.path.dirname(project_path), 'drive_backup')
        drive_base_path = local_backup_dir
        print(f"ℹ️  Локальный режим: сохранение в {drive_base_path}")
    
    print(f"💾 Сохранение версии проекта из: {project_path}")
    
    # Создаем базовую директорию
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
            "files_count": sum([len(files) for r, d, files in os.walk(target_path)]),
            "environment": "Colab" if is_colab() else "Local"
        }
        
        metadata_file = os.path.join(target_path, "version_metadata.json")
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Проект сохранен в: {target_path}")
        print(f"   Файлов: {metadata['files_count']}")
        print(f"   Среда: {metadata['environment']}")
        
        return target_path
        
    except Exception as e:
        print(f"❌ Ошибка сохранения версии: {e}")
        return None
