"""
Утилиты для определения платформы и абстракции от среды выполнения.
"""

import os
import sys
import subprocess

def is_colab():
    """
    Определяет, выполняется ли код в Google Colab.
    
    Returns:
        bool: True если в Colab, иначе False.
    """
    return 'COLAB_GPU' in os.environ

def get_secret(key, default=None):
    """
    Получает секретное значение из переменных окружения или Colab userdata.
    
    Args:
        key (str): Ключ секрета.
        default: Значение по умолчанию, если секрет не найден.
    
    Returns:
        Значение секрета или default.
    """
    # Сначала пробуем переменные окружения
    value = os.environ.get(key)
    if value:
        return value
    
    # Если в Colab, пробуем получить из userdata
    if is_colab():
        try:
            from google.colab import userdata
            return userdata.get(key)
        except (ImportError, userdata.SecretNotFoundError):
            pass
    
    return default

def install_packages(packages):
    """
    Устанавливает пакеты в зависимости от платформы.
    
    Args:
        packages (list): Список пакетов для установки.
    """
    if is_colab():
        # В Colab используем !pip
        import IPython
        for pkg in packages:
            IPython.get_ipython().system(f'pip -q install {pkg}')
    else:
        # Локально используем subprocess
        for pkg in packages:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

def get_project_root():
    """
    Возвращает путь к корню проекта в зависимости от платформы.
    
    Returns:
        str: Абсолютный путь к корню проекта.
    """
    if is_colab():
        # В Colab проект клонируется в /content
        return '/content/aimetodolog'
    else:
        # Локально - текущая директория или родительская от этого файла
        return os.path.dirname(os.path.abspath(__file__))

def setup_environment():
    """
    Настраивает переменные окружения для корректной работы в обеих средах.
    """
    # Устанавливаем кодировку
    os.environ['PYTHONUTF8'] = '1'
    os.environ['LANG'] = 'en_US.UTF-8'
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    # Проверяем API ключ (больше не устанавливаем в окружение, чтобы не раскрывать ключ)
    api_key = get_secret('OPENROUTER_API_KEY')
    if api_key:
        print(f"✅ API ключ OpenRouter доступен ({len(api_key)} символов)")
        # Ключ уже загружен из .env или Colab секретов, не устанавливаем в окружение
    else:
        print("⚠️  API ключ OpenRouter не найден")
        print("   Установите переменную окружения OPENROUTER_API_KEY")
        if is_colab():
            print("   или добавьте в 'Секреты' Colab с именем OPENROUTER_API_KEY")
    
    # Создаем необходимые директории
    from config import LOG_DIR, OUTPUT_DIR, PROJECT_DIR
    for directory in [LOG_DIR, OUTPUT_DIR, PROJECT_DIR]:
        os.makedirs(directory, exist_ok=True)
    
    return api_key is not None

if __name__ == "__main__":
    # Тестируем функции
    print(f"Running in Colab: {is_colab()}")
    print(f"Project root: {get_project_root()}")
    print(f"Secret test: {get_secret('OPENROUTER_API_KEY', 'Not found')}")
