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

        # Runtime tracking for label stabilization (per color)
        # Structure: { color_name: [ { 'center': (x,y), 'label_anchor': (ax,ay), 'last_seen': frame, 'bbox': (x,y,w,h) }, ... ] }
        self._label_tracks = {}
        self._frame_idx = 0
    
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
    
    def process_frame(self, frame, selected_colors, sensitivity=5, contrast=5, color_translations=None, skin_tone_filtering=True, stability_enhancement=True, color_blindness_type='red_green', mobile_optimization=False, debug_mode=False, background_dimming=True):
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
        # Start with original frame and optionally darken background
        if background_dimming:
            darkened_background = cv2.convertScaleAbs(frame, alpha=0.3, beta=0)  # 30% brightness
            result = darkened_background.copy()
        else:
            result = frame.copy()
        
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
        
        # Stabilize label positions across frames to reduce jitter
        detected_colors = self._stabilize_label_positions(detected_colors)
        
        # Normalize CB type to algorithm mapping keys so overlays adapt like buttons
        cb_map_key = self._normalize_cb_mapping(color_blindness_type, selected_colors)

        # Apply highlighting system using algorithms module
        result = self.algorithms.apply_highlighting_system(frame, total_mask, detected_colors, cb_map_key, background_dimming)
        
        # Draw color labels using algorithms module
        result = self.algorithms.draw_color_labels(result, detected_colors, cb_map_key)
        
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

    # -------------------------
    # Label stabilization logic
    # -------------------------
    def _stabilize_label_positions(self, detected_colors):
        """Assign stable label positions to detected colors.
        If an object's center hasn't moved beyond a threshold, keep previous label
        position; otherwise update to the new top-center position.
        """
        self._frame_idx += 1
        tracks = self._label_tracks

        # Group detections by color
        by_color = {}
        for idx, info in enumerate(detected_colors):
            by_color.setdefault(info['color_name'], []).append((idx, info))

        for color_name, items in by_color.items():
            # Prepare track list for this color
            if color_name not in tracks:
                tracks[color_name] = []
            color_tracks = tracks[color_name]

            # Greedy nearest-neighbor matching
            used_tracks = set()
            for idx, info in items:
                x, y, w, h = info['bbox']
                center = (x + w / 2.0, y + h / 2.0)

                # Compute default label anchor (top center)
                default_anchor = (int(x + w / 2), int(max(y - 10, 20)))

                # Thresholds based on object size
                size_scale = max(w, h)
                match_thresh = max(20, int(0.25 * size_scale))
                stickiness = max(12, int(0.2 * size_scale))

                # Find best matching existing track
                best_track = None
                best_dist = 1e9
                for t_i, tr in enumerate(color_tracks):
                    if t_i in used_tracks:
                        continue
                    tx, ty = tr['center']
                    dist = ((center[0] - tx) ** 2 + (center[1] - ty) ** 2) ** 0.5
                    if dist < best_dist:
                        best_dist = dist
                        best_track = (t_i, tr)

                if best_track is not None and best_dist <= match_thresh:
                    t_i, tr = best_track
                    used_tracks.add(t_i)
                    # If movement is small, keep previous label position
                    if best_dist <= stickiness:
                        anchor = tr.get('label_anchor', default_anchor)
                    else:
                        # Significant move: snap to new default anchor
                        anchor = default_anchor

                    # Update track
                    tr['center'] = center
                    tr['label_anchor'] = anchor
                    tr['bbox'] = (x, y, w, h)
                    tr['last_seen'] = self._frame_idx

                    # Smooth/stabilize label typography independent of noisy bbox
                    # Even smaller labels: further lower target size range and smoothing baseline
                    prev_font = int(tr.get('label_font_size', 13))
                    target_font = int(max(10, min(14, 12 + 0.01 * max(w, h))))
                    smoothed_font = int(0.8 * prev_font + 0.2 * target_font)
                    tr['label_font_size'] = smoothed_font
                    # Thinner outline for less visual bulk
                    tr['label_outline'] = max(1, smoothed_font // 10)

                else:
                    # Create a new track
                    color_tracks.append({
                        'center': center,
                        'label_anchor': default_anchor,
                        'bbox': (x, y, w, h),
                        'last_seen': self._frame_idx,
                        # Initialize typography with a smaller size derived from scale
                        'label_font_size': int(max(10, min(14, 12 + 0.01 * max(w, h)))) ,
                        'label_outline': 1
                    })
                    anchor = default_anchor

                # Save stabilized label anchor back to detection
                detected_colors[idx]['label_anchor'] = anchor
                detected_colors[idx]['label_font_size'] = int(tracks[color_name][-1]['label_font_size']) if color_tracks else int(max(14, min(22, 16 + 0.02 * max(w, h))))
                detected_colors[idx]['label_outline'] = int(tracks[color_name][-1].get('label_outline', 3)) if color_tracks else 3

            # Prune stale tracks
            max_age = 30  # frames
            tracks[color_name] = [tr for tr in color_tracks if (self._frame_idx - tr.get('last_seen', 0)) <= max_age]

        return detected_colors

    def _normalize_cb_mapping(self, cb_type, selected_colors):
        """Map UI CB types to algorithm mapping keys.
        - 'protanopia'/'deuteranopia' -> 'red_green'
        - 'tritanopia' -> 'blue_yellow'
        - 'custom' -> infer: if only BY selected then 'blue_yellow', else 'red_green'
        - fallback -> 'red_green'
        """
        try:
            ct = (cb_type or 'none').lower()
        except Exception:
            ct = 'none'
        if ct in ('protanopia', 'deuteranopia'):
            return 'red_green'
        if ct == 'tritanopia':
            return 'blue_yellow'
        if ct == 'custom':
            try:
                r = bool(selected_colors.get('red'))
                g = bool(selected_colors.get('green'))
                b = bool(selected_colors.get('blue'))
                y = bool(selected_colors.get('yellow'))
                # If user focused purely on BY pair, use blue_yellow mapping
                if (b or y) and not (r or g):
                    return 'blue_yellow'
            except Exception:
                pass
            return 'red_green'
        # Default mapping
        return 'red_green'
