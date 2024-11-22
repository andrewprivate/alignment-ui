import time
import threading
import pyvisa


class PyvisaPowerMeter:
    def __init__(self, address):
        self.rm = pyvisa.ResourceManager()
        self.power_meter = self.rm.open_resource(address)

    def read_power_micro(self):
        """Read the power meter and return the power in uW"""
        power = (float(self.power_meter.query("MEAS:POW?")) * 1e6)
        return power

    def close(self):
        """Close the connection to the power meter, releasing the resources"""
        self.power_meter.close()
        self.rm.close()
        
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