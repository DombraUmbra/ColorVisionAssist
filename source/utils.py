import cv2
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Metin çizimi için UTF-8 destekli fonksiyon
def draw_text_with_utf8(img, text, position, text_color=(255, 255, 255), font_size=20, stroke_color=(0, 0, 0), stroke_width=2):
    """
    Draw text with UTF-8 support using PIL library
    
    Args:
        img: OpenCV image (BGR format)
        text: Text string to draw
        position: (x, y) position
        text_color: Text color as RGB tuple
        font_size: Font size
        stroke_color: Outline color
        stroke_width: Outline width
        
    Returns:
        OpenCV image with text drawn
    """
    # Convert the image from OpenCV BGR format to RGB for PIL
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(img_rgb)
    draw = ImageDraw.Draw(pil_img)
    
    # Try to load a font that supports UTF-8
    try:
        # Try to find a suitable system font (Arial supports Turkish chars)
        if os.name == 'nt':  # Windows
            font_path = "C:\\Windows\\Fonts\\arial.ttf"
        else:  # Linux/Mac
            font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        
        if not os.path.exists(font_path):
            # Fallback to default
            font = ImageFont.load_default()
        else:
            font = ImageFont.truetype(font_path, font_size)
    except IOError:
        font = ImageFont.load_default()
    
    # Draw text with stroke (outline)
    x, y = position
    
    # Draw stroke (outline)
    draw.text((x-stroke_width, y-stroke_width), text, font=font, fill=stroke_color)
    draw.text((x+stroke_width, y-stroke_width), text, font=font, fill=stroke_color)
    draw.text((x-stroke_width, y+stroke_width), text, font=font, fill=stroke_color)
    draw.text((x+stroke_width, y+stroke_width), text, font=font, fill=stroke_color)
    
    # Draw the main text
    draw.text(position, text, font=font, fill=text_color)
    
    # Convert back to OpenCV format (BGR)
    img_with_text = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    return img_with_text
