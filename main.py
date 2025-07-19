from os.path import exists

import cv2 as cv
import numpy as np
import os
from math import dist, atan2


def get_mal_angle(p1, p2):
    x1,y1,x2,y2 = *p1, *p2
    return atan2(y2 - y1, x2 - x1)

def transform_points(point, origin):
    new_x = point[0] - origin[0]
    new_y = point[1] - origin[1]
    return [300 - new_x, 300 - new_y]


def average_point(points):
    if not points:
        return None

    x_total = sum(p[0] for p in points)
    y_total = sum(p[1] for p in points)
    n = len(points)

    avg_x = int(round(x_total / n))
    avg_y = int(round(y_total / n))
    return (avg_x, avg_y)

def db_scan(poins1):
    clusters = []
    poins = poins1.copy()
    while poins:
        cl = [poins.pop()]
        for p in cl:
            sosed = [p1 for p1 in poins if dist(p,p1) < 5]
            cl += sosed
            for p1 in sosed: poins.remove(p1)
        clusters.append(cl)
    return [average_point(cl) for cl in clusters]

def clear_console():
    os.system("cls")


def get_rectangle_center(points):
    """
    Принимает массив из 4 точек (формат: [[x1, y1], [x2, y2], [x3, y3], [x4, y4]])
    Возвращает центр прямоугольника как (x, y)
    """
    center = points.mean(axis=0)
    return list(center)


cap = cv.VideoCapture(0)
dictionary = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_4X4_1000)
dictionaryW = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_5X5_1000)

image = cv.imread("C:\\WIN_20250718_18_11_34_Pro.jpg")

param = cv.aruco.DetectorParameters()

# markerCorners, markerIds, rejectedCandidates = cv.aruco.detectMarkers(image, dictionary, parameters=param)
# for i in range(len(markerIds)):
#     for j in range(4):
#         cv.circle(image, list(int(i) for i in markerCorners[i][0][j]), 5, (0, 255, 0), 5)
#         cv.imshow("imggg", image)
#         cv.waitKey()
#
# markerCorners, markerIds, rejectedCandidates = cv.aruco.detectMarkers(image, dictionary, parameters=param)
# for i in range(len(markerIds)):
#     if markerIds[i][0] in [0, 1, 2, 3]:
#         for j in range(4):
#             cv.circle(image, [int(i) for i in markerCorners[i][0][j]], 2, (255, 0, 0), 2)
#             cv.imshow("m", image)
#             cv.waitKey()
#
# cv.imshow("m", image)
# cv.waitKey()
# cv.destroyAllWindows()




ptsAcc = []
ptsIndAcc = []

while True:
    ret, frame = cap.read()
    if not ret:
        print("Не удалось получить кадр")
        break
    gray_bgr = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    gray = cv.cvtColor(gray_bgr, cv.COLOR_GRAY2BGR)
    dst = gray
    markerCorners, markerIds, rejectedCandidates = cv.aruco.detectMarkers(gray, dictionary, parameters=param)
    mcW, miW, rcW = cv.aruco.detectMarkers(gray, dictionaryW, parameters=param)

    if miW is not None:
        for i in range(len(miW)):
            cv.circle(gray, list(int(i) for i in get_rectangle_center(mcW[i][0])), 2, (0, 0, 255), 2)

    if markerIds is not None:
        for i in range(len(markerIds)):
            if markerIds[i][0] in [40, 50, 60, 70, 80]:
                cv.circle(gray, list(int(i) for i in get_rectangle_center(markerCorners[i][0])), 2, (0, 255, 0), 2)

    ptsInd = []
    res = gray
    if markerIds is not None:
        for i in range(len(markerIds)):
            if markerIds[i][0] in [0, 1, 2, 3]:
                ptsInd.append(i)
    if len(ptsInd) == 4:
        pts = np.float32([list(int(i) for i in markerCorners[ptsInd[0]][0][1]),
                          list(int(i) for i in markerCorners[ptsInd[1]][0][0]),
                          list(int(i) for i in markerCorners[ptsInd[2]][0][2]),
                          list(int(i) for i in markerCorners[ptsInd[3]][0][3])])
        ptsAcc = pts.copy()
        if not ptsIndAcc: ptsIndAcc = ptsInd.copy()

        ptsA = np.float32([[0, 0], [300, 0], [0, 300], [300, 300]])
        M = cv.getPerspectiveTransform(pts, ptsA)
        dst = cv.warpPerspective(gray, M, (300, 300))
        MM = cv.getRotationMatrix2D(((300 - 1) / 2.0, (300 - 1) / 2.0), 180, 1)
        im = cv.warpAffine(dst, MM, (300, 300))

        fp = cv.flip(im, 1)
        res = fp.copy()

    elif len(ptsAcc) == 4:
        ptsA = np.float32([[0, 0], [300, 0], [0, 300], [300, 300]])
        M = cv.getPerspectiveTransform(ptsAcc, ptsA)
        dst = cv.warpPerspective(gray, M, (300, 300))
        MM = cv.getRotationMatrix2D(((300 - 1) / 2.0, (300 - 1) / 2.0), 180, 1)
        im = cv.warpAffine(dst, MM, (300, 300))

        fp = cv.flip(im, 1)
        res = fp.copy()

    else:
        res = gray

    red_mask = cv.inRange(res, (0, 0, 250), (10, 10, 255))

    # Создаем маску для зелёного цвета (в BGR: (0, 255, 0))
    green_mask = cv.inRange(res, (0, 250, 0), (10, 255, 10))

    # Находим координаты ненулевых точек (то есть цветных точек)
    red_coords = cv.findNonZero(red_mask)  # np array: [[x, y]], [[x2, y2]], ...
    green_coords = cv.findNonZero(green_mask)

    # Преобразуем в список координат
    if red_coords is not None:
        red_points = [tuple(pt[0]) for pt in red_coords]
    else:
        red_points = []

    if green_coords is not None:
        green_points = [tuple(pt[0]) for pt in green_coords]
    else:
        green_points = []

    avg_red = db_scan(red_points)
    avg_green = db_scan(green_points)
    print("\n" * 100)
    # red_points.sort()
    # green_points.sort()
    # for i in range(0, len(green_points) - 36, 37):
    #     avg_green.append(average_point([green_points[i+j] for j in range(37)]))
    # for i in range(0, len(red_points) - 36, 37):
    #     avg_red.append(average_point([red_points[i+j] for j in range(37)]))
    wrngSqr = list([325 - j for j in i] for i in avg_red)
    print(wrngSqr)
    finArr = []
    for i in wrngSqr:
        x, y = i
        ind = 0
        rot = 0
    mc, mi, rc = cv.aruco.detectMarkers(res, dictionary, parameters=param)
    if mi is not None:
        for i in range(len(mi)):
            x, y = list(int(i) for i in get_rectangle_center(mc[i][0]))
            ind = mi[i][0]
            rot = get_mal_angle([int(i) for i in mc[i][0][1]], [int(i) for i in mc[i][0][0]])
            print(f'{i + 1}: x: {325 - x}, y: {325 - y}, ind: {ind}, rot: {rot}')

    cv.imshow("image", res)
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()

# cv.waitKey()
cv.destroyAllWindows()

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
            (half_size, -half_size),  # bottom-right
            (half_size, half_size),  # top-right
            (-half_size, half_size)  # top-left
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
            length = math.sqrt(normal[0] ** 2 + normal[1] ** 2)
            if length > 0:
                axes.append((normal[0] / length, normal[1] / length))

        # Get axes from second square
        for i in range(len(corners2)):
            p1 = corners2[i]
            p2 = corners2[(i + 1) % len(corners2)]
            edge = (p2[0] - p1[0], p2[1] - p1[1])
            normal = (-edge[1], edge[0])  # Perpendicular vector
            # Normalize
            length = math.sqrt(normal[0] ** 2 + normal[1] ** 2)
            if length > 0:
                axes.append((normal[0] / length, normal[1] / length))

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

ptsAccGlodal= []
imgCount = 1

def get_rects():
    global ptsAccGlodal
    global imgCount
    ret, frame = cap.read()
    if not ret:
        print("Не удалось получить кадр")
    gray_bgr = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    gray = cv.cvtColor(gray_bgr, cv.COLOR_GRAY2BGR)
    markerCorners, markerIds, rejectedCandidates = cv.aruco.detectMarkers(gray, dictionary, parameters=param)
    mcW, miW, rcW = cv.aruco.detectMarkers(gray, dictionaryW, parameters=param)

    if miW is not None:
        for i in range(len(miW)):
            cv.circle(gray, list(int(i) for i in get_rectangle_center(mcW[i][0])), 2, (0, 0, 255), 2)

    if markerIds is not None:
        for i in range(len(markerIds)):
            if markerIds[i][0] in [40, 50, 60, 70, 80]:
                cv.circle(gray, list(int(i) for i in get_rectangle_center(markerCorners[i][0])), 2, (0, 255, 0), 2)

    ptsInd = []
    res = gray
    if markerIds is not None:
        for i in range(len(markerIds)):
            if markerIds[i][0] in [0, 1, 2, 3]:
                ptsInd.append(i)
    if len(ptsInd) == 4:
        pts = np.float32([list(int(i) for i in markerCorners[ptsInd[0]][0][1]),
                          list(int(i) for i in markerCorners[ptsInd[1]][0][0]),
                          list(int(i) for i in markerCorners[ptsInd[2]][0][2]),
                          list(int(i) for i in markerCorners[ptsInd[3]][0][3])])
        ptsAccGlodal = pts.copy()

        ptsA = np.float32([[0, 0], [300, 0], [0, 300], [300, 300]])
        M = cv.getPerspectiveTransform(pts, ptsA)
        dst = cv.warpPerspective(gray, M, (300, 300))
        MM = cv.getRotationMatrix2D(((300 - 1) / 2.0, (300 - 1) / 2.0), 180, 1)
        im = cv.warpAffine(dst, MM, (300, 300))

        fp = cv.flip(im, 1)
        res = fp.copy()

    elif len(ptsAccGlodal) == 4:
        ptsA = np.float32([[0, 0], [300, 0], [0, 300], [300, 300]])
        M = cv.getPerspectiveTransform(ptsAccGlodal, ptsA)
        dst = cv.warpPerspective(gray, M, (300, 300))
        MM = cv.getRotationMatrix2D(((300 - 1) / 2.0, (300 - 1) / 2.0), 180, 1)
        im = cv.warpAffine(dst, MM, (300, 300))

        fp = cv.flip(im, 1)
        res = fp.copy()

    else:
        res = gray

    red_mask = cv.inRange(res, (0, 0, 250), (10, 10, 255))

    # Находим координаты ненулевых точек (то есть цветных точек)
    red_coords = cv.findNonZero(red_mask)  # np array: [[x, y]], [[x2, y2]], ...

    # Преобразуем в список координат
    if red_coords is not None:
        red_points = [tuple(pt[0]) for pt in red_coords]
    else:
        red_points = []
    avg_red = db_scan(red_points)
    wrngSqr = list([325 - j for j in i] for i in avg_red)
    finArr = []
    for i in wrngSqr:
        x, y = i
        ind = 0
        rot = 0
        finArr.append(Square(x, y, ind, rot))
    mc, mi, rc = cv.aruco.detectMarkers(res, dictionary, parameters=param)
    for i in range(len(mi)):
        x, y = list(int(i) for i in get_rectangle_center(mc[i][0]))
        ind = mi[i][0]
        rot = get_mal_angle([int(i) for i in mc[i][0][1]], [int(i) for i in mc[i][0][0]])
        finArr.append(Square(325 - x, 325 - y, ind, rot))
    cv.imwrite(f'img{imgCount}.jpeg', res)
    imgCount += 1
    return finArr
