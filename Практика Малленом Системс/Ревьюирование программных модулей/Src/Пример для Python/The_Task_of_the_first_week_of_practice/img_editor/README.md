# Ревьюрирование программных модулей (Производственная практика в Малленом Системс)

# Утилита работы с изображениями

## Описание проекта
Этот проект представляет собой простую утилиту для редактирования изображений, реализованную на Python. Она соответствует "Проекту 1" из задания: поддерживает изменение яркости, контраста, размера изображения, получение информации о файле и сохранение в другом формате.

Проект разделён на два модуля:
- **image_processor.py**: Модуль обработки изображений (библиотека).
- **main.py**: Модуль взаимодействия с пользователем (UI на PyQt6).

Дополнительные функции:
- Логирование операций в `logs/app.log`.
- История действий в `history.json`.
- Сохранение настроек в `configs/settings.ini`.
- Unit-тесты в `tests/test_image_processor.py`.
- Автосоздание папок: logs, configs, output.

Требования:
- Python 3.8+
- Pillow
- PyQt6
- pytest (для тестов)

Установка:
1. `pip install -r requirements.txt`
Запуск:
2. `python main.py`
Запуск тестов:
3. `pytest -v`

## Документация
### UML-диаграмма
```mermaid
classDiagram
 class ImageProcessor {
     +original_image: Image
     +current_image: Image
     +original_format: str
     +history: list
     +load_image(path: str) : tuple[bool, str]
     +get_info() : dict
     +adjust_brightness(factor: float)
     +adjust_contrast(factor: float)
     +resize(width: int, height: int)
     +reset()
     +save(path: str) : tuple[bool, str]
 }
 class ImageEditor {
     +processor: ImageProcessor
     +brightness: QSlider
     +contrast: QSlider
     +w_spin: QSpinBox
     +h_spin: QSpinBox
     +keep_aspect: QCheckBox
     +load_image()
     +save_image()
     +reset_image()
     +apply_all_changes()
     +display_current_image()
 }
 ImageEditor --o ImageProcessor : uses