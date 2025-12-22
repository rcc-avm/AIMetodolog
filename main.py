"""
Основной модуль проекта AIMetodolog.
Содержит главный рабочий процесс для генерации учебных материалов.
"""

import sys
import os

# Добавляем текущую директорию в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from utils.helpers import format_text, text_to_list_lines, log_to_file, print_header
from core.session_manager import SessionManager
from core.prompt_factory import PromptFactory
from llm.client import get_llm_response
from llm.output_processor import extract_and_repair_json
from utils.structure_parser import parse_structure
from utils.notebook_builder import build_and_save_notebook

def dialog(questions: str) -> str:
    """
    Функция диалога (вопрос-ответ) и сохранение.

    Args:
        questions: вопросы для диалога, каждый вопрос с новой строки

    Returns:
        str: форматированная история диалога
    """
    questions_list = text_to_list_lines(questions)
    dialog_str = ''

    for i, question in enumerate(questions_list, 1):
        formatted_question = format_text(f"Вопрос {i}: {question}")
        print(formatted_question, '\n')
        answer = input("Ваш ответ: ")
        formatted_answer = format_text(f"Ответ: {answer}")
        print()
        dialog_str += f"{formatted_question}\n\n{formatted_answer}\n\n"

    # Логируем диалог
    log_to_file(dialog_str, "user_dialog")

    return dialog_str

def main_workflow():
    """Основной рабочий процесс генерации занятия."""

    print_header("НЕЙРО-МЕТОДОЛОГ (модульная версия)")

    # 1. Инициализация сессии
    session = SessionManager(generation_mode=config.DEFAULT_GENERATION_MODE)
    print(f"🆕 Создана сессия: режим '{session.generation_mode}'")

    # 2. Ввод данных пользователя
    print_header("1. Ввод данных пользователя")

    initial_questions = """
1. Какая у Вас будет основная тема занятия(Общая тема: Физика, тема занятия: Закон Архимеда)?
2. Какой у Вас уровень подготовки? (начинающий, средний, продвинутый, начальный (5-7 класс), средний (8-9 класс), продвинутый (10-11 класс), университетский)?
3. Какоя предполагается продолжительность занятия (15 минут, 45 минут, 1 час, 2 часа)?
4. Какими предварительными знаниями и навыками обладают обучаемые в данной теме (никакими, начальными, работаю в данной сфере, являюсь специалистом)?
5. С какой целью хотите изучить занятие(урок в школе, занятие факультатива, лекция на курсе, для самостоятельного самообразования, для профессиональной подготовки, для совершенствования в профессии)?
6. Укажите дополнительные пожелания к занятию: """

    session.summarized_dialog = dialog(initial_questions)
    print(f"💬 Длина диалога: {len(session.summarized_dialog)} символов")

    # 3. Генерация структуры занятия
    print_header("2. Генерация структуры занятия")

    # Создаем промпт для генерации структуры
    structure_system_prompt = """Ты опытный создатель уроков по теме занятия.
Ты должен проанализировать ответы студента на вопросы и создать структуру занятия.
Структура должна включать теоретическую, практическую часть и домашнее задание.
Выведи структуру в формате:
1. Теоретическая часть
   1.1. [название подраздела]
   1.2. [название подраздела]
2. Практическая часть
   2.1. [название подраздела]
   2.2. [название подраздела]
3. Домашнее задание
   3.1. [название подраздела]

Не добавляй никаких дополнительных пояснений, только структуру."""

    structure_user_prompt = f"""Ответы студента: {session.summarized_dialog}

На основе этих ответов создай структуру занятия по теме занятия.
Создай структуру из 3-4 подразделов в каждом основном разделе."""

    print("🧠 Генерация структуры занятия...")

    structure_messages = [
        {"role": "system", "content": structure_system_prompt},
        {"role": "user", "content": structure_user_prompt}
    ]

    structure_raw, structure_time, _ = get_llm_response(
        messages=structure_messages,
        model=config.DEFAULT_MODEL,
        max_tokens=2000
    )

    session.lesson_structure = structure_raw
    print(f"✅ Структура сгенерирована за {structure_time:.2f} сек.")
    print(f"\n📋 Структура занятия:\n{format_text(structure_raw)}")

    # Логируем структуру
    log_to_file(structure_raw, "lesson_structure")

    # 4. Согласование структуры (опционально)
    print_header("3. Согласование структуры")

    need_changes = input("\nХотите внести изменения в структуру? (y/n): ").strip().lower()

    if need_changes in ['y', 'yes', 'да', 'д']:
        changes = input("Опишите изменения: ")

        # Генерация обновленной структуры
        update_system_prompt = """Ты опытный создатель уроков по теме занятия.
Ты должен обновить структуру занятия с учетом пожеланий пользователя."""

        update_user_prompt = f"""Исходная структура: {session.lesson_structure}
Пожелания студента: {changes}
Обнови структуру с учетом пожеланий. Сохрани тот же формат."""

        update_messages = [
            {"role": "system", "content": update_system_prompt},
            {"role": "user", "content": update_user_prompt}
        ]

        updated_structure, update_time, _ = get_llm_response(
            messages=update_messages,
            model=config.DEFAULT_MODEL,
            max_tokens=2000
        )

        session.lesson_structure = updated_structure
        print(f"✅ Структура обновлена за {update_time:.2f} сек.")
        print(f"\n📋 Обновленная структура:\n{format_text(updated_structure)}")

    # 5. Генерация материалов занятия
    print_header("4. Генерация материалов занятия")

    # Инициализируем фабрику промптов
    factory = PromptFactory(session)

    # В зависимости от режима определяем цели генерации
    if session.generation_mode == 'full':
        print("🎯 РЕЖИМ 'FULL': Генерация всего занятия одним запросом")
        # В режиме 'full' цель - вся структура целиком
        generation_targets = [None]  # None означает "весь урок"
        print("   Будет выполнен ОДИН запрос на весь урок")
    else:
        # В режимах 'sections' или 'subsections' парсим структуру
        generation_targets = parse_structure(session.lesson_structure)
        print(f"🎯 РЕЖИМ '{session.generation_mode.upper()}': Генерация по частям")
        print(f"   Будет сгенерировано {len(generation_targets)} разделов")

    # Очищаем ячейки (начинаем с чистого листа)
    session.clear_cells()

    # Цикл генерации
    for i, target in enumerate(generation_targets, 1):
        if session.generation_mode == 'full':
            print(f"\n🔨 Генерация ВСЕГО занятия (запрос {i}/{len(generation_targets)})")
            section_title_display = "ВЕСЬ УРОК"
        else:
            print(f"\n🔨 Генерация раздела {i}/{len(generation_targets)}: {target}")
            section_title_display = target

        # Получаем промпт (для режима 'full' target=None)
        system_prompt, user_prompt = factory.get_prompt(target)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        # Настраиваем параметры запроса в зависимости от режима
        if session.generation_mode == 'full':
            # Для полной генерации увеличиваем лимит токенов
            current_max_tokens = 8000
            current_temperature = 0.7
        else:
            current_max_tokens = 4000
            current_temperature = 0.7

        # Отправляем запрос к LLM
        print(f"   Параметры: max_tokens={current_max_tokens}, temperature={current_temperature}")
        raw_output, gen_time, _ = get_llm_response(
            messages=messages,
            model=config.DEFAULT_MODEL,
            temperature=current_temperature,
            max_tokens=current_max_tokens
        )

        print(f"   ⏱️  Время генерации: {gen_time:.2f} сек.")

        # Логируем сырой ответ
        log_prefix = "full_lesson" if session.generation_mode == 'full' else f"section_{i}"
        log_to_file(raw_output, log_prefix)

        # Обрабатываем вывод LLM (извлекаем JSON)
        try:
            json_content = extract_and_repair_json(raw_output)

            if 'cells' in json_content:
                session.add_cells(json_content['cells'])
                cell_count = len(json_content['cells'])
                print(f"   ✅ Добавлено {cell_count} ячеек")

                # Для отладки показываем типы ячеек
                cell_types = {}
                for cell in json_content['cells']:
                    cell_type = cell.get('cell_type', 'unknown')
                    cell_types[cell_type] = cell_types.get(cell_type, 0) + 1
                print(f"   📊 Типы ячеек: {cell_types}")
            else:
                print(f"   ⚠️  В ответе нет ячеек (cells)")

        except Exception as e:
            print(f"   ❌ Ошибка обработки JSON: {e}")

    # После цикла выводим статистику
    print(f"\n📈 ИТОГИ ГЕНЕРАЦИИ:")
    print(f"   Режим: {session.generation_mode}")
    print(f"   Всего ячеек: {len(session.cells)}")
    if session.generation_mode == 'full':
        print(f"   Запросов к LLM: 1 (экономия токенов)")
    else:
        print(f"   Запросов к LLM: {len(generation_targets)}")

    # 6. Сборка финального ноутбука
    print_header("5. Сборка финального ноутбука")

    if len(session.cells) == 0:
        print("❌ Нет ячеек для сборки ноутбука")
        return

    notebook_name = input("Введите имя для итогового ноутбука (без .ipynb): ").strip()
    if not notebook_name:
        notebook_name = "generated_lesson"

    notebook_filename = f"{notebook_name}.ipynb"

    # Собираем ноутбук
    notebook_path = build_and_save_notebook(
        cells=session.cells,
        output_dir=session.output_dir,
        filename=notebook_filename
    )

    if notebook_path and os.path.exists(notebook_path):
        print(f"\n🎉 Ноутбук успешно создан!")
        print(f"📁 Путь: {notebook_path}")
        print(f"📊 Ячеек: {len(session.cells)}")

        # Показываем размер файла
        file_size = os.path.getsize(notebook_path)
        print(f"💾 Размер: {file_size / 1024:.1f} KB")

        # Предложение открыть ноутбук
        print("\nВы можете открыть ноутбук в Colab:")
        print(f"  from google.colab import files")
        print(f"  files.download('{notebook_path}')")
    else:
        print("❌ Не удалось создать ноутбук")

    print_header("РАБОТА ЗАВЕРШЕНА")


if __name__ == "__main__":
    try:
        main_workflow()
    except KeyboardInterrupt:
        print("\n\n⚠️  Прервано пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
