"""
Core color detection algorithms and utilities
Contains main color detection logic and processing algorithms
"""

import cv2
import numpy as np
from .utils import draw_text_with_utf8

class ColorDetectionAlgorithms:
    """Core color detection algorithms"""
    
    def __init__(self):
        # Color ranges (HSV)
        self.color_ranges = {
            'red': [
                (np.array([0, 120, 80]), np.array([10, 255, 255])),    # Lower red range
                (np.array([160, 120, 80]), np.array([180, 255, 255]))  # Upper red range
            ],
            'green': [
                (np.array([40, 80, 80]), np.array([80, 255, 255])),
                (np.array([35, 60, 60]), np.array([85, 255, 255]))     # Extended green range
            ],
            'blue': [
                (np.array([100, 100, 80]), np.array([130, 255, 255])),
                (np.array([90, 80, 60]), np.array([140, 255, 255]))    # Extended blue range
            ],
            'yellow': [
                (np.array([20, 100, 100]), np.array([35, 255, 255])),
                (np.array([15, 80, 80]), np.array([40, 255, 255]))     # Extended yellow range
            ],
            'skin': [  # For filtering purposes
                (np.array([0, 20, 70]), np.array([20, 255, 255]))
            ]
        }
        
        # Minimum area thresholds for each color
        self.min_areas = {
            'red': 200,
            'green': 200,
            'blue': 200,
            'yellow': 200,
            'skin': 500
        }
        
        # Color blindness friendly color mappings
        self.color_blindness_mappings = {
            'red_green': {
                'red': (0, 150, 255),      # Orange-Blue
                'green': (255, 200, 0),    # Yellow-Blue
                'blue': (255, 0, 0),       # Blue
                'yellow': (255, 255, 0),   # Yellow
                'skin': (139, 105, 20)     # Brown
            },
            'blue_yellow': {
                'red': (0, 0, 255),        # Red
                'green': (0, 255, 0),      # Green
                'blue': (255, 100, 255),   # Pink-Purple
                'yellow': (0, 255, 255),   # Cyan
                'skin': (139, 105, 20)     # Brown
            },
            'monochrome': {
                'red': (200, 200, 200),    # Light gray
                'green': (150, 150, 150),  # Medium gray
                'blue': (100, 100, 100),   # Dark gray
                'yellow': (250, 250, 250), # Very light gray
                'skin': (180, 180, 180)    # Gray
            }
        }

    def additional_filters_for_red(self, red_mask, lighting_parameters):
        """
        Additional filtering operations for red color
        To better distinguish skin-like areas
        """
        # Find contours
        contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Cleaned mask
        cleaned_mask = np.zeros_like(red_mask)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 80:  # Filter very small areas
                continue
                
            # Get bounding box
            x, y, w, h = cv2.boundingRect(contour)
            
            # Aspect ratio control - filter long objects like hands
            aspect_ratio = max(w, h) / max(min(w, h), 1)
            if aspect_ratio > 4:  # Filter very long objects
                continue
            
            # Contour density control
            hull = cv2.convexHull(contour)
            hull_area = cv2.contourArea(hull)
            if hull_area > 0:
                solidity = area / hull_area
                if solidity < 0.3:  # Filter very irregular shapes
                    continue
            
            # Size control - skin color regions are usually large
            if area > 5000:  # Filter very large areas (like hands)
                # Additional density control
                roi_mask = red_mask[y:y+h, x:x+w]
                pixelCount = np.sum(roi_mask > 0)
                density = pixelCount / (w * h)
                
                if density < 0.4:  # Filter low-density large areas
                    continue
            
            # Add to mask if this contour is valid
            cv2.fillPoly(cleaned_mask, [contour], 255)
        
        return cleaned_mask

    def apply_highlighting_system(self, frame, total_mask, detected_colors, color_blindness_type='red_green'):
        """
        Apply highlighting system to detected colors
        """
        # Start with original frame for background darkening
        result = frame.copy()
        darkened_background = cv2.convertScaleAbs(frame, alpha=0.3, beta=0)  # 30% brightness
        
        # ALWAYS APPLY BACKGROUND DARKENING
        # First darken the entire frame
        result = darkened_background.copy()
        
        # APPLY HIGHLIGHTING SYSTEM
        if np.sum(total_mask) > 0:
            # Smooth mask edges
            total_mask_smooth = cv2.GaussianBlur(total_mask, (15, 15), 0)
            total_mask_smooth = total_mask_smooth.astype(np.float32) / 255.0
            
            # Expand to 3 channels
            mask_3d = np.stack([total_mask_smooth] * 3, axis=2)
            
            # Restore original colors in detected areas
            result = result.astype(np.float32)
            frame_float = frame.astype(np.float32)
            
            # Highlight original colors with smooth transition
            result = result * (1 - mask_3d) + frame_float * mask_3d
            result = result.astype(np.uint8)
            
            # COLOR BLINDNESS FRIENDLY HIGHLIGHT EFFECT
            # Use optimal frame color for each color
            for color_info in detected_colors:
                contour = color_info['contour']
                color_name = color_info['color_name']
                
                # Select optimal frame color according to color blindness type
                if color_blindness_type in self.color_blindness_mappings:
                    frame_color = self.color_blindness_mappings[color_blindness_type].get(color_name, (255, 255, 255))
                else:
                    frame_color = (255, 255, 255)  # Default white
                
                # Create mask for this contour
                contour_mask = np.zeros(total_mask.shape, dtype=np.uint8)
                cv2.fillPoly(contour_mask, [contour], 255)
                
                # Expand contour edge
                highlight_mask = cv2.dilate(contour_mask, np.ones((5, 5), np.uint8), iterations=1)
                highlight_edge = cv2.bitwise_xor(highlight_mask, contour_mask)
                
                # Draw this color's edge with optimal frame color
                result[highlight_edge > 0] = frame_color
        
        return result

    def draw_color_labels(self, result, detected_colors, color_blindness_type='red_green'):
        """
        Draw color-blind friendly text labels
        """
        # COLOR BLINDNESS FRIENDLY TEXT DRAWING
        for color_info in detected_colors:
            x, y, w, h = color_info['bbox']
            text = color_info['text']
            color_name = color_info['color_name']
            
            # Select optimal text color according to color blindness type
            if color_blindness_type in self.color_blindness_mappings:
                text_color = self.color_blindness_mappings[color_blindness_type].get(color_name, (255, 255, 255))
            else:
                text_color = (255, 255, 255)  # Default white
            
            # Calculate center position
            center_x = x + w // 2
            center_y = y + h // 2
            
            # Get text size
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
            
            # Place text at the top center of the object
            text_x = center_x - text_size[0] // 2
            text_y = max(y - 10, 20)  # At least 20 pixels above
            
            # Convert BGR to RGB (draw_text_with_utf8 expects RGB)
            text_color_rgb = (text_color[2], text_color[1], text_color[0])
            
            # Draw color blindness friendly text
            result = draw_text_with_utf8(
                result, text, (text_x, text_y),
                text_color=text_color_rgb, font_size=14,
                outline_color=(0, 0, 0), outline_thickness=2
            )
        
        return result

    def process_color_mask(self, hsv, color_name, lighting_parameters, skin_tone_filtering=True):
        """
        Process individual color mask with filtering
        """
        if color_name not in self.color_ranges:
            return np.zeros(hsv.shape[:2], dtype=np.uint8)
        
        # Create color mask
        combined_mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        
        for lower_bound, upper_bound in self.color_ranges[color_name]:
            mask = cv2.inRange(hsv, lower_bound, upper_bound)
            combined_mask = cv2.bitwise_or(combined_mask, mask)
        
        # Apply morphological cleaning
        kernel_small = np.ones((3, 3), np.uint8)
        kernel_medium = np.ones((lighting_parameters['morph_kernel_size'], lighting_parameters['morph_kernel_size']), np.uint8)
        
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel_small)
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel_medium)
        combined_mask = cv2.medianBlur(combined_mask, 5)
        
        return combined_mask

    def validate_contour(self, contour, color_name, sensitivity=5):
        """
        Validate contour based on size, shape and other criteria
        """
        area = cv2.contourArea(contour)
        
        # Adjust minimum area according to sensitivity
        min_area = self.min_areas[color_name] * (12 - sensitivity) / 10
        
        if area < min_area:
            return False, 0
        
        # Get bounding box
        x, y, w, h = cv2.boundingRect(contour)
        
        # Advanced shape filter (more tolerant for red)
        aspect_ratio = max(w, h) / max(min(w, h), 1)
        if color_name == 'red':
            if aspect_ratio > 8:  # More tolerant for red
                return False, 0
        else:
            if aspect_ratio > 6:  # Standard for other colors
                return False, 0
        
        # Contour quality control
        peri = cv2.arcLength(contour, True)
        if peri > 0:
            compactness = 4 * np.pi * area / (peri * peri)
            if compactness < 0.1:  # Skip very irregular shapes
                return False, 0
        
        return True, area

    def get_color_value(self, color_name):
        """
        Get BGR color value for drawing
        """
        color_values = {
            'skin': (139, 105, 20),  # Brown tone (for skin color)
            'red': (0, 0, 255),
            'green': (0, 255, 0),
            'blue': (255, 0, 0),
            'yellow': (0, 255, 255)
        }
        return color_values.get(color_name, (255, 255, 255))
