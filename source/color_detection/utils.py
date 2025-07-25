import cv2
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Text drawing function with UTF-8 support
def draw_text_with_utf8(image, text, position, text_color=(255, 255, 255), font_size=20, outline_color=(0, 0, 0), outline_thickness=2):
    """
    Draw text with UTF-8 support using PIL library
    
    Args:
        image: OpenCV image (BGR format)
        text: Text string to draw
        position: (x, y) position
        text_color: Text color as BGR tuple (will be converted to RGB for PIL)
        font_size: Font size
        outline_color: Outline color as BGR tuple (will be converted to RGB for PIL)
        outline_thickness: Outline width
        
    Returns:
        OpenCV image with text drawn
    """
    # Convert the image from OpenCV BGR format to RGB for PIL
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(image_rgb)
    draw = ImageDraw.Draw(pil_image)
    
    # Convert BGR colors to RGB for PIL
    # OpenCV uses BGR format, PIL uses RGB format
    text_color_rgb = (text_color[2], text_color[1], text_color[0])  # BGR to RGB
    outline_color_rgb = (outline_color[2], outline_color[1], outline_color[0])  # BGR to RGB
    
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
    # Draw stroke (outline) using RGB colors
    draw.text((x-outline_thickness, y-outline_thickness), text, font=font, fill=outline_color_rgb)
    draw.text((x+outline_thickness, y-outline_thickness), text, font=font, fill=outline_color_rgb)
    draw.text((x-outline_thickness, y+outline_thickness), text, font=font, fill=outline_color_rgb)
    draw.text((x+outline_thickness, y+outline_thickness), text, font=font, fill=outline_color_rgb)
    
    # Draw the main text using RGB color
    draw.text(position, text, font=font, fill=text_color_rgb)
    
    # Convert back to OpenCV format (BGR)
    text_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    return text_image
