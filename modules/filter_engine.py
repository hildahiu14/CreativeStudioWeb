import cv2
import numpy as np

def adjust_light_and_color(img, brightness=0, contrast=0, saturation=0):
    alpha = 1.0 + (contrast / 100.0)
    beta = brightness
    adjusted = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)
    
    if saturation != 0:
        hsv = cv2.cvtColor(adjusted, cv2.COLOR_BGR2HSV).astype("float32")
        (h, s, v) = cv2.split(hsv)
        s = s + saturation
        s = np.clip(s, 0, 255)
        hsv = cv2.merge([h, s, v]).astype("uint8")
        adjusted = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    return adjusted

def apply_grayscale(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

def apply_sepia(img):
    kernel = np.array([[0.272, 0.534, 0.131],
                       [0.349, 0.686, 0.168],
                       [0.393, 0.769, 0.189]])
    sepia = cv2.transform(img, kernel)
    return np.clip(sepia, 0, 255).astype(np.uint8)

def apply_vintage_vignette(img):
    rows, cols = img.shape[:2]
    kernel_x = cv2.getGaussianKernel(cols, cols/1.5)
    kernel_y = cv2.getGaussianKernel(rows, rows/1.5)
    kernel = kernel_y * kernel_x.T
    mask = 255 * kernel / np.max(kernel)
    vintage = np.copy(img)
    for i in range(3):
        vintage[:,:,i] = vintage[:,:,i] * (mask / 255.0)
    return vintage.astype(np.uint8)

def apply_cyberpunk(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    h = np.mod(h + 40, 180).astype(np.uint8)
    s = cv2.add(s, 40)
    cyber = cv2.merge([h, s, v])
    return cv2.cvtColor(cyber, cv2.COLOR_HSV2BGR)

def apply_invert(img):
    return cv2.bitwise_not(img)

def rotate_90(img):
    return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)

def flip_image(img, mode="horizontal"):
    return cv2.flip(img, 1 if mode == "horizontal" else 0)

def apply_blur(img, value=15):
    if value <= 0: return img
    if value % 2 == 0: value += 1
    return cv2.GaussianBlur(img, (value, value), 0)

def apply_pencil_sketch(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    inv_blur = cv2.bitwise_not(cv2.GaussianBlur(gray, (21, 21), 0))
    sketch = cv2.divide(gray, inv_blur, scale=256.0)
    return cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)

def apply_cartoon(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
    color = cv2.bilateralFilter(img, 9, 300, 300)
    return cv2.bitwise_and(color, color, mask=edges)