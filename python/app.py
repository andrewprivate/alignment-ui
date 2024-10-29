import eel
import os
import bottle
import asyncio
import cv2
from bottle import HTTPResponse
import time
import stage_control

class App:
    def __init__(self):
        self.app = bottle.Bottle()
        web_dir = os.path.join(os.path.dirname(__file__), '../web')
        eel.init(web_dir)

        # self.camera_in = cv2.VideoCapture(0)
        print('Starting stage control')
        stage_control.start(8080)
        self.setup_hooks()

    def setup_hooks(self):
        @eel.expose
        def say_hello_py(x):
            print(f'Hello from {x}')
            return f'Hello from {x}'
        
        @self.app.route('/api/video_feed')
        def video_feed():
            return HTTPResponse(self.gen_frames(), headers={'Content-Type': 'multipart/x-mixed-replace; boundary=frame'})
        


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

    async def run(self):
        eel.start('index.html', app=self.app)
        print(f'App is running')

   

    
