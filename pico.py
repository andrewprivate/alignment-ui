import time
import pyvisa
from pylablib.devices import Newport

# Connect to the stage controllers
controller = Newport.Picomotor8742( multiaddr=True) 
addrs = controller.get_addr_map()

# Connect to power meter
rm = pyvisa.ResourceManager()
power_meter = rm.open_resource('USB0::0x1313::0x80BB::M01045161::INSTR')

def read_power_meter():
    return float(power_meter.query("MEAS:POW?")) * 1e6 # convert to uW

#print(read_power_meter())
# addr 1 is the stage on the right, addr 2 is the stage on the left
def optimize_axis(controller, axis, step_size, addr, noise_threshold=0.1):
    best_power = read_power_meter()
    best_position = controller.get_position(axis, addr)
    print(f"Initial power: {best_power} uW")
    print(f"Initial position: {best_position}")
    while True:
        controller.move_by(axis, step_size, addr)
        time.sleep(0.5)
        new_power = read_power_meter()
        if (new_power - best_power) >= noise_threshold:
           best_power = new_power
           best_position = controller.get_position(axis, addr)
           print(f"New best power: {best_power} uW")
           print(f"New best position: {best_position}")
        else:
           controller.move_by(axis, -2*step_size, addr)
           time.sleep(0.5)
           new_power = read_power_meter()
           if (new_power - best_power) >= noise_threshold:
               best_power = new_power
               best_position = controller.get_position(axis, addr)
               print(f"New best power: {best_power} uW")
               print(f"New best position: {best_position}")
           else:
               step_size /= 2
               if step_size < 100:
                   break

    controller.move_to(axis, best_position, addr)
               
    print(f"Final best power: {best_power} uW")
    print(f"Final best position: {best_position}")
    return best_position

def optimize_stage(controller, step_size, addr):
    #x = optimize_axis(controller, 1, step_size, addr)
    x = controller.get_position(1, addr)
    y = optimize_axis(controller, 2, step_size, addr)
    z = optimize_axis(controller, 3, step_size, addr)

    final_power = read_power_meter()
    return (x,y,z), final_power

def optimize_all_stages():
    #for addr in addrs:
    position, power = optimize_stage(controller, 1000, 1)
    print(f"Optimized stage 1 with position {position} with power {power} uW")

try:
    optimize_all_stages()
except KeyboardInterrupt:
    print("Optimization interrupted")
finally:
    controller.close()
    power_meter.close()
