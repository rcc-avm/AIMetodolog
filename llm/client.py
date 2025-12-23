"""
Клиент для работы с LLM через OpenRouter.
"""

import os
import time
import json
from datetime import datetime
from openai import OpenAI
from openai import APIConnectionError, APIError, RateLimitError, AuthenticationError

def log_to_file(content, prefix="log", log_dir=None):
    """
    Логирует содержимое в файл для отладки.
    Адаптированная версия из utils.helpers для использования внутри этого модуля.
    """
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

def get_llm_response(messages, model=None, temperature=0.7, max_tokens=4000):
    """
    Отправляет запрос к LLM через OpenRouter.
    
    Args:
        messages: Список сообщений в формате OpenAI
        model: Имя модели (если None, берется из конфига)
        temperature: Температура генерации
        max_tokens: Максимальное количество токенов
    
    Returns:
        tuple: (текст ответа, время выполнения, объект ответа или None при ошибке)
    """
    start_time = time.time()
    
    try:
        # Импортируем конфигурацию
        import config
        
        # Генерируем временную метку для логирования
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Определяем, активен ли любой демо-режим
        is_demo_mode = (config.DEMO_LOCAL or config.DEMO_LOCAL_LLM or 
                        config.DEMO_BIG_LLM or config.DEMO_BIG_LLM_REAL)
        
        # Логируем запрос только в демо-режимах
        if is_demo_mode:
            request_log_filename = log_to_file(
                json.dumps(messages, ensure_ascii=False, indent=2),
                prefix="llm",
                log_dir=config.LOG_DIR
            )
            if request_log_filename:
                print(f"📝 Запрос сохранен (демо-режим): {os.path.basename(request_log_filename)}")
        
        # Получаем модель
        if model is None:
            model = config.DEFAULT_MODEL
        
        # Проверка демо-режимов
        if config.DEMO_LOCAL:
            print("🔧 ДЕМО-РЕЖИМ LOCAL: возвращаем шаблонный ответ")
            # Шаблонный JSON-ответ, который будет обработан как реальный ответ LLM
            demo_answer = '''{
  "cells": [
    {
      "cell_type": "markdown",
      "source": [
        "# Демонстрационный режим (DEMO_LOCAL)",
        "Этот ответ был сгенерирован в демо-режиме без подключения к LLM.",
        "Реальный запрос не отправлялся.",
        "Содержимое данного раздела предназначено для тестирования работоспособности конвейера."
      ]
    },
    {
      "cell_type": "code",
      "source": [
        "# Пример кода из демо-режима\\n",
        "print('Демо-режим: запрос к LLM не выполнялся')\\n",
        "print('Этот код сгенерирован шаблоном')"
      ],
      "execution_count": null,
      "outputs": []
    }
  ]
}'''
            execution_time = time.time() - start_time
            # Логируем ответ
            log_to_file(
                demo_answer,
                prefix="respond",
                log_dir=config.LOG_DIR
            )
            return demo_answer, execution_time, None
            
        elif config.DEMO_LOCAL_LLM:
            print("🔧 ДЕМО-РЕЖИМ LOCAL_LLM: используем заглушку для локальной модели")
            # Пока используем ту же логику, что и для DEMO_BIG_LLM
            # В будущем здесь можно будет подключить локальную модель
            demo_answer = "Ты - мой помошник при тестировании. Ответь только фразой <Ответ от LLM>. От себя ничего не добавляй"
            execution_time = time.time() - start_time
            # Логируем ответ
            log_to_file(
                demo_answer,
                prefix="respond",
                log_dir=config.LOG_DIR
            )
            return demo_answer, execution_time, None
            
        elif config.DEMO_BIG_LLM:
            print("🔧 ДЕМО-РЕЖИМ BIG_LLM: используем тестовый запрос-заглушку")
            # Тестовый запрос-заглушка
            demo_answer = "Ты - мой помошник при тестировании. Ответь только фразой <Ответ от LLM>. От себя ничего не добавляй"
            execution_time = time.time() - start_time
            # Логируем ответ
            log_to_file(
                demo_answer,
                prefix="respond",
                log_dir=config.LOG_DIR
            )
            return demo_answer, execution_time, None
        
        # Проверяем API ключ (только для реального запроса)
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            raise AuthenticationError("API ключ OpenRouter не установлен в переменных окружения")
        
        # Инициализация клиента
        client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            timeout=60.0,
            default_headers={
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "AIMetodist Colab"
            }
        )
        
        # Отправка запроса
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=False
        )
        
        # Извлекаем ответ
        answer = response.choices[0].message.content
        execution_time = time.time() - start_time
        
        # Логируем ответ только в демо-режимах
        if is_demo_mode:
            log_to_file(
                answer,
                prefix="respond",
                log_dir=config.LOG_DIR
            )
        
        return answer, execution_time, response
        
    except AuthenticationError as e:
        error_msg = f"Ошибка аутентификации OpenRouter: {e}. Проверьте API ключ."
        print(f"❌ {error_msg}")
    except RateLimitError as e:
        error_msg = f"Превышен лимит запросов OpenRouter: {e}"
        print(f"⚠️  {error_msg}")
    except APIConnectionError as e:
        error_msg = f"Ошибка соединения с OpenRouter: {e}"
        print(f"🔌 {error_msg}")
    except APIError as e:
        error_msg = f"Ошибка API OpenRouter: {e}"
        print(f"⚠️  {error_msg}")
    except Exception as e:
        # Безопасное формирование сообщения об ошибке
        try:
            error_msg = f"Неизвестная ошибка: {type(e).__name__}: {str(e)}"
        except:
            error_msg = f"Неизвестная ошибка: {type(e).__name__} (не удалось получить детали)"
        print(f"❌ {error_msg}")
    
    # Возвращаем ошибку
    execution_time = time.time() - start_time
    error_response = f'{{"error": "{error_msg}"}}'
    
    # Логируем ошибку как ответ
    try:
        import config
        log_to_file(
            error_response,
            prefix="respond",
            log_dir=config.LOG_DIR
        )
    except:
        pass
    
    return error_response, execution_time, None
