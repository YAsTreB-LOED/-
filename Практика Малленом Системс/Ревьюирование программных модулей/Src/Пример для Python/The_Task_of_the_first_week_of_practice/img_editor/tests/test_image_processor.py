# tests/test_image_processor.py
import pytest
import sys
from pathlib import Path

# Добавляем корень проекта в путь — теперь импорт работает всегда
sys.path.insert(0, str(Path(__file__).parent.parent))

from image_processor import ImageProcessor
from PIL import Image
import tempfile
import os


@pytest.fixture
def processor():
    proc = ImageProcessor()
    proc.original_image = None
    proc.current_image = None
    proc.original_format = "Unknown"
    return proc


@pytest.fixture
def temp_image():
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        img = Image.new("RGB", (100, 100), color=(100, 150, 200))
        img.save(f.name)
        yield f.name
    try:
        os.unlink(f.name)
    except:
        pass


def test_load_image_success(processor, temp_image):
    success, msg = processor.load_image(temp_image)
    assert success
    assert processor.current_image.size == (100, 100)
    assert processor.original_format in ["PNG", "JPEG", "BMP"]


def test_load_image_invalid_path(processor):
    success, msg = processor.load_image("несуществующий_файл.png")
    assert not success


def test_adjust_contrast(processor, temp_image):
    processor.load_image(temp_image)
    before = processor.current_image.getpixel((50, 50))
    processor.adjust_contrast(3.0)
    after = processor.current_image.getpixel((50, 50))
    assert before != after  # контраст применился!


def test_resize(processor, temp_image):
    processor.load_image(temp_image)
    processor.resize(50, 50)
    assert processor.current_image.size == (50, 50)


def test_reset(processor, temp_image):
    processor.load_image(temp_image)
    processor.adjust_brightness(1.5)
    processor.resize(30, 30)
    processor.reset()
    assert processor.current_image.size == (100, 100)


def test_save_image(processor, temp_image):
    processor.load_image(temp_image)
    output_path = Path("output/test_saved.png")
    output_path.parent.mkdir(exist_ok=True)

    success, msg = processor.save(str(output_path))
    assert success
    assert output_path.exists()

    with Image.open(output_path) as img:
        assert img.size == (100, 100)

    output_path.unlink()  # удаляем