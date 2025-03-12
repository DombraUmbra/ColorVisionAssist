import cv2
import numpy as np

# Defining the color ranges
color_ranges = {
    'red1': (
        np.array([0, 150, 70]),
        np.array([10, 255, 255])
    ),
    'red2': (
        np.array([170, 150, 70]),
        np.array([180, 255, 255])
    ),
    'green': (
        np.array([35, 70, 70]),
        np.array([85, 255, 255])
    )
}

# Minimum contour area by pixels
min_contour_area = 500

# Opening the camera
cam = cv2.VideoCapture(0)

while True:
    # Capturing every frame
    ret, frame = cam.read()
    
    # Converting RGB to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Generating masks
    mask_red1 = cv2.inRange(hsv, color_ranges['red1'][0], color_ranges['red1'][1])
    mask_red2 = cv2.inRange(hsv, color_ranges['red2'][0], color_ranges['red2'][1])
    mask_red = mask_red1 | mask_red2
    mask_green = cv2.inRange(hsv, color_ranges['green'][0], color_ranges['green'][1])

    # Expanding the masks
    kernel = np.ones((5, 5), np.uint8)
    mask_red = cv2.dilate(mask_red, kernel, iterations=2)
    mask_green = cv2.dilate(mask_green, kernel, iterations=2)

    # Combining the masks
    mask_combined = mask_red | mask_green
    
    # Filtering the colors
    result = cv2.bitwise_and(frame, frame, mask=mask_combined)
    
    # Adjusting vibrance for masked colors
    result[np.where((result != [0, 0, 0]).all(axis=2))] = [120, 120, 120]
    
    # Darkening the originial frame
    darkened_frame = cv2.addWeighted(frame, 0.5, np.zeros_like(frame), 0.5, 0)
    
    # Combining the results
    combined_result = cv2.addWeighted(darkened_frame, 0.7, result, 0.3, 0)
    
    # Tagging the colors
    contours_red, _ = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours_green, _ = cv2.findContours(mask_green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours_red:
        if cv2.contourArea(contour) > min_contour_area:
            x, y, w, h = cv2.boundingRect(contour)
            mask_contour = mask_red[y:y+h, x:x+w]
            contour_area = cv2.contourArea(contour)
            mask_area = np.sum(mask_contour > 0)
            accuracy = min((mask_area / contour_area) * 100, 100)
            cv2.rectangle(combined_result, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.putText(combined_result, f'Red ({accuracy:.1f}%)', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    
    for contour in contours_green:
        if cv2.contourArea(contour) > min_contour_area:
            x, y, w, h = cv2.boundingRect(contour)
            mask_contour = mask_green[y:y+h, x:x+w]
            contour_area = cv2.contourArea(contour)
            mask_area = np.sum(mask_contour > 0)
            accuracy = min((mask_area / contour_area) * 100, 100)
            cv2.rectangle(combined_result, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(combined_result, f'Green ({accuracy:.1f}%)', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    # Showing the output
    cv2.imshow("Original", frame)
    cv2.imshow("Color Filtered for Color Blindness", combined_result)
    
    # Key for closing the application
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Closing the camera
cam.release()
cv2.destroyAllWindows()
