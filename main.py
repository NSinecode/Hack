# import cv2 as cv
# import numpy as np
# def get_rectangle_center(points):
#     """
#     Принимает массив из 4 точек (формат: [[x1, y1], [x2, y2], [x3, y3], [x4, y4]])
#     Возвращает центр прямоугольника как (x, y)
#     """
#     points = np.array(points)
#     center = points.mean(axis=0)
#     return list(center)

# # cap = cv.VideoCapture(1)
# dictionary = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_4X4_1000)

# image = cv.imread("C:\\WIN_20250718_18_11_34_Pro.jpg")

# param = cv.aruco.DetectorParameters()

# markerCorners, markerIds, rejectedCandidates = cv.aruco.detectMarkers(image, dictionary, parameters=param)
# sqrInd = []
# for i in range(len(markerIds)):
#     if markerIds[i][0] in [40, 50, 60, 70, 80]:
#         sqrInd.append(i)

# # pts = np.float32([list(int(i) for i in markerCorners[ptsInd[0]][0][1]),
# # list(int(i) for i in markerCorners[ptsInd[1]][0][0]),
# # list(int(i) for i in markerCorners[ptsInd[2]][0][2]),
# # # list(int(i) for i in markerCorners[ptsInd[3]][0][3])])
# pts = np.float32([[369, 921], [1237, 1006], [513, 118], [1277, 216]])


# ptsA = np.float32([[0, 0], [500, 0], [0, 500], [500, 500]])
# M = cv.getPerspectiveTransform(pts, ptsA)
# dst = cv.warpPerspective(image, M, (500, 500))

# MM = cv.getRotationMatrix2D(((500-1)/2.0,(500-1)/2.0),180,1)
# im = cv.warpAffine(dst,MM,(500, 500))

# markerCorners, markerIds, rejectedCandidates = cv.aruco.detectMarkers(im, dictionary, parameters=param)

# sqrInd = []
# for i in range(len(markerIds)):
#     ##if markerIds[i][0] in [40, 50, 60, 70, 80]:
#     cv.circle(im, get_rectangle_center(list(int(i) for i in markerCorners[i][0])))
# while True:
#     ret, frame = cap.read()  # Читаем кадр
#     if not ret:
#         print("Не удалось получить кадр")
#         break
#
#     markerCorners, markerIds, rejectedCandidates = cv.aruco.detectMarkers(frame, dictionary, parameters=param)
#
#     pts = np.float32([[369, 921], [1237, 1006], [513, 118], [1277, 216]])
#
#     ptsA = np.float32([[0, 0], [500, 0], [0, 500], [500, 500]])
#     M = cv.getPerspectiveTransform(pts, ptsA)
#     dst = cv.warpPerspective(frame, M, (500, 500))
#
#     cv.imshow('Веб-камера', dst)  # Показываем кадр
#
#     # Выход по клавише "q"
#     if cv.waitKey(1) & 0xFF == ord('q'):
#         break
#
# # Освобождаем ресурсы
# cap.release()

# cv.imshow("img", im)
# cv.waitKey()
# cv.destroyAllWindows()


import math
from typing import Tuple, Optional

class Square:

    def __init__(self, x: int = 0, y: int = 0, size: int = 50, rotation: int = 0):
        """
        Initialize a square with position, size, and rotation.
        
        Args:
            x: x-coordinate of the square's center
            y: y-coordinate of the square's center  
            size: side length of the square
            rotation: rotation angle in radians
        """
        self.x = x
        self.y = y
        self.size = size
        self.rotation = rotation
    
    def get_corners(self) -> "list[Tuple[int, int]]":
        """Get the four corners of the square after rotation."""
        half_size = self.size / 2
        
        # Define corners relative to center before rotation
        corners = [
            (-half_size, -half_size),  # bottom-left
            (half_size, -half_size),   # bottom-right
            (half_size, half_size),    # top-right
            (-half_size, half_size)    # top-left
        ]
        
        # Apply rotation and translation
        cos_r = math.cos(self.rotation)
        sin_r = math.sin(self.rotation)
        
        rotated_corners = []
        for corner_x, corner_y in corners:
            # Rotate
            rotated_x = corner_x * cos_r - corner_y * sin_r
            rotated_y = corner_x * sin_r + corner_y * cos_r
            # Translate
            rotated_corners.append((rotated_x + self.x, rotated_y + self.y))
        
        return rotated_corners
    
    def get_bounding_box(self) -> Tuple[int, int, int, int]:
        """Get the axis-aligned bounding box (min_x, min_y, max_x, max_y)."""
        corners = self.get_corners()
        x_coords = [corner[0] for corner in corners]
        y_coords = [corner[1] for corner in corners]
        
        return (min(x_coords), min(y_coords), max(x_coords), max(y_coords))
    
    def point_inside(self, px: int, py: int) -> bool:
        """Check if a point is inside the square using ray casting algorithm."""
        corners = self.get_corners()
        
        # Ray casting algorithm
        inside = False
        j = len(corners) - 1
        
        for i in range(len(corners)):
            xi, yi = corners[i]
            xj, yj = corners[j]
            
            if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi) + xi):
                inside = not inside
            j = i
        
        return inside
    
    def collides_with(self, other: 'Square') -> bool:
        """Check collision with another square using Separating Axis Theorem (SAT)."""
        # Quick bounding box check first
        if not self._bounding_boxes_overlap(other):
            return False
        
        # Get corners of both squares
        corners1 = self.get_corners()
        corners2 = other.get_corners()
        
        # Check all axes from both squares
        axes = self._get_separating_axes(corners1, corners2)
        
        for axis in axes:
            if not self._projections_overlap(corners1, corners2, axis):
                return False
        
        return True
    
    def _bounding_boxes_overlap(self, other: 'Square') -> bool:
        """Quick check if bounding boxes overlap."""
        box1 = self.get_bounding_box()
        box2 = other.get_bounding_box()
        
        return not (box1[2] < box2[0] or box1[0] > box2[2] or 
                   box1[3] < box2[1] or box1[1] > box2[3])
    
    def _get_separating_axes(self, corners1: list, corners2: list) -> list:
        """Get potential separating axes from both squares."""
        axes = []
        
        # Get axes from first square
        for i in range(len(corners1)):
            p1 = corners1[i]
            p2 = corners1[(i + 1) % len(corners1)]
            edge = (p2[0] - p1[0], p2[1] - p1[1])
            normal = (-edge[1], edge[0])  # Perpendicular vector
            # Normalize
            length = math.sqrt(normal[0]**2 + normal[1]**2)
            if length > 0:
                axes.append((normal[0]/length, normal[1]/length))
        
        # Get axes from second square
        for i in range(len(corners2)):
            p1 = corners2[i]
            p2 = corners2[(i + 1) % len(corners2)]
            edge = (p2[0] - p1[0], p2[1] - p1[1])
            normal = (-edge[1], edge[0])  # Perpendicular vector
            # Normalize
            length = math.sqrt(normal[0]**2 + normal[1]**2)
            if length > 0:
                axes.append((normal[0]/length, normal[1]/length))
        
        return axes
    
    def _projections_overlap(self, corners1: list, corners2: list, axis: Tuple[int, int]) -> bool:
        """Check if projections of both squares overlap on the given axis."""
        # Project corners of first square
        proj1 = [corner[0] * axis[0] + corner[1] * axis[1] for corner in corners1]
        min1, max1 = min(proj1), max(proj1)
        
        # Project corners of second square
        proj2 = [corner[0] * axis[0] + corner[1] * axis[1] for corner in corners2]
        min2, max2 = min(proj2), max(proj2)
        
        # Check for overlap
        return not (max1 < min2 or max2 < min1)
    
    def move(self, dx: int, dy: int):
        """Move the square by the given delta."""
        self.x += dx
        self.y += dy
    
    def rotate(self, angle: int):
        """Rotate the square by the given angle in radians."""
        self.rotation += angle
    
    def set_position(self, x: int, y: int):
        """Set the position of the square."""
        self.x = x
        self.y = y
    
    def set_rotation(self, rotation: int):
        """Set the rotation of the square in radians."""
        self.rotation = rotation
    
    def get_center(self) -> Tuple[int, int]:
        """Get the center position of the square."""
        return (self.x, self.y)

def get_rects():
    return []

print('onewhsd;fl')