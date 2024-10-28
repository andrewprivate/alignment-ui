import eel
import os

class App:
    def __init__(self):
        self.name = 'App'
        web_dir = os.path.join(os.path.dirname(__file__), 'web')
        eel.init(web_dir)

    def run(self):
        eel.start('index.html')
        print(f'{self.name} is running')