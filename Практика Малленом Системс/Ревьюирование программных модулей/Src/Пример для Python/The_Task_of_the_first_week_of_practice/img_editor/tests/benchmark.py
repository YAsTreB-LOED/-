import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import timeit
from image_processor import ImageProcessor
from PIL import Image

# ВНИМАНИЕ СОЗДАЙТЕ любое тестовое изображение, если нет (без этого работать не будет)
test_image_path = '../test_image.jpg'  # Относительно tests/
if not os.path.exists(test_image_path):
    img = Image.new('RGB', (1000, 1000), color=(255, 0, 0))
    img.save(test_image_path)

proc = ImageProcessor()

N = 100  # Количество запусков для усреднения

# load_image
load_time = timeit.timeit(lambda: proc.load_image(test_image_path), number=N)
avg_load = (load_time / N) * 1000
print(f"load_image average time: {avg_load:.3f} ms")

# adjust_brightness (после загрузки)
proc.load_image(test_image_path)
bright_time = timeit.timeit(lambda: proc.adjust_brightness(1.5), number=N)
avg_bright = (bright_time / N) * 1000
print(f"adjust_brightness average time: {avg_bright:.3f} ms")

# adjust_contrast
proc.load_image(test_image_path)
contrast_time = timeit.timeit(lambda: proc.adjust_contrast(2.0), number=N)
avg_contrast = (contrast_time / N) * 1000
print(f"adjust_contrast average time: {avg_contrast:.3f} ms")

# resize
proc.load_image(test_image_path)
resize_time = timeit.timeit(lambda: proc.resize(500, 500), number=N)
avg_resize = (resize_time / N) * 1000
print(f"resize average time: {avg_resize:.3f} ms")

# reset
proc.load_image(test_image_path)
proc.adjust_brightness(1.5)  # Сделай изменение
reset_time = timeit.timeit(proc.reset, number=N)
avg_reset = (reset_time / N) * 1000
print(f"reset average time: {avg_reset:.3f} ms")

# get_info
proc.load_image(test_image_path)
info_time = timeit.timeit(proc.get_info, number=N)
avg_info = (info_time / N) * 1000
print(f"get_info average time: {avg_info:.3f} ms")

# save
proc.load_image(test_image_path)
save_path = '../saved_image.jpg'
save_time = timeit.timeit(lambda: proc.save(save_path), number=N)
avg_save = (save_time / N) * 1000
print(f"save average time: {avg_save:.3f} ms")

# Размеры
print(f"Size of test_image.jpg: {os.path.getsize(test_image_path) / 1024:.2f} KB")
print(f"Size of saved_image.jpg: {os.path.getsize(save_path) / 1024:.2f} KB")

# Очистка
os.remove(test_image_path)
os.remove(save_path)