import cv2 as cv
import numpy as np
from collision import calculate_distance_mm, calibrate_distance, get_distance_with_calibration, draw_distance_line

def mouse_callback(event, x, y, flags, param):
    """Mouse callback to select points"""
    global points, image_copy
    
    if event == cv.EVENT_LBUTTONDOWN:
        if len(points) < 2:
            points.append((x, y))
            cv.circle(image_copy, (x, y), 5, (0, 255, 0), -1)
            
            if len(points) == 1:
                cv.putText(image_copy, f"Point 1: ({x}, {y})", (10, 30), 
                          cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            elif len(points) == 2:
                cv.putText(image_copy, f"Point 2: ({x}, {y})", (10, 60), 
                          cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Calculate distance
                distance = calculate_distance_mm(points[0], points[1])
                print(f"Distance: {distance:.2f} mm")
                
                # Draw line and distance
                draw_distance_line(image_copy, points[0], points[1], distance)
        
        cv.imshow("Distance Measurement", image_copy)

def main():
    global points, image_copy
    
    # Load your image (replace with your image path)
    image_path = "C:\\WIN_20250718_18_11_34_Pro.jpg"  # Use your image path
    image = cv.imread(image_path)
    
    if image is None:
        print("Error: Could not load image")
        return
    
    image_copy = image.copy()
    points = []
    
    # Create window and set mouse callback
    cv.namedWindow("Distance Measurement")
    cv.setMouseCallback("Distance Measurement", mouse_callback)
    
    # Instructions
    print("Click two points to measure distance")
    print("Press 'r' to reset, 'q' to quit")
    
    while True:
        cv.imshow("Distance Measurement", image_copy)
        key = cv.waitKey(1) & 0xFF
        
        if key == ord('q'):
            break
        elif key == ord('r'):
            # Reset
            points = []
            image_copy = image.copy()
            print("Reset - click two points to measure distance")
    
    cv.destroyAllWindows()

def calibrate_example():
    """Example of how to calibrate the distance measurement"""
    
    # Example: You have a known object that's 100mm wide
    # and it appears as 200 pixels wide in your image
    known_distance_mm = 100  # mm
    p1 = (100, 100)  # pixels
    p2 = (300, 100)  # pixels (200 pixels apart)
    
    # Calibrate
    conversion_factor = calibrate_distance(known_distance_mm, p1, p2)
    print(f"Calibration factor: {conversion_factor:.4f} mm/pixel")
    
    # Now use this factor for other measurements
    test_p1 = (150, 150)
    test_p2 = (250, 200)
    distance = get_distance_with_calibration(test_p1, test_p2, conversion_factor)
    print(f"Test distance: {distance:.2f} mm")

if __name__ == "__main__":
    # Uncomment the function you want to run:
    main()  # Interactive distance measurement
    # calibrate_example()  # Calibration example 