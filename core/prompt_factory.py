"""
Фабрика промптов для разных режимов генерации.
"""

class PromptFactory:
    """
    Создает промпты для LLM в зависимости от режима генерации.
    """
    
    MODES = {
        'full': 'Генерация занятия целиком',
        'sections': 'По разделам 1 уровня',
        'subsections': 'По подразделам'
    }
    
    def __init__(self, session_manager):
        """
        Инициализация фабрики промптов.
        
        Args:
            session_manager: Экземпляр SessionManager
        """
        self.session = session_manager
    
    def get_prompt(self, target_section=None):
        """
        Возвращает system_prompt и user_prompt для заданного раздела.
        
        Args:
            target_section: Название раздела (None для режима 'full')
        
        Returns:
            tuple: (system_prompt, user_prompt)
        """
        mode = self.session.generation_mode
        
        if mode not in self.MODES:
            raise ValueError(f"Неизвестный режим: {mode}. Допустимо: {list(self.MODES.keys())}")
        
        # Базовый system_prompt
        base_system = """Ты — опытный создатель уроков по теме занятия для Google Colab.
Твоя задача — создать качественный, практический и понятный материал.

ВАЖНЫЕ ПРАВИЛА:
1. ВСЕГДА создавай подробные комментарии к каждой строке кода.
2. Код на Python размещай ТОЛЬКО в ячейках типа "code".
3. Вывод должен быть ТОЛЬКО в виде валидного JSON для .ipynb файла.

КОНТЕКСТ УРОКА:
{context}

СТРУКТУРА ВСЕГО ЗАНЯТИЯ:
{structure}

{instruction}"""
        
        # Подготавливаем контекст (ограничиваем длину)
        context = self.session.summarized_dialog[:800] + ("..." if len(self.session.summarized_dialog) > 800 else "")
        structure = self.session.lesson_structure[:400] + ("..." if len(self.session.lesson_structure) > 400 else "")
        
        # Инструкция в зависимости от режима
        if mode == 'full':
            instruction = "ИНСТРУКЦИЯ: Сгенерируй ВЕСЬ материал занятия одним JSON-объектом. Включи все разделы из структуры выше."
            user_prompt = "Сгенерируй полный Jupyter Notebook для всего занятия, включая все разделы из структуры."
            
        elif mode == 'sections':
            if not target_section:
                raise ValueError("Для режима 'sections' необходимо указать target_section")
            
            instruction = f"ИНСТРУКЦИЯ: Сгенерируй материал ТОЛЬКО для РАЗДЕЛА: '{target_section}'. Не затрагивай другие разделы."
            user_prompt = f"Сгенерируй материал для раздела: '{target_section}'."
            
        elif mode == 'subsections':
            if not target_section:
                raise ValueError("Для режима 'subsections' необходимо указать target_section")
            
            instruction = f"ИНСТРУКЦИЯ: Сгенерируй материал ТОЛЬКО для ПОДРАЗДЕЛА: '{target_section}'. Будь максимально детальным."
            user_prompt = f"Сгенерируй детализированный материал для подраздела: '{target_section}'."
        
        # Собираем финальный промпт
        system_prompt = base_system.format(
            context=context,
            structure=structure,
            instruction=instruction
        )
        
        return system_prompt, user_prompt