from PIL import Image

image_types = {
    "jpg": "JPEG",
    "jpeg": "JPEG",
    "png": "PNG",
    "gif": "GIF",
    "tif": "TIFF",
    "tiff": "TIFF",
}

options = {
    'max_width': 800,
    'max_height': 450,
}

def calculate_size(image):
    w = image.width
    h = image.height
    if w > h:
        if w > options['max_width']:
            h = round((h * options['max_width']) / w)
            w = options['max_width']
    else:
        if h > options['max_height']:
            w = round((w * options['max_height']) / h)
            h = options['max_height']
    return [w, h]

def image_resize(image):
    # Open the image using Pillow
    img = Image.open(image)
    width, height = calculate_size(img)

    img = img.resize((int(width), int(height)), Image.ANTIALIAS)
    return img
