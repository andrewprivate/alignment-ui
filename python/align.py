import eel
import pyvisa
from pylablib.devices import Newport
import scipy

def align(app):
    print("Aligning fiber")

    controller = Newport.Picomotor8742( multiaddr=True) 
    addrs = controller.get_addr_map()

    # Connect to power meter
    rm = pyvisa.ResourceManager()
    power_meter = rm.open_resource('USB0::0x1313::0x80BB::M01045161::INSTR')

    def read_power_meter():
        return float(power_meter.query("MEAS:POW?")) * 1e6 # convert to uW


    def optimize_stage(controller, step_size, addr):
        current_x = controller.get_position(1, addr) # This stays constant
        current_y = controller.get_position(2, addr)
        current_z = controller.get_position(3, addr)

        x0 = [current_y, current_z]

        def objective(x):
            controller.move_to(2, x[0], addr)
            controller.move_to(3, x[1], addr)
            power = read_power_meter()
            print(f"Power: {power} uW at position {x}")
            eel.add_point(x[0], x[1], power)
            return -power
        
        result = scipy.optimize.minimize(objective, x0, method='Nelder-Mead')

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
    