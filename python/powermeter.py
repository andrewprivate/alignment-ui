import time
import threading


class PowerMeterThread(threading.Thread):
    def __init__(self, controller):
        threading.Thread.__init__(self)
        self.controller = controller
        self.running = True

    def read_power_meter(self):
        power = (float(self.controller.power_meter.query("MEAS:POW?")) * 1e6)
        formatted = f"{power:.4f} uW"
        return formatted

    def run(self):
        while self.running:
            time.sleep(0.1)
            reading = self.read_power_meter()
            self.controller.update_power_meter(reading)