import eel
import pyvisa
from pylablib.devices import Newport
import scipy
import numpy as np
from time import sleep

def align(app):
    print("Aligning fiber")

    controller = Newport.Picomotor8742( multiaddr=True) 

    # Connect to power meter
    rm = pyvisa.ResourceManager()
    power_meter = rm.open_resource('USB0::0x1313::0x80BB::M01045161::INSTR')

    def read_power_meter():
        sample_num = 10
        power_sum = 0
        counter = 0
        for i in range(sample_num):
            val = float(power_meter.query("MEAS:POW?")) * 1e6 # convert to uW
            if np.isnan(val) or np.isinf(val):
                continue
            power_sum += val
            counter += 1

        if counter == 0:
            return np.nan
        
        return power_sum / counter


    def optimize_stage(controller, step_size, addr):

        # x0 = np.array([0,0])
        # last_position = np.array([0,0])
        # stop = False
        # def objective(x):
        #     nonlocal last_position
        #     nonlocal stop
        #     diff = x - last_position
        #     steps = np.round(diff)
        #     steps = steps.astype(int)
        #     last_position = x

        #     if steps[0] == 0 and steps[1] == 0:
        #         stop = True

        #     print(f"Moving to position {x} with steps {steps}")
        #     controller.move_by(2, steps[0], addr)
        #     controller.move_by(3, steps[1], addr)
        #     controller.wait_move("all", addr=addr)

        #     power_sum = 0
        #     for i in range(10):
        #         power_sum += read_power_meter()

        #     power = power_sum / 10

        #     print(f"Power: {power} uW at position {x}")
        #     eel.add_point(x[0], x[1], power)
        #     return -power
        
        # def callback(intermediate_result):
        #     if stop:
        #         raise StopIteration
            


        
        # init_size =  1000
        # init = np.array([[init_size,init_size],[init_size,-init_size],[-init_size,init_size]])
        # result = scipy.optimize.minimize(objective, x0, method='Nelder-Mead', callback=callback, options={'initial_simplex':init, 'xatol':1, 'adaptive':True})

        segment_angle = 0
        segment_length = 1000

        for iteration in range(4):
            
            while True:
                segment_displacement = [segment_length * np.cos(segment_angle), segment_length * np.sin(segment_angle)]
                # make it int
                segment_steps = np.round(segment_displacement).astype(int)

                # y, z, power
                measurements = []

                pos = controller.get_position("all", addr)
                measurements.append([pos[1], pos[2], read_power_meter()])

                if segment_steps[0] != 0:
                    controller.move_by(2, segment_steps[0], addr)
                if segment_steps[1] != 0:
                    controller.move_by(3, segment_steps[1], addr)

                while True:
                    moving = controller.is_moving("all", addr)
                    # array of bools
                    if not any(moving):
                        break
                    pos = controller.get_position("all", addr)
                    measurements.append([pos[1], pos[2], read_power_meter()])

                pos = controller.get_position("all", addr)
                measurements.append([pos[1], pos[2], read_power_meter()])

                # Deduplicate measurements
                dedup = []
                for m in measurements:
                    # Check nan and inf
                    if np.isnan(m[2]) or np.isinf(m[2]):
                        continue
                    if len(dedup) == 0 or dedup[-1][0] != m[0] or dedup[-1][1] != m[1]:
                        dedup.append(m)

                measurements = dedup
                print("Measurement length: ", len(measurements))
                if len(measurements) < 15:
                    print("Not enough measurements")
                    continue

                # Lowpass filter power
                power = np.array([m[2] for m in measurements])
                b, a = scipy.signal.butter(3, 0.1)
                power = scipy.signal.filtfilt(b, a, power)
                for i, m in enumerate(measurements):
                    m[2] = power[i]


                for measurement in measurements:
                    eel.add_point(measurement[0], measurement[1], measurement[2])


                # Find peak
                max_power = 0
                max_index = 0
                for i, m in enumerate(measurements):
                    if m[2] > max_power:
                        max_power = m[2]
                        max_index = i

                print(f"Max power: {max_power} at {measurements[max_index][0]}, {measurements[max_index][1]}")

                # Three cases
                # 1. Peak is at left edge (<10%)
                # 2. Peak is at right edge (>90%)
                # 3. Peak is in the middle
                threshold = 0.10

                if max_index < len(measurements) * threshold:
                    print("Peak is at left edge")

                    # Move back to 20% of the way
                    controller.move_by(2, -round(segment_steps[0] * (1 - threshold * 2)), addr)
                    controller.wait_move(2, addr=addr)
                    controller.move_by(3, -round(segment_steps[1] * (1 - threshold * 2)), addr)
                    controller.wait_move(3, addr=addr)
                    

                        
                    segment_length = segment_length / 2
                    segment_length = max(segment_length, 500)

                    # Flip angle
                    segment_angle += np.pi
            
                elif max_index > len(measurements) * (1 - threshold):
                    print("Peak is at right edge")

                    # Move back to 20% of the way
                    controller.move_by(2, -round(segment_steps[0] * (threshold * 2)), addr)
                    controller.wait_move(2, addr=addr)
                    controller.move_by(3, -round(segment_steps[1] * (threshold * 2)), addr)
                    controller.wait_move(3, addr=addr)

                    segment_length = segment_length * 2
                    segment_length = min(segment_length, 10000)
                else:
                    print("Peak is in the middle")

                    # Move to peak
                    peak_measurement = measurements[max_index]
                    first_measurement = measurements[0]
                    diff_pos = np.array([peak_measurement[0] - first_measurement[0], peak_measurement[1] - first_measurement[1]])
                    diff_steps = np.round(diff_pos).astype(int)
                    controller.move_by(2, diff_steps[0]-segment_steps[0], addr)
                    controller.wait_move(2, addr=addr)
                    controller.move_by(3, diff_steps[1]-segment_steps[1], addr)
                    controller.wait_move(3, addr=addr)

                    segment_length = 1000
                    segment_angle = segment_angle + np.pi / 2

                    break
        
        x0 = np.array([0,0])
        last_position = np.array([0,0])
        stop = False
        def objective(x):
            nonlocal last_position
            nonlocal stop
            diff = x - last_position
            steps = np.round(diff)
            steps = steps.astype(int)
            last_position[0] = last_position[0] + steps[0]
            last_position[1] = last_position[1] + steps[1]

            if steps[0] == 0 and steps[1] == 0:
                stop = True

            print(f"Moving to position {x} with steps {steps}")
            controller.move_by(2, steps[0], addr)
            controller.wait_move(2, addr=addr)
            controller.move_by(3, steps[1], addr)
            controller.wait_move(3, addr=addr)

            sleep(0.01)
            power = read_power_meter()

            pos = controller.get_position("all", addr)
            print(f"Power: {power} uW at position {pos}")
            eel.add_point(pos[1], pos[2], power)
            return -power
        
        def callback(intermediate_result):
            if stop:
                raise StopIteration
            


        
        init_size = 50
        init = np.array([[init_size,init_size],[init_size,-init_size],[-init_size,init_size]])
        result = scipy.optimize.minimize(objective, x0, method='Nelder-Mead', callback=callback, options={'initial_simplex':init, 'xatol':1, 'adaptive':True})

        # Move to final position
        final_position = result.x
        diff = final_position - last_position
        steps = np.round(diff).astype(int)
        controller.move_by(2, steps[0], addr)
        controller.wait_move(2, addr=addr)
        controller.move_by(3, steps[1], addr)
        controller.wait_move(3, addr=addr)

        pos = controller.get_position("all", addr)

        return pos, -result.fun

    def optimize_all_stages():
        position, power = optimize_stage(controller, 0.01, 1)
        print(f"Optimized stage 1 with position {position} with power {power} uW")

    try:
        optimize_all_stages()
    except KeyboardInterrupt:
        print("Optimization interrupted")
    finally:
        controller.close()
        power_meter.close()
    