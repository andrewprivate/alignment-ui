import serial.tools.list_ports
from zaber_motion import Units
from zaber_motion.ascii import Connection
from zaber_motion import Measurement


class StageController:
    def __init__(self, x_axis_serial_id, y_axis_serial_id, z_axis_serial_id):
        self.x_axis_serial_id = x_axis_serial_id
        self.y_axis_serial_id = y_axis_serial_id
        self.z_axis_serial_id = z_axis_serial_id

        self.x_axis = None
        self.y_axis = None
        self.z_axis = None

        self.connections = []

    def __enter__(self):
        self.connect_to_stage()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        for connection in self.connections:
            connection.close()
        connections = []

    def connect_to_stage(self):
        # Find serial ports
        ports = serial.tools.list_ports.comports()
        for port, desc, hwid in sorted(ports):
            # Test each port
            try:
                connection = Connection.open_serial_port(port)
                # Try detecting devices
                print("Trying port {}".format(port))
                try:
                    device_list = connection.detect_devices()
                    print("Found {} devices".format(len(device_list)))
                    # Check each device
                    for device in device_list:
                        print(device.identity)
                        if device.serial_number == self.x_axis_serial_id:
                            self.x_axis = device.get_axis(1)
                        elif device.serial_number == self.y_axis_serial_id:
                            self.y_axis = device.get_axis(1)
                        elif device.serial_number == self.z_axis_serial_id:
                            self.z_axis = device.get_axis(1)

                    self.connections.append(connection)
                except:
                    print("Failed to detect devices on port {}".format(port))
                    connection.close()
            except:
                print("Failed to open port {}".format(port))

        if self.x_axis is None:
            print("Failed to find x-axis")
        else:
            print("Found x-axis {}".format(self.x_axis))

        if self.y_axis is None:
            print("Failed to find y-axis")
        else:
            print("Found y-axis {}".format(self.y_axis))

        if self.z_axis is None:
            print("Failed to find z-axis")
        else:
            print("Found z-axis {}".format(self.z_axis))

        return self.x_axis is not None and self.y_axis is not None and self.z_axis is not None
    
    def are_all_axis_connected(self):
        return self.x_axis is not None and self.y_axis is not None and self.z_axis is not None
        
    def home(self):
        self.x_axis.home(wait_until_idle=False)
        self.y_axis.home(wait_until_idle=False)
        self.z_axis.home(wait_until_idle=False)

        # Wait for all axes to finish homing
        self.wait_until_idle()
    
    def wait_until_idle(self):
        self.x_axis.wait_until_idle()
        self.y_axis.wait_until_idle()
        self.z_axis.wait_until_idle()

    def get_x(self):
        return self.x_axis
    
    def get_y(self):
        return self.y_axis
    
    def get_z(self):
        return self.z_axis
    
    def get_velocity_units(self, unit):
        if unit == Units.LENGTH_MILLIMETRES:
            return Units.VELOCITY_MILLIMETRES_PER_SECOND
        elif unit == Units.LENGTH_MICROMETRES:
            return Units.VELOCITY_MICROMETRES_PER_SECOND
        elif unit == Units.LENGTH_NANOMETRES:
            return Units.VELOCITY_NANOMETRES_PER_SECOND
        else:
            print("Unsupported unit")
            exit(1)

    def move_staged(self, axis, position, unit = Units.NATIVE, start_velocity = 0, end_velocity = 0, precise_distance_start = 0, precise_distance_end = 0, wait_until_idle = True):
        velocity_unit = self.get_velocity_units(unit)
        max_speed = axis.settings.get('maxspeed', unit=velocity_unit)
        if start_velocity == 0 or start_velocity > max_speed:
            start_velocity = max_speed

        if end_velocity == 0 or end_velocity > max_speed:
            end_velocity = max_speed

        axis_number = axis.axis_number
        device = axis.device
        numstreams = device.settings.get('stream.numstreams')
        start_position = axis.get_position(unit=unit)

        if numstreams < 1:
            print("Streams are not supported on this device")
            exit(1)

        if axis_number > numstreams:
            print("Streams {} is not supported on this device".format(axis_number))
            exit(1)

        stream = device.streams.get_stream(axis_number)
        stream.setup_live(axis_number)

        stream.cork()

        dist = abs(position - start_position)
        sign = 1 if position > start_position else -1

        start_dst = min(precise_distance_start, dist - precise_distance_end)
        if start_dst > 0:
            stream.set_max_speed(start_velocity, velocity_unit)
            start_position += start_dst * sign
            stream.line_absolute(
                Measurement(start_position, unit=unit),
            )
            dist -= start_dst
        
        middle_dist = dist - precise_distance_end
        if middle_dist > 0:
            stream.set_max_speed(max_speed, velocity_unit)
            start_position += middle_dist * sign
            stream.line_absolute(
                Measurement(start_position, unit=unit),
            )
            dist -= middle_dist

        if dist > 0:
            stream.set_max_speed(end_velocity, velocity_unit)
            stream.line_absolute(
                Measurement(position, unit=unit),
            )

        stream.uncork()

        if wait_until_idle:
            self.wait_until_idle()
    
        return stream
    
    
    def home(self, homeX = True, homeY = True, homeZ = True):
        "Move the stage to the home position"
        if homeX:
            self.x_axis.home(wait_until_idle=False)
        if homeY:
            self.y_axis.home(wait_until_idle=False)
        if homeZ:
            self.z_axis.home(wait_until_idle=False)

        self.wait_until_idle()

    def move_to(self, x = None, y = None, z = None, unit = Units.LENGTH_MILLIMETRES):
        "Move the stage to the specified position in mm"
        
        if x is not None:
            self.x_axis.move_absolute(x, unit, wait_until_idle=False)

        if y is not None:
            self.y_axis.move_absolute(y, unit, wait_until_idle=False)

        if z is not None:
            self.z_axis.move_absolute(z, unit, wait_until_idle=False)

        if x is not None:
            self.x_axis.wait_until_idle()
        
        if y is not None:
            self.y_axis.wait_until_idle()

        if z is not None:
            self.z_axis.wait_until_idle()
        

    def get_position(self, unit = Units.LENGTH_MILLIMETRES):
        x = self.x_axis.get_position(unit)
        y = self.y_axis.get_position(unit)
        z = self.z_axis.get_position(unit)
        return x, y, z
    
    def get_scale(self, unit = Units.LENGTH_MILLIMETRES):
        x = self.x_axis.settings.convert_to_native_units("pos", 1, unit)
        y = self.y_axis.settings.convert_to_native_units("pos", 1, unit)
        z = self.z_axis.settings.convert_to_native_units("pos", 1, unit)

        return x, y, z

        
 