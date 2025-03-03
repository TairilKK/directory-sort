import pystray
from PIL import Image
import threading
import time
import os
import json
import sys
import threading
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def configuration_check(config_path):
    try:
        with open(config_path, 'r') as json_file:
            config = json.loads(json_file.read())
    except:
        print('Missing "config.json" file.')
        sys.exit(-1)

    if not os.path.exists(config['INP_DIRECTORY']):
        inp_dir = config['INP_DIRECTORY']
        print(f'{inp_dir}.')
        sys.exit(-2)

    if not os.path.exists(config['OUT_DIRECTORY']):
        config['OUT_DIRECTORY'] = config['INP_DIRECTORY']

    if config['MAX_FILE_SIZE'] < 1:
        config['MAX_FILE_SIZE'] = 512 * 1024

    return config['INP_DIRECTORY'], config['OUT_DIRECTORY'], config['IGNORE_FILES'], config['MAX_FILE_SIZE']

def move_file(file, in_dir, out_dir, max_byte_size):
    if os.path.getsize(f'{in_dir}/{file}') > max_byte_size:
        return
    
    while not wait_for_download_completion(f'{INP_DIRECTORY}/{file}'):
        pass 
    
    
    file_name, file_ext = os.path.splitext(file)
    file_ext = file_ext.replace('.', '')
    if not os.path.exists(f'{OUT_DIRECTORY}/{file_ext}'):
        try:
            os.mkdir(f'{out_dir}/{file_ext}')
        except:
            pass
    
    count = 0
    new_file = file
    while os.path.exists(f'{out_dir}/{file_ext}/{new_file}'):
        new_file = f'{file_name}_{count:03}.{file_ext}'
        count+=1

    os.replace(f'{in_dir}/{file}', f'{out_dir}/{file_ext}/{new_file}')

def first_run(INP_DIRECTORY, OUT_DIRECTORY, IGNORE, MAX_FILE_SIZE):
    threads = []
    for file in os.listdir(INP_DIRECTORY):
        if file in IGNORE:
            continue
        
        if not os.path.isdir(f'{INP_DIRECTORY}/{file}'):  
            threads.append(threading.Thread(target=move_file, args=(file, INP_DIRECTORY, OUT_DIRECTORY, MAX_FILE_SIZE))) 

    for thread in threads:
        thread.start()  



class MyHandler(FileSystemEventHandler):
    def __init__(self, INP_DIRECTORY, OUT_DIRECTORY, IGNORE, MAX_FILE_SIZE):
        super().__init__()
        self.INP_DIRECTORY = INP_DIRECTORY
        self.OUT_DIRECTORY = OUT_DIRECTORY
        self.IGNORE = IGNORE
        self.MAX_FILE_SIZE = MAX_FILE_SIZE

    def on_created(self, event):
        if not event.is_directory:  
            file = os.path.basename(event.src_path)
            thread = threading.Thread(target=move_file, args=(file, INP_DIRECTORY, OUT_DIRECTORY, MAX_FILE_SIZE))
            thread.start()

def monitor_directory(INP_DIRECTORY, OUT_DIRECTORY, IGNORE, MAX_FILE_SIZE):
    event_handler = MyHandler(INP_DIRECTORY, OUT_DIRECTORY, IGNORE, MAX_FILE_SIZE)
    observer = Observer()
    observer.schedule(event_handler, INP_DIRECTORY, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(60)  
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def wait_for_download_completion(file_path, wait_time=0.05):
    initial_size = os.path.getsize(file_path)
    time.sleep(wait_time)
    return initial_size == os.path.getsize(file_path)

def background_task():
    CONFIG_PATH = './config.json'
    INP_DIRECTORY, OUT_DIRECTORY, IGNORE, MAX_FILE_SIZE = configuration_check('./config.json')
    first_run(INP_DIRECTORY, OUT_DIRECTORY, IGNORE, MAX_FILE_SIZE)
    monitor_directory(INP_DIRECTORY, OUT_DIRECTORY, IGNORE, MAX_FILE_SIZE)


def on_exit(icon, item):
    icon.stop()

def create_system_tray_icon():
    image = Image.open("icon.png")
    
    menu = pystray.Menu(
        pystray.MenuItem("Zamknij", on_exit)
    )
    
    icon = pystray.Icon("Download sort", image, "Moja Aplikacja", menu)
    
    icon.run()

if __name__ == "__main__":
    background_thread = threading.Thread(target=background_task)
    background_thread.daemon = True
    background_thread.start()
    create_system_tray_icon()