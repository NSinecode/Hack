import math
import cv2 as cv
import numpy as np

def get_mal_angle(p1, p2):
    x1,y1,x2,y2 = *p1, *p2
    angle = round(math.atan2(y2 - y1, x2 - x1) * 180 / math.pi)
    return 90 - angle % 90 if angle % 90 != 0 else 0

def calculate_distance_mm(p1, p2, focal_length_mm=None, known_object_width_mm=50, known_object_width_pixels=115):
    """
    Calculate distance between two points in millimeters.
    
    Args:
        p1: First point (x1, y1)
        p2: Second point (x2, y2) 
        focal_length_mm: Camera focal length in mm (optional, for more accurate measurements)
        known_object_width_mm: Width of a known object in mm (for calibration)
        known_object_width_pixels: Width of the same object in pixels
    
    Returns:
        Distance in millimeters
    """
    x1, y1 = p1
    x2, y2 = p2
    
    # Calculate pixel distance
    pixel_distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    if focal_length_mm and known_object_width_mm and known_object_width_pixels:
        # More accurate calculation using focal length
        # distance = (known_object_width_mm * focal_length_mm) / known_object_width_pixels
        # For point-to-point distance, we need to scale the pixel distance
        scale_factor = known_object_width_mm / known_object_width_pixels
        return pixel_distance * scale_factor
    else:
        # Simple approximation - you'll need to calibrate this
        # This assumes a rough conversion factor (adjust based on your setup)
        conversion_factor = 0.1  # mm per pixel - CALIBRATE THIS!
        return pixel_distance * conversion_factor

def calibrate_distance(known_distance_mm, p1, p2):
    """
    Calibrate the distance measurement using a known distance.
    
    Args:
        known_distance_mm: The actual distance in mm between two points
        p1: First point (x1, y1) in pixels
        p2: Second point (x2, y2) in pixels
    
    Returns:
        Conversion factor (mm per pixel)
    """
    x1, y1 = p1
    x2, y2 = p2
    pixel_distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return known_distance_mm / pixel_distance

def get_distance_with_calibration(p1, p2, conversion_factor):
    """
    Calculate distance using a pre-calibrated conversion factor.
    
    Args:
        p1: First point (x1, y1)
        p2: Second point (x2, y2)
        conversion_factor: mm per pixel (from calibration)
    
    Returns:
        Distance in millimeters
    """
    x1, y1 = p1
    x2, y2 = p2
    pixel_distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return pixel_distance * conversion_factor

def draw_distance_line(image, p1, p2, distance_mm, color=(0, 255, 0), thickness=2):
    """
    Draw a line between two points with distance label.
    
    Args:
        image: OpenCV image
        p1: First point (x1, y1)
        p2: Second point (x2, y2)
        distance_mm: Distance in millimeters
        color: Line color (BGR)
        thickness: Line thickness
    """
    cv.line(image, p1, p2, color, thickness)
    
    # Calculate midpoint for text placement
    mid_x = (p1[0] + p2[0]) // 2
    mid_y = (p1[1] + p2[1]) // 2
    
    # Add distance label
    text = f"{distance_mm:.1f} mm"
    cv.putText(image, text, (mid_x + 5, mid_y - 5), 
               cv.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)




