import math

def get_mal_angle(p1, p2):
    x1,y1,x2,y2 = *p1, *p2
    angle = round(math.atan2(y2 - y1, x2 - x1) * 180 / math.pi)
    return 90 - angle % 90 if angle % 90 != 0 else 0




