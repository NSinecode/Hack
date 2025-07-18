import socket

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



client = RobotClient('192.168.0.191', 5000)
client.send_command('TOOL_ROTATE_TO 0')

def get_pos():
    return list(map(int, client.send_command('GET_POSITION').split()))

def move(x,y,z):
    client.send_command(f'MOVE_TO {x} {y} {z}')

def activate():
    client.send_command(f'TOOL_VACUUM_ON')

def deactivate():
    client.send_command(f'TOOL_VACUUM_OFF')


def rotate(angle):
    client.send_command(f'TOOL_ROTATE_TO {angle}')

x,y,z = get_pos()



try:
    #########################Ваш код: НАЧАЛО#######################


    client.send_command(f'TOOL_VACUUM_OFF')
    client.send_command(f'MOVE_TO 175 175 100')
    client.send_command(f'TOOL_VACUUM_ON')
    client.send_command(f'MOVE_TO 175 175 45')
    client.send_command(f'MOVE_TO 175 175 100')
    client.send_command(f'TOOL_VACUUM_OFF')


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

