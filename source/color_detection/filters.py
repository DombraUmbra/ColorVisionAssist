"""
Skin tone filtering and lighting condition analysis
Contains advanced filtering algorithms for color detection
"""

import cv2
import numpy as np

class SkinToneFilters:
    """Skin tone filtering algorithms"""
    
    def __init__(self):
        # Enhanced skin tone ranges (HSV)
        self.skin_ranges = [
            (np.array([0, 20, 70]), np.array([20, 255, 255])),    # Light skin
            (np.array([0, 30, 60]), np.array([17, 255, 255])),   # Medium skin
            (np.array([0, 40, 50]), np.array([15, 255, 255])),   # Dark skin
            (np.array([160, 20, 70]), np.array([180, 255, 255])) # Red-tinted skin
        ]

    def advanced_skin_tone_filter(self, hsv, red_mask):
        """
        Advanced skin tone filtering algorithm
        Shows better performance under different lighting conditions
        """
        # 1. Basic skin tone mask
        skin_mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        for lower_bound, upper_bound in self.skin_ranges:
            skin_mask_temp = cv2.inRange(hsv, lower_bound, upper_bound)
            skin_mask = cv2.bitwise_or(skin_mask, skin_mask_temp)
        
        # 2. Skin tone detection in YCrCb color space (more stable)
        bgr_frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        ycrcb = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2YCrCb)
        
        # Typical skin tone ranges in YCrCb
        skin_ycrcb_mask = cv2.inRange(ycrcb, 
                                     np.array([0, 133, 77]),    # Lower bound
                                     np.array([255, 173, 127])) # Upper bound
        
        # 3. Skin tone control in RGB color space
        bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        b, g, r = cv2.split(bgr)
        
        # Typical RGB conditions for skin tone
        skin_rgb_mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        
        # Condition 1: R > G > B (typical skin tone characteristic)
        condition1 = (r > g) & (g > b)
        
        # Condition 2: Difference between R and G should not be too large
        condition2 = np.abs(r.astype(np.int16) - g.astype(np.int16)) < 80
        
        # Condition 3: Minimum brightness control
        condition3 = (r > 50) & (g > 30) & (b > 20)
        
        # Condition 4: Maximum brightness control (filter overly bright areas)
        condition4 = (r < 250) & (g < 250) & (b < 250)
        
        # Condition 5: Red not dominant (skin tone should not be red)
        condition5 = (r - g) < 50
        
        # Combine all conditions
        skin_rgb_mask = (condition1 & condition2 & condition3 & condition4 & condition5).astype(np.uint8) * 255
        
        # 4. Skin tone validation with histogram analysis
        hist_mask = self.histogram_based_skin_filter(hsv, red_mask)
        
        # 5. Combine all masks (intersection)
        final_skin_mask = cv2.bitwise_and(skin_mask, skin_ycrcb_mask)
        final_skin_mask = cv2.bitwise_and(final_skin_mask, skin_rgb_mask)
        final_skin_mask = cv2.bitwise_and(final_skin_mask, hist_mask)
        
        # 6. Morphological cleaning
        kernel = np.ones((5, 5), np.uint8)
        final_skin_mask = cv2.morphologyEx(final_skin_mask, cv2.MORPH_CLOSE, kernel)
        final_skin_mask = cv2.morphologyEx(final_skin_mask, cv2.MORPH_OPEN, kernel)
        
        # 7. Remove skin tone areas from red mask
        cleaned_red = cv2.bitwise_and(red_mask, cv2.bitwise_not(final_skin_mask))
        
        return cleaned_red, final_skin_mask

    def histogram_based_skin_filter(self, hsv, red_mask):
        """
        Skin tone validation with histogram analysis
        """
        h, s, v = cv2.split(hsv)
        
        # Mask for histogram analysis
        hist_mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        
        # Hue histogram analysis
        # Skin tone is usually in 0-30 degree range
        hue_hist = cv2.calcHist([h], [0], None, [180], [0, 180])
        
        # Saturation histogram analysis
        # Skin tone usually has low-medium saturation
        sat_hist = cv2.calcHist([s], [0], None, [256], [0, 256])
        
        # Skin tone characteristic ranges
        skin_hue_mask = cv2.inRange(h, 0, 30)
        skin_sat_mask = cv2.inRange(s, 15, 120)
        skin_val_mask = cv2.inRange(v, 60, 255)
        
        # Combine histogram masks
        hist_mask = cv2.bitwise_and(skin_hue_mask, skin_sat_mask)
        hist_mask = cv2.bitwise_and(hist_mask, skin_val_mask)
        
        return hist_mask

    def lighting_condition_analysis(self, hsv):
        """
        Analyzes lighting conditions and adjusts skin tone filtering parameters
        """
        # Calculate average brightness (Value)
        average_brightness = np.mean(hsv[:, :, 2])
        
        # Parameters according to lighting condition
        if average_brightness < 80:
            # Low light conditions
            return {
                'skin_threshold': 0.6,
                'red_threshold': 0.8,
                'morph_kernel_size': 7
            }
        elif average_brightness > 180:
            # High light conditions
            return {
                'skin_threshold': 0.8,
                'red_threshold': 0.9,
                'morph_kernel_size': 3
            }
        else:
            # Normal light conditions
            return {
                'skin_threshold': 0.7,
                'red_threshold': 0.85,
                'morph_kernel_size': 5
            }
