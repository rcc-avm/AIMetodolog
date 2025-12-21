"""
Клиент для работы с LLM через OpenRouter.
"""

import os
import time
from openai import OpenAI
from openai import APIConnectionError, APIError, RateLimitError, AuthenticationError

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
        # Получаем модель
        if model is None:
            import config
            model = config.DEFAULT_MODEL
        
        # Проверяем API ключ
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
        error_msg = f"Неизвестная ошибка: {type(e).__name__}: {str(e)}"
        print(f"❌ {error_msg}")
    
    # Возвращаем ошибку
    execution_time = time.time() - start_time
    return f'{{"error": "{error_msg}"}}', execution_time, None