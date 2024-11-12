import eel
import os
import bottle
import asyncio
import cv2
from bottle import HTTPResponse
import time
import pictestingrs
import pyvisa
from pylablib.devices import Newport
from python.commands import Commands
from python.powermeter import PowerMeterThread

class App:
    def __init__(self):
        self.app = bottle.Bottle()
        web_dir = os.path.join(os.path.dirname(__file__), '../web')
        eel.init(web_dir, allowed_extensions=['.js', '.html', '.mjs'])

        self.camera_in = cv2.VideoCapture(0)
        print('Starting stage control')
        self.video_feed_port = pictestingrs.start()
        self.setup_hooks()

        self.commands = Commands(self)

        # Connect to power meter
        self.rm = pyvisa.ResourceManager()
        self.power_meter = self.rm.open_resource('USB0::0x1313::0x80BB::M01045161::INSTR')

        # Connect to picomotor controller
        self.controller = Newport.Picomotor8742( multiaddr=True)

    def setup_hooks(self):
        @eel.expose
        def say_hello_py(x):
            print(f'Hello from {x}')
            eel.start_video_feed(self.video_feed_port)
            return f'Hello from {x}'
        
        @eel.expose
        def start_power_meter():
            print('Starting power meter')
            self.pm_thread = PowerMeterThread(self)
            self.pm_thread.start()


        @eel.expose
        def stop_power_meter():
            if hasattr(self, 'pm_thread'):
                print('Stopping power meter')
                self.pm_thread.running = False
                self.pm_thread.join()

        @eel.expose
        def move_stage(addr, axis, step_size):
            if(axis == 'x'):
                self.controller.move_by(1, step_size, addr)
            elif(axis == 'y'):
                self.controller.move_by(2, step_size, addr)
            elif(axis == 'z'):
                self.controller.move_by(3, step_size, addr)
            self.controller.wait_move("all", addr=addr)

    def gen_frames(self):
        last_frame_time = 0
        last_display_time = time.time()
        while True:
            success, frame = self.camera_in.read()
            if not success:
                break
            else:
                ret, buffer = cv2.imencode('.bmp', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\nContent-Type: image/bmp\r\n\r\n' + frame + b'\r\n\r\n')

                frame_time = time.time()
                # Print frame rate
                if frame_time - last_display_time > 1:
                    print(f'Frame rate: {1 / (frame_time - last_frame_time)}')
                    last_display_time = frame_time
                last_frame_time = frame_time

    def update_power_meter(self, reading):
        eel.update_power_reading(reading)

    async def run(self):

        print(f'App is running')
        eel.start('index.html', app=self.app)
       
       

   

    
