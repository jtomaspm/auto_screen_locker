import subprocess
import time
from pynput import mouse, keyboard

config = {
    'home_network': "Xuxu's Home",                  # name of the network you're connected to at home
    'lock_screen_timeout': 5,                       # time without activity before locking screen in seconds
    'enabled_at_home': False,                        # if False, will only lock when not at home
    'network_check_timeout': 1800,                  # time between network checks in seconds 
}

shared_state = {
    'last_activity': time.time(),
    'hard_stop': False,
}

lock_screen                 = lambda: subprocess.call(["rundll32.exe", "user32.dll", "LockWorkStation"])
time_since_last_activity    = lambda: time.time() - shared_state['last_activity']
am_i_home                   = lambda: config['home_network'] in str(subprocess.check_output("netsh wlan show interfaces"))
should_i_stop               = lambda: not config['enabled_at_home'] and am_i_home()
should_i_lock               = lambda: time_since_last_activity() > config['lock_screen_timeout']

def handle_action(*args, **kwargs):
    shared_state['last_activity'] = time.time()
    shared_state['hard_stop'] = False

def main():
    mouse_listener = mouse.Listener(
        on_move=handle_action,
        on_click=handle_action,
        on_scroll=handle_action)
    keyboard_listener = keyboard.Listener(
        on_press=handle_action,
        on_release=handle_action)
    mouse_listener.start()
    keyboard_listener.start()

    while True:
        if should_i_stop():
            time.sleep(config['network_check_timeout'])
            continue
        while not shared_state['hard_stop']:
            if should_i_lock():
                lock_screen()
                shared_state['hard_stop'] = True
        time.sleep(5)
        
if __name__ == '__main__':
    main()