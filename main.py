import os
import time
import keyboard
import pyautogui
from termcolor import colored
from colorant import Colorant

# Settings
TOGGLE_KEY = 'F1'  # Toggle on/off colorant key
X_FOV = 350  # X-Axis FOV
Y_FOV = 350  # Y-Axis FOV
IN_GAME_SENSITIVITY = 0.6  # Replace this with the in-game sensitivity value
FLICK_SPEED = 1.07437623 * (IN_GAME_SENSITIVITY ** -0.9936827126)  # Calculate flick speed
MOVE_SPEED = 1 / (5 * IN_GAME_SENSITIVITY)  # Calculate move speed

monitor = pyautogui.size()
CENTER_X, CENTER_Y = monitor.width // 2, monitor.height // 2


def main():
    os.system('cls')
    os.system('title Buatan')
    colorant = Colorant(CENTER_X - X_FOV // 2, CENTER_Y - Y_FOV // 2, X_FOV, Y_FOV, FLICK_SPEED, MOVE_SPEED)
    print(colored('''
                     ▄████▄   ▒█████   ██▓     ▒█████   ██▀███   ▄▄▄       ███▄    █ ▄▄▄█████▓
                    ▒██▀ ▀█  ▒██▒  ██▒▓██▒    ▒██▒  ██▒▓██ ▒ ██▒▒████▄     ██ ▀█   █ ▓  ██▒ ▓▒
                    ▒▓█    ▄ ▒██░  ██▒▒██░    ▒██░  ██▒▓██ ░▄█ ▒▒██  ▀█▄  ▓██  ▀█ ██▒▒ ▓██░ ▒░
                    ▒▓▓▄ ▄██▒▒██   ██░▒██░    ▒██   ██░▒██▀▀█▄  ░██▄▄▄▄██ ▓██▒  ▐▌██▒░ ▓██▓ ░ 
                    ▒ ▓███▀ ░░ ████▓▒░░██████▒░ ████▓▒░░██▓ ▒██▒ ▓█   ▓██▒▒██░   ▓██░  ▒██▒ ░ 
                    ░ ░▒ ▒  ░░ ▒░▒░▒░ ░ ▒░▓  ░░ ▒░▒░▒░ ░ ▒▓ ░▒▓░ ▒▒   ▓▒█░░ ▒░   ▒ ▒   ▒ ░░   
                      ░  ▒     ░ ▒ ▒░ ░ ░ ▒  ░  ░ ▒ ▒░   ░▒ ░ ▒░  ▒   ▒▒ ░░ ░░   ░ ▒░    ░    
                    ░        ░ ░ ░ ▒    ░ ░   ░ ░ ░ ▒    ░░   ░   ░   ▒      ░   ░ ░   ░      
                    ░ ░          ░ ░      ░  ░    ░ ░     ░           ░  ░         ░          
                    ░                                                                         
                                              COLOR AIM BOT - v1.1''', 'magenta'))
    print()
    print(colored('[Info]', 'green'), colored('Set enemies to', 'white'), colored('Purple', 'magenta'))
    print(colored('[Info]', 'green'),
          colored(f'Press {colored(TOGGLE_KEY, "magenta")} to toggle ON/OFF Colorant', 'white'))
    print(colored('[Info]', 'green'), colored(f'Press', 'white'), colored('F2', 'magenta'),
          colored('to toggle ON/OFF Detection Window', 'white'))
    # print(colored('[Info]', 'green'), colored('RightMB', 'magenta'), colored('= Aim bot,', 'white'))
    # print(colored('[Info]', 'green'), colored('LeftAlt', 'magenta'), colored('= Trigger bot', 'white'))
    # print(colored('[Info]', 'green'), colored('LeftCtrl', 'magenta'), colored('= Silent aim', 'white'))
    print(colored('[Info]', 'green'), colored('GitHub Repo:', 'white'),
          '\033[35;4m https://github.com/gemboran/colorant-ahk \033[0m')
    print(colored('[Info]', 'green'), colored('Made By', 'white'), colored('Gemboran', 'magenta'))
    status = 'Disabled'

    try:
        while True:
            if keyboard.is_pressed(TOGGLE_KEY):
                colorant.toggle()
                status = 'Enabled ' if colorant.toggled else 'Disabled'
            print(f'\r{colored("[Status]", "green")} {colored(status, "white")}', end='')
            time.sleep(0.01)
    except (KeyboardInterrupt, SystemExit):
        print(colored('\n[Info]', 'green'), colored('Exiting...', 'white') + '\n')
    finally:
        colorant.close()


if __name__ == '__main__':
    main()
