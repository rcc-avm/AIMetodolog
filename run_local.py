#!/usr/bin/env python3
"""
Скрипт для локального запуска AIMetodolog.
Запускает основной рабочий процесс в консольном режиме.
"""

import os
import sys

# Добавляем текущую директорию в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Основная функция локального запуска."""
    print("🚀 Локальный запуск AIMetodolog")
    print("=" * 60)
    
    # Проверяем наличие .env файла
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file):
        print(f"✅ Найден файл конфигурации: {env_file}")
        # Загружаем переменные из .env
        from dotenv import load_dotenv
        load_dotenv(env_file)
    else:
        print(f"⚠️  Файл конфигурации .env не найден")
        print("   Создайте .env на основе .env.template")
    
    # Проверяем API ключ
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_API_KEY не установлен")
        print("   Установите API ключ в переменных окружения или в .env файле")
        sys.exit(1)
    
    # Импортируем и запускаем основной рабочий процесс
    try:
        from main import main_workflow
        print("✅ Модули загружены, запуск рабочего процесса...")
        print("-" * 60)
        main_workflow()
    except Exception as e:
        print(f"❌ Ошибка при запуске: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
