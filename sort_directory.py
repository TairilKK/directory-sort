import os
import json

def configuration_check(config_path):
    try:
        with open(config_path, 'r') as json_file:
            config = json.loads(json_file.read())
    except:
        print('Missing "config.json" file.')
        exit(-1)

    if not os.path.exists(config['INP_DIRECTORY']):
        inp_dir = config['INP_DIRECTORY']
        print(f'{inp_dir}.')
        exit(-2)

    if not os.path.exists(config['OUT_DIRECTORY']):
        config['OUT_DIRECTORY'] = config['INP_DIRECTORY']

    if config['MAX_FILE_SIZE'] < 1:
        config['MAX_FILE_SIZE'] = 512 * 1024

    return config['INP_DIRECTORY'], config['OUT_DIRECTORY'], config['IGNORE_FILES'], config['MAX_FILE_SIZE']

def move_file(file, in_dir, out_dir, max_byte_size):
    if os.path.getsize(f'{in_dir}/{file}') > max_byte_size:
        return

    _, file_ext = os.path.splitext(file)
    file_ext = file_ext.replace('.', '')
    if not os.path.exists(f'{OUT_DIRECTORY}/{file_ext}'):
        os.mkdir(f'{out_dir}/{file_ext}')
    os.replace(f'{in_dir}/{file}', f'{out_dir}/{file_ext}/{file}')

def first_run(INP_DIRECTORY, OUT_DIRECTORY, IGNORE, MAX_FILE_SIZE):
    for file in os.listdir(INP_DIRECTORY):
        if file in IGNORE:
            continue

        if not os.path.isdir(f'{INP_DIRECTORY}/{file}'):       
            move_file(file, INP_DIRECTORY, OUT_DIRECTORY, MAX_FILE_SIZE)
           

import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

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
            move_file(file, INP_DIRECTORY, OUT_DIRECTORY, MAX_FILE_SIZE)




def monitor_directory(INP_DIRECTORY, OUT_DIRECTORY, IGNORE, MAX_FILE_SIZE):
    event_handler = MyHandler(INP_DIRECTORY, OUT_DIRECTORY, IGNORE, MAX_FILE_SIZE)
    observer = Observer()
    observer.schedule(event_handler, INP_DIRECTORY, recursive=False)  # recursive=False oznacza, że nie monitorujemy podkatalogów
    observer.start()

    try:
        while True:
            time.sleep(1)  
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == '__main__':
    CONFIG_PATH = './config.json'
    INP_DIRECTORY, OUT_DIRECTORY, IGNORE, MAX_FILE_SIZE = configuration_check('./config.json')
    first_run(INP_DIRECTORY, OUT_DIRECTORY, IGNORE, MAX_FILE_SIZE)
    monitor_directory(INP_DIRECTORY, OUT_DIRECTORY, IGNORE, MAX_FILE_SIZE)