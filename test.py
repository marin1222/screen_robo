import cv2
import numpy as np
import tkinter as tk

# Tkinterで画面サイズを取得
root = tk.Tk()
screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()
root.destroy()

images = ["image1.jpg", "image2.jpg", "image3.jpg"]
index = 0

cv2.namedWindow("Display", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("Display", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

def fit_image_with_black(img, screen_w, screen_h):
    h, w = img.shape[:2]
    scale = min(screen_w / w, screen_h / h)
    new_w, new_h = int(w * scale), int(h * scale)
    resized = cv2.resize(img, (new_w, new_h))

    # 黒背景に中央配置
    background = np.zeros((screen_h, screen_w, 3), dtype=np.uint8)
    x_offset = (screen_w - new_w) // 2
    y_offset = (screen_h - new_h) // 2
    background[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
    return background

while True:
    img = cv2.imread(images[index])
    if img is None:
        print(f"{images[index]} が見つかりません")
        break

    img_fitted = fit_image_with_black(img, screen_w, screen_h)
    cv2.imshow("Display", img_fitted)

    key = cv2.waitKey(0) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('1'):
        index = 0
    elif key == ord('2'):
        index = 1
    elif key == ord('3'):
        index = 2

cv2.destroyAllWindows()
