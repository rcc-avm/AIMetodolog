"""
Скрипт для очистки директории логов.
Автономный скрипт, который удаляет все файлы в директории logs.
"""

import os
import shutil
import sys

def clear_logs(force=False):
    """
    Очищает директорию logs.
    
    Args:
        force: Если True, не запрашивает подтверждение
    
    Returns:
        bool: True если успешно, False если отменено или ошибка
    """
    try:
        # Импортируем конфигурацию для получения пути к логам
        import config
        
        log_dir = config.LOG_DIR
        
        # Проверяем существование директории
        if not os.path.exists(log_dir):
            print(f"Директория логов не существует: {log_dir}")
            return False
        
        # Получаем список файлов
        files = []
        for root, dirs, filenames in os.walk(log_dir):
            for filename in filenames:
                files.append(os.path.join(root, filename))
        
        if not files:
            print("В директории логов нет файлов.")
            return True
        
        # Выводим информацию о файлах
        print(f"Найдено файлов в логах: {len(files)}")
        print("Примеры файлов:")
        for i, file in enumerate(files[:5]):
            print(f"  {os.path.basename(file)}")
        if len(files) > 5:
            print(f"  ... и еще {len(files) - 5} файлов")
        
        # Запрос подтверждения (если не forced)
        if not force:
            response = input(f"\nВы уверены, что хотите удалить все файлы в {log_dir}? (yes/no): ").strip().lower()
            if response not in ['yes', 'y', 'да', 'д']:
                print("Очистка отменена.")
                return False
        
        # Удаляем файлы
        deleted_count = 0
        for file in files:
            try:
                os.remove(file)
                deleted_count += 1
            except Exception as e:
                print(f"Ошибка при удалении {file}: {e}")
        
        print(f"\n✅ Удалено файлов: {deleted_count} из {len(files)}")
        
        # Проверяем, остались ли файлы
        remaining_files = []
        for root, dirs, filenames in os.walk(log_dir):
            for filename in filenames:
                remaining_files.append(os.path.join(root, filename))
        
        if remaining_files:
            print(f"⚠️  Осталось файлов: {len(remaining_files)} (возможно, системные или скрытые)")
            return False
        else:
            print("✅ Директория логов полностью очищена.")
            return True
            
    except ImportError:
        print("❌ Не удалось импортировать config. Убедитесь, что скрипт запускается из корня проекта.")
        return False
    except Exception as e:
        print(f"❌ Неизвестная ошибка: {e}")
        return False

def main():
    """Основная функция скрипта."""
    print("\n" + "=" * 60)
    print("ОЧИСТКА ДИРЕКТОРИИ ЛОГОВ")
    print("=" * 60)
    
    # Проверяем аргументы командной строки
    force = False
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-f', '--force']:
            force = True
            print("Режим принудительной очистки (без подтверждения)")
        elif sys.argv[1] in ['-h', '--help']:
            print("Использование: python clear_logs.py [опции]")
            print("Опции:")
            print("  -f, --force   Принудительная очистка без подтверждения")
            print("  -h, --help    Показать эту справку")
            return
    
    success = clear_logs(force=force)
    
    if success:
        print("\n✅ Очистка завершена успешно.")
    else:
        print("\n❌ Очистка не удалась или была отменена.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
