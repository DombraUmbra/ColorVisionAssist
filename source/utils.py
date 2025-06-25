import cv2
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Metin çizimi için UTF-8 destekli fonksiyon
def utf8_destekli_metin_ciz(resim, metin, konum, metin_rengi=(255, 255, 255), font_boyutu=20, dis_cizgi_rengi=(0, 0, 0), dis_cizgi_kalinligi=2):
    """
    Draw text with UTF-8 support using PIL library
    
    Args:
        resim: OpenCV image (BGR format)
        metin: Text string to draw
        konum: (x, y) position
        metin_rengi: Text color as BGR tuple (will be converted to RGB for PIL)
        font_boyutu: Font size
        dis_cizgi_rengi: Outline color as BGR tuple (will be converted to RGB for PIL)
        dis_cizgi_kalinligi: Outline width
        
    Returns:
        OpenCV image with text drawn
    """
    # Convert the image from OpenCV BGR format to RGB for PIL
    resim_rgb = cv2.cvtColor(resim, cv2.COLOR_BGR2RGB)
    pil_resim = Image.fromarray(resim_rgb)
    cizim = ImageDraw.Draw(pil_resim)
    
    # Convert BGR colors to RGB for PIL
    # OpenCV uses BGR format, PIL uses RGB format
    metin_rengi_rgb = (metin_rengi[2], metin_rengi[1], metin_rengi[0])  # BGR to RGB
    dis_cizgi_rengi_rgb = (dis_cizgi_rengi[2], dis_cizgi_rengi[1], dis_cizgi_rengi[0])  # BGR to RGB
    
    # Try to load a font that supports UTF-8
    try:
        # Try to find a suitable system font (Arial supports Turkish chars)
        if os.name == 'nt':  # Windows
            font_yolu = "C:\\Windows\\Fonts\\arial.ttf"
        else:  # Linux/Mac
            font_yolu = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        
        if not os.path.exists(font_yolu):
            # Fallback to default
            font = ImageFont.load_default()
        else:
            font = ImageFont.truetype(font_yolu, font_boyutu)
    except IOError:
        font = ImageFont.load_default()
    
    # Draw text with stroke (outline)
    x, y = konum
      # Draw stroke (outline) using RGB colors
    cizim.text((x-dis_cizgi_kalinligi, y-dis_cizgi_kalinligi), metin, font=font, fill=dis_cizgi_rengi_rgb)
    cizim.text((x+dis_cizgi_kalinligi, y-dis_cizgi_kalinligi), metin, font=font, fill=dis_cizgi_rengi_rgb)
    cizim.text((x-dis_cizgi_kalinligi, y+dis_cizgi_kalinligi), metin, font=font, fill=dis_cizgi_rengi_rgb)
    cizim.text((x+dis_cizgi_kalinligi, y+dis_cizgi_kalinligi), metin, font=font, fill=dis_cizgi_rengi_rgb)
    
    # Draw the main text using RGB color
    cizim.text(konum, metin, font=font, fill=metin_rengi_rgb)
    
    # Convert back to OpenCV format (BGR)
    metinli_resim = cv2.cvtColor(np.array(pil_resim), cv2.COLOR_RGB2BGR)
    return metinli_resim

# Eski fonksiyon adı ile uyumluluk için alias oluştur
draw_text_with_utf8 = utf8_destekli_metin_ciz
