import socket
from main import Square, get_rects
import math

class RobotClient:
    def __init__(self, host, port):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((host, port))
    
    def send_command(self, command):
        print(f"[CLIENT] Отправляем команду: {command}")
        self.s.sendall((command + '\n').encode())
        data = self.s.recv(1024)
        response = data.decode().strip()
        print("[CLIENT] Ответ от сервера:", response)
        if response == "BUSY":
            print("[CLIENT] Сервер занят, завершаем работу.")
            self.s.close()
            raise RuntimeError("Server is busy")
        return response

    def close(self):
        self.s.close()


def get_mal_angle(p1, p2):
    x1,y1,x2,y2 = *p1, *p2
    return math.atan2(y2 - y1, x2 - x1)
    

def deform_angle(angle):
    angle = round(angle * 180 / math.pi)
    return 90 - angle % 90 if angle % 90 != 0 else 0 


print('stage 1')

client = RobotClient('127.0.0.1', 5000)

print('stage 2')

client.send_command('TOOL_ROTATE_TO 0')
client.send_command('SET_MAX_SPEED 1500 1500 1500')

print('stage 3')

def get_pos():
    client.send_command('GET_POSITION')

def move(x,y,z):
    x = max(x,56)
    y = max(y,56)

    x = min(x, 300)
    y = min(y, 300)
    client.send_command(f'MOVE_TO {x} {y} {z}')

def activate():
    client.send_command(f'TOOL_VACUUM_ON')

def deactivate():
    client.send_command(f'TOOL_VACUUM_OFF')

def rotate(angle):
    angle = angle%90
    client.send_command(f'TOOL_ROTATE_TO {angle}')

def move_sq(sq, x, y, height0=5, height1=5, max_h=28, rotation=False):
    move(sq.x, sq.y, height0)
    activate()
    move(sq.x, sq.y, max_h)
    if rotation:
        rotate(deform_angle(sq.rotation))
    move(x, y, max_h)
    move(x, y, height1)
    deactivate()

def move_sq_vec(sq, vec, height0=5, height1=5, max_h=28):
    x,y = vec
    move_sq(sq, sq.x + x, sq.y + y, height0, height1, max_h)

def normalize(vec):
    l = length(vec)
    return [vec[0] / l, vec[1] / l]

def set_len_vec(vec, length):
    x,y = normalize(vec)
    return [x * length, y * length]

def length(vec):
    return ( vec[0] ** 2 + vec[1] ** 2 ) ** 0.5

def find_id(sqs, id = 80):
    a = [i for i in sqs if i.size == id]
    return a[0] if a else None



# x,y,z = get_pos()
field = get_rects()


starting_place = Square(175, 175, 80, 0)

try:
    #########################Ваш код: НАЧАЛО#######################

    client.send_command(f'CALIBRATE')

    #Расчистка старта
    for i in field:
        id = i.size
        if id == 0:
            move_sq(i, 300, 300, height0=5, height1=20, max_h=28)
        elif id != 80 and i.collides_with(starting_place):
            vec = [i.x - 175, i.y - 175]
            move_sq_vec(i, set_len_vec(vec, i.size),max_h=15)
            #Обновление поля обязательно
            field = get_rects()

    for stage in range(5):
        stage_sq = find_id(field, 80 - stage * 10)

        move_sq(stage_sq, 175, 175, height0=5, height1=5 + stage * 5, max_h=13 + stage * 5, rotation=True)


    # client.send_command(f'TOOL_VACUUM_OFF')
    # client.send_command(f'MOVE_TO 175 175 100')
    # client.send_command(f'TOOL_VACUUM_ON')
    # client.send_command(f'MOVE_TO 175 175 45')
    # client.send_command(f'MOVE_TO 175 175 100')
    # client.send_command(f'TOOL_VACUUM_OFF')

    
    # move(175, 175, 100)
    #OK X 377.00 Y 93.00 Z 97.00
    # move(175, 175, 100)
    # while True:
        
    #     i = input()
    #     if i == 'a':
    #         activate()
    #     elif i == 'd':
    #         deactivate()
    #     else: 
    #         x,y,z = map(int, i.split())
    #         move(x,y,z)
        
    

    #########################Ваш код: КОНЕЦ#######################
except RuntimeError:
    print("[CLIENT] Сервер занят, завершаем работу.")
finally:
    client.close()

# Пример использования
#client.send_command('SET_MAX_SPEED 1500 1500 1500') # Установить скорость перемещения
#client.send_command('TOOL_ROTATE_TO 90') # Повернуть присоску 0-90 (предупреждаем, что если в команде вы пишете, к примеру, число 60, 
# то он не повернет присоску на 60 градусов от изначального положения, а повернется на отметку 60 градусов в своей системе координат)
##client.send_command('TOOL_VACUUM_ON') # Включить компрессор
##client.send_command('TOOL_VACUUM_OFF') # Выключить компрессор
#client.send_command('MOVE_TO_ROBOT 350 80 200') # Перемещение в координатах робота
#client.send_command('MOVE_TO 270 200 200') # Перемещение в координатах поля
#client.send_command('GET_POSITION') #Получить координаты робота

