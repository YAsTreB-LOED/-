# Ревьюрирование программных модулей (Производственная практика в Малленом Системс)

## Описание
Проект для первой недели практики: разработка модулей обработки изображений (Python, PyQt6, Pillow). Включает UI и обработку, логирование, тесты, историю действий.

## Структура
- **Docs/**: Документы практики (методичка, задание, аттестация).
- **Report/**: Отчёт с диаграммами, картинками, разделами.
- **Src/**: Исходный код (main.py, image_processor.py, tests/).
- **README.md**: Это файл.

## Установка
1. `pip install -r Src/requirements.txt`
2. `python Src/main.py`

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