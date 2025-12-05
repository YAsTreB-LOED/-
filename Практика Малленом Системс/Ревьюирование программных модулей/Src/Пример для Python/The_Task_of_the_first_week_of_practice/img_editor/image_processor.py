# image_processor.py
import logging
from pathlib import Path
from typing import Tuple, Optional
from PIL import Image, ImageEnhance
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class ImageProcessor:
    def __init__(self):
        self.original_image: Optional[Image.Image] = None
        self.current_image: Optional[Image.Image] = None
        self.original_format = "Unknown"
        self.history = []
        self.history_path = Path("history.json")
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        Path("logs").mkdir(exist_ok=True)
        self._load_history()

    def _log_action(self, action: str, params: dict):
        entry = {"timestamp": datetime.now().isoformat(), "action": action, "params": params}
        self.history.append(entry)
        self.history_path.write_text(json.dumps(self.history, ensure_ascii=False, indent=2), encoding="utf-8")

    def _load_history(self):
        if self.history_path.exists():
            try:
                self.history = json.loads(self.history_path.read_text(encoding="utf-8"))
            except:
                self.history = []

    def load_image(self, path: str) -> Tuple[bool, str]:
        try:
            img = Image.open(path)
            self.original_format = img.format or "Unknown"  # сохраняем формат
            
            img = img.convert("RGB")  # конвертируем
            
            self.original_image = img.copy()
            self.current_image = img.copy()
            
            self._log_action("load_image", {"path": str(path), "format": self.original_format})
            return True, "Изображение успешно загружено"
        except Exception as e:
            logger.error(f"Ошибка загрузки изображения {path}: {e}")
            return False, f"Не удалось открыть файл:\n{e}"

    def get_info(self) -> dict:
        if not self.current_image:
            return {}
        w, h = self.current_image.size
        return {
            "width": w,
            "height": h,
            "format": self.original_format  # ← теперь правильно
        }

    def adjust_brightness(self, factor: float):
        if not self.current_image: return
        enhancer = ImageEnhance.Brightness(self.current_image)
        self.current_image = enhancer.enhance(factor)
        self._log_action("brightness", {"factor": factor})

    def adjust_contrast(self, factor: float):
        if not self.current_image: return
        enhancer = ImageEnhance.Contrast(self.current_image)
        self.current_image = enhancer.enhance(factor)
        self._log_action("contrast", {"factor": factor})

    def resize(self, width: int, height: int):
        if not self.current_image: return
        if width <= 0 or height <= 0:
            return  # защита от нулевых размеров
        self.current_image = self.current_image.resize((width, height), Image.Resampling.LANCZOS)
        self._log_action("resize", {"width": width, "height": height})

    def reset(self):
        if self.original_image:
            self.current_image = self.original_image.copy()
            self._log_action("reset", {})

    def save(self, path: str) -> Tuple[bool, str]:
        try:
            self.current_image.save(path)
            self._log_action("save", {"path": str(path)})
            return True, f"Сохранено: {path}"
        except Exception as e:
            return False, f"Ошибка сохранения: {e}"