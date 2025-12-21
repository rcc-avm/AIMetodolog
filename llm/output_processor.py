"""
Обработка вывода LLM: извлечение и починка JSON.
"""

import json
import re

def extract_and_repair_json(llm_output):
    """
    Извлекает JSON из ответа LLM и чинит его.
    
    Args:
        llm_output: Сырой вывод от LLM
    
    Returns:
        dict: Распарсенный JSON
    """
    # Если вывод уже содержит ошибку
    if '"error":' in llm_output:
        return {"cells": [{"cell_type": "markdown", "source": [f"# Ошибка\n{llm_output}"]}]}
    
    # Извлекаем JSON из текста
    json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', llm_output, re.DOTALL)
    
    if json_match:
        json_str = json_match.group(1).strip()
    else:
        # Ищем JSON в тексте
        json_str = llm_output.strip()
    
    # Пробуем распарсить
    try:
        result = json.loads(json_str)
        return result
        
    except json.JSONDecodeError:
        # Пробуем починить
        try:
            from json_repair import repair_json
            repaired = repair_json(json_str)
            return repaired
        except:
            # Возвращаем минимальную структуру
            return {
                "cells": [
                    {
                        "cell_type": "markdown",
                        "metadata": {},
                        "source": ["# Сгенерированный раздел", "Контент будет здесь."]
                    }
                ]
            }