# main.py
import sys
from pathlib import Path
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QPixmap, QDragEnterEvent, QDropEvent
from PyQt6.QtCore import Qt, QTimer, QSettings
from image_processor import ImageProcessor
import logging

# === ПУТИ К СЛУЖЕБНЫМ ПАПКАМ ===
BASE_DIR = Path(__file__).parent
LOG_DIR = BASE_DIR / "logs"
CONFIG_DIR = BASE_DIR / "configs"
OUTPUT_DIR = BASE_DIR / "output"

for directory in (LOG_DIR, CONFIG_DIR, OUTPUT_DIR):
    directory.mkdir(exist_ok=True)

# === НАСТРОЙКА ЛОГИРОВАНИЯ ===
logging.basicConfig(
    filename=LOG_DIR / "app.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    encoding="utf-8",
    filemode="a"
)

logger = logging.getLogger("ImageEditor")


class ImageEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Утилита работы с изображениями, практикант: ФИО")
        self.setMinimumSize(1000, 600)

        # Настройки приложения
        self.settings = QSettings(str(CONFIG_DIR / "settings.ini"), QSettings.Format.IniFormat)
        self.restore_geometry()

        self.processor = ImageProcessor()
        self.setAcceptDrops(True)
        self.init_ui()

        # Таймер для плавного обновления
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.apply_all_changes)

        # Восстанавливаем сохранённые параметры
        self.restore_settings()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)

        # === Левая панель ===
        left = QVBoxLayout()
        main_layout.addLayout(left, 1)

        # Кнопки управления
        btns = QGroupBox("Управление")
        bl = QVBoxLayout(btns)

        self.btn_load = QPushButton("Загрузить изображение")
        self.btn_load.clicked.connect(self.load_image)
        bl.addWidget(self.btn_load)

        self.btn_save = QPushButton("Сохранить результат")
        self.btn_save.clicked.connect(self.save_image)
        self.btn_save.setEnabled(False)
        bl.addWidget(self.btn_save)

        self.btn_reset = QPushButton("Сбросить изменения")
        self.btn_reset.clicked.connect(self.reset_image)
        self.btn_reset.setEnabled(False)
        bl.addWidget(self.btn_reset)

        left.addWidget(btns)

        # Параметры обработки
        params = QGroupBox("Параметры обработки")
        fl = QFormLayout(params)

        self.brightness = QSlider(Qt.Orientation.Horizontal)
        self.brightness.setRange(0, 300)
        self.brightness.setValue(100)
        self.brightness.valueChanged.connect(self.schedule_update)
        fl.addRow("Яркость:", self.brightness)

        self.contrast = QSlider(Qt.Orientation.Horizontal)
        self.contrast.setRange(0, 300)
        self.contrast.setValue(100)
        self.contrast.valueChanged.connect(self.schedule_update)
        fl.addRow("Контраст:", self.contrast)

        size_box = QHBoxLayout()
        self.w_spin = QSpinBox()
        self.w_spin.setRange(1, 10000)
        self.h_spin = QSpinBox()
        self.h_spin.setRange(1, 10000)
        self.keep_aspect = QCheckBox("Сохранять пропорции")
        self.keep_aspect.setChecked(True)
        self.keep_aspect.stateChanged.connect(self.on_aspect_changed)

        self.w_spin.valueChanged.connect(self.on_size_changed)
        self.h_spin.valueChanged.connect(self.on_size_changed)

        size_box.addWidget(self.w_spin)
        size_box.addWidget(QLabel("×"))
        size_box.addWidget(self.h_spin)
        size_box.addWidget(self.keep_aspect)
        fl.addRow("Новый размер:", size_box)

        left.addWidget(params)

        # Информация
        info = QGroupBox("Блок информации")
        il = QVBoxLayout(info)
        self.info_label = QLineEdit()
        self.info_label.setReadOnly(True)
        il.addWidget(self.info_label)
        left.addWidget(info)
        left.addStretch()

        # Изображение
        self.image_label = QLabel("Перетащите изображение или нажмите «Загрузить»")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("background: white; border: 1px solid #cccccc;")
        self.image_label.setMinimumSize(400, 400)
        main_layout.addWidget(self.image_label, 4)

    # ======================= Настройки =======================
    def restore_settings(self):
        brightness = self.settings.value("brightness", 100, int)
        contrast = self.settings.value("contrast", 100, int)
        keep_aspect = self.settings.value("keep_aspect", True, bool)

        self.brightness.setValue(brightness)
        self.contrast.setValue(contrast)
        self.keep_aspect.setChecked(keep_aspect)

    def save_settings(self):
        self.settings.setValue("brightness", self.brightness.value())
        self.settings.setValue("contrast", self.contrast.value())
        self.settings.setValue("keep_aspect", self.keep_aspect.isChecked())

    def restore_geometry(self):
        if self.settings.contains("geometry"):
            self.restoreGeometry(self.settings.value("geometry"))
        else:
            self.resize(1200, 700)
            self.move(100, 100)

    def save_geometry(self):
        self.settings.setValue("geometry", self.saveGeometry())

    # ======================= Загрузка изображения =======================
    def load_image(self):
        last_dir = self.settings.value("last_directory", str(Path.home() / "Pictures"))
        path, _ = QFileDialog.getOpenFileName(
            self, "Открыть изображение", last_dir,
            "Images (*.png *.jpg *.jpeg *.bmp *.gif *.tif *.tiff *.webp)"
        )
        if path:
            self.settings.setValue("last_directory", str(Path(path).parent))
            self.process_load(Path(path))

    def dragEnterEvent(self, e: QDragEnterEvent):
        if e.mimeData().hasUrls():
            url = e.mimeData().urls()[0].toLocalFile()
            if url.lower().split('.')[-1] in {'png', 'jpg', 'jpeg', 'bmp', 'gif', 'tif', 'tiff', 'webp'}:
                e.acceptProposedAction()

    def dropEvent(self, e: QDropEvent):
        path = Path(e.mimeData().urls()[0].toLocalFile())
        self.process_load(path)

    def process_load(self, path: Path):
        logger.info(f"Начата загрузка изображения: {path}")
        success, msg = self.processor.load_image(str(path))
        if success:
            logger.info(f"Успешно загружено: {path.name}")
            self.update_info()
            self.set_original_size()
            self.apply_all_changes()
            self.btn_save.setEnabled(True)
            self.btn_reset.setEnabled(True)
        else:
            logger.error(f"Ошибка загрузки: {msg}")
        QMessageBox.information(self, "Загрузка", msg)

    def set_original_size(self):
        if self.processor.original_image:
            w, h = self.processor.original_image.size
            self.w_spin.blockSignals(True)
            self.h_spin.blockSignals(True)
            self.w_spin.setValue(w)
            self.h_spin.setValue(h)
            self.w_spin.blockSignals(False)
            self.h_spin.blockSignals(False)

    # ======================= Обработка изменений =======================
    def schedule_update(self):
        self.update_timer.start(150)

    def on_aspect_changed(self):
        if self.keep_aspect.isChecked() and self.processor.original_image:
            orig_w, orig_h = self.processor.original_image.size
            ratio = orig_w / orig_h
            if self.sender() == self.w_spin:
                new_h = int(self.w_spin.value() / ratio)
                self.h_spin.blockSignals(True)
                self.h_spin.setValue(new_h)
                self.h_spin.blockSignals(False)
            elif self.sender() == self.h_spin:
                new_w = int(self.h_spin.value() * ratio)
                self.w_spin.blockSignals(True)
                self.w_spin.setValue(new_w)
                self.w_spin.blockSignals(False)
        self.schedule_update()

    def on_size_changed(self):
        if self.keep_aspect.isChecked():
            self.on_aspect_changed()
        else:
            self.schedule_update()

    def apply_all_changes(self):
        if not self.processor.original_image:
            return

        self.processor.reset()

        bright = self.brightness.value() / 100.0
        contrast = self.contrast.value() / 100.0
        new_w = self.w_spin.value()
        new_h = self.h_spin.value()

        if bright != 1.0:
            self.processor.adjust_brightness(bright)
            logger.info(f"Применена яркость: {bright:.2f}")

        if contrast != 1.0:
            self.processor.adjust_contrast(contrast)
            logger.info(f"Применён контраст: {contrast:.2f}")

        if (new_w, new_h) != self.processor.original_image.size:
            self.processor.resize(new_w, new_h)
            logger.info(f"Изменён размер: {new_w}×{new_h}")

        self.display_current_image()

    def display_current_image(self):
        if not self.processor.current_image:
            self.image_label.setPixmap(QPixmap())
            return

        tmp = OUTPUT_DIR / "temp_preview.jpg"
        tmp.parent.mkdir(exist_ok=True)
        self.processor.current_image.save(tmp, quality=95)

        pixmap = QPixmap(str(tmp)).scaled(
            self.image_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.image_label.setPixmap(pixmap)

    def update_info(self):
        info = self.processor.get_info()
        if info:
            text = f"Ширина: {info['width']} | Высота: {info['height']} | Формат: {info['format']}"
            self.info_label.setText(text)

    def reset_image(self):
        self.set_original_size()
        self.brightness.setValue(100)
        self.contrast.setValue(100)
        self.apply_all_changes()
        self.save_settings()

    def save_image(self):
        if not self.processor.current_image:
            return
        default_path = str(OUTPUT_DIR / "processed_image.jpg")
        path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить",
            default_path,
            "JPEG (*.jpg *.jpeg);;PNG (*.png);;Все файлы (*)"
        )
        if path:
            ok, msg = self.processor.save(path)
            if ok:
                logger.info(f"Изображение сохранено: {Path(path).name}")
                QMessageBox.information(self, "Сохранение", msg)
            else:
                logger.error(f"Ошибка сохранения: {msg}")
                QMessageBox.critical(self, "Ошибка", msg)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.processor.current_image:
            self.display_current_image()

    def closeEvent(self, event):
        self.save_settings()
        self.save_geometry()

        # Удаление временных файлов
        for temp_file in ["output/temp_preview.jpg", "output/temp_preview.png"]:
            path = Path(temp_file)
            if path.exists():
                try:
                    path.unlink()
                except Exception as e:
                    print(f"Не удалось удалить {path}: {e}")

        logger.info("=== ЗАВЕРШЕНИЕ РАБОТЫ ПРИЛОЖЕНИЯ ===")
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("ImageEditor")
    app.setOrganizationName("MallenomSystems")

    win = ImageEditor()
    win.show()

    def on_exit():
        logger.info("=== ПРИЛОЖЕНИЕ ЗАКРЫТО ===")
    app.aboutToQuit.connect(on_exit)

    sys.exit(app.exec())