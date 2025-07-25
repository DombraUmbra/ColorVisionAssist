"""
Main ColorDetector class that combines all color detection modules
This is the refactored version that maintains backward compatibility
"""

import cv2
import numpy as np
from .filters import SkinToneFilters
from .algorithms import ColorDetectionAlgorithms
from .utils import draw_text_with_utf8

class ColorDetector:
    """
    Main color detection class that orchestrates all detection algorithms
    Maintains full backward compatibility with the original interface
    """
    
    def __init__(self):
        # Initialize component modules
        self.skin_filters = SkinToneFilters()
        self.algorithms = ColorDetectionAlgorithms()
        
        # Expose component attributes for backward compatibility
        self.color_ranges = self.algorithms.color_ranges
        self.min_areas = self.algorithms.min_areas
        self.color_blindness_mappings = self.algorithms.color_blindness_mappings
    
    def advanced_skin_tone_filter(self, hsv, red_mask):
        """
        Advanced skin tone filtering algorithm
        Delegates to SkinToneFilters module
        """
        return self.skin_filters.advanced_skin_tone_filter(hsv, red_mask)
    
    def histogram_based_skin_filter(self, hsv, red_mask):
        """
        Skin tone validation with histogram analysis
        Delegates to SkinToneFilters module
        """
        return self.skin_filters.histogram_based_skin_filter(hsv, red_mask)
    
    def lighting_condition_analysis(self, hsv):
        """
        Analyzes lighting conditions and adjusts filtering parameters
        Delegates to SkinToneFilters module
        """
        return self.skin_filters.lighting_condition_analysis(hsv)
    
    def additional_filters_for_red(self, red_mask, lighting_parameters=None):
        """
        Additional filtering operations for red color
        Delegates to ColorDetectionAlgorithms module
        """
        if lighting_parameters is None:
            lighting_parameters = {'morph_kernel_size': 5}
        return self.algorithms.additional_filters_for_red(red_mask, lighting_parameters)
    
    def process_frame(self, frame, selected_colors, sensitivity=5, contrast=5, color_translations=None, skin_tone_filtering=True, stability_enhancement=True, color_blindness_type='red_green', mobile_optimization=False, debug_mode=False):
        """
        Improved color detection + highlighting system
        
        Args:
            mobile_optimization: True for fast processing on mobile devices
        """
        if color_translations is None:
            color_translations = {
                'skin': 'Ten Rengi',
                'red': 'Kırmızı',
                'green': 'Yeşil', 
                'blue': 'Mavi',
                'yellow': 'Sarı'
            }
        
        # Simple preprocessing (same for all colors)
        alpha = 1.0 + (contrast - 5) * 0.15  # Effective contrast
        frame_enhanced = cv2.convertScaleAbs(frame, alpha=alpha, beta=5)
        
        # HSV conversion
        hsv = cv2.cvtColor(frame_enhanced, cv2.COLOR_BGR2HSV)
        
        # Analyze lighting conditions
        lighting_parameters = self.lighting_condition_analysis(hsv)
        
        # Noise reduction (simplified for mobile)
        if mobile_optimization:
            # Faster filtering for mobile
            hsv = cv2.medianBlur(hsv, 3)
        else:
            # Full filtering for desktop
            hsv = cv2.bilateralFilter(hsv, 9, 75, 75)
        
        # HIGHLIGHTING SYSTEM PREPARATION
        # Start with original frame for background darkening
        result = frame.copy()
        darkened_background = cv2.convertScaleAbs(frame, alpha=0.3, beta=0)  # 30% brightness
        
        # ALWAYS APPLY BACKGROUND DARKENING
        # First darken the entire frame
        result = darkened_background.copy()
        
        # Combine all color masks
        total_mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        
        # Store color information (for drawing)
        detected_colors = []
        
        # Process each color (excluding skin tone - only used in background)
        for color_name, selected in selected_colors.items():
            if not selected or color_name not in self.color_ranges or color_name == 'skin':
                continue
            
            # Process color mask using algorithms module
            combined_mask = self.algorithms.process_color_mask(hsv, color_name, lighting_parameters)
            
            # Apply advanced skin tone filter for red color
            if color_name == 'red' and skin_tone_filtering:
                # Apply advanced skin tone filter
                combined_mask, skin_mask_debug = self.advanced_skin_tone_filter(hsv, combined_mask)
                
                # Additional check: Size and shape control for red areas
                combined_mask = self.additional_filters_for_red(combined_mask, lighting_parameters)
                
                # Light smoothing for red - for stability
                combined_mask = cv2.GaussianBlur(combined_mask, (3, 3), 0)
                _, combined_mask = cv2.threshold(combined_mask, 127, 255, cv2.THRESH_BINARY)
            
            # Find contours
            contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Color value
            color = self.algorithms.get_color_value(color_name)
            
            # Collect valid contours for this color
            for contour in contours:
                # Validate contour using algorithms module
                is_valid, area = self.algorithms.validate_contour(contour, color_name, sensitivity)
                if not is_valid:
                    continue
                
                # Bounding box
                x, y, w, h = cv2.boundingRect(contour)
                
                # Calculate accuracy
                roi_mask = combined_mask[y:y+h, x:x+w]
                mask_area = np.sum(roi_mask > 0)
                accuracy = min(100, (mask_area / max(area, 1)) * 100)
                
                # Simple accuracy control (same for all colors)
                if accuracy < 30:
                    continue
                
                # Add this contour's mask to total mask
                cv2.fillPoly(total_mask, [contour], 255)
                
                # Store color information
                text = f"{color_translations.get(color_name, color_name)} ({accuracy:.0f}%)"
                detected_colors.append({
                    'contour': contour,
                    'bbox': (x, y, w, h),
                    'color': color,
                    'color_name': color_name,
                    'text': text
                })
        
        # Apply highlighting system using algorithms module
        result = self.algorithms.apply_highlighting_system(frame, total_mask, detected_colors, color_blindness_type)
        
        # Draw color labels using algorithms module
        result = self.algorithms.draw_color_labels(result, detected_colors, color_blindness_type)
        
        # Debug mode: Print filtering information to screen
        if debug_mode:
            debug_info = f"Light level: {lighting_parameters.get('skin_threshold', 'N/A'):.1f}"
            debug_info += f" | Detected color count: {len(detected_colors)}"
            
            # Print debug info to top left corner
            result = draw_text_with_utf8(
                result, debug_info, (10, 30),
                text_color=(255, 255, 255), font_size=12,
                outline_color=(0, 0, 0), outline_thickness=1
            )
        
        return result
