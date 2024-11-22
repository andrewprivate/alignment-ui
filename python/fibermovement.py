from pylablib.devices import Newport

class PicomotorAxis:
    def __init__(self, controller, addr, axis):
        self.controller = controller
        self.addr = addr
        self.axis = axis

    
    def get_position(self):
        """Get the current position of the motor"""
        return self.controller.get_position(axis=self.axis, addr=self.addr)
    
    def move_by(self, steps):
        """Move the motor by the specified number of steps"""
        self.controller.move_by(axis=self.axis, steps=steps, addr=self.addr)

    def is_moving(self):
        """Check if the motor is currently moving"""
        return self.controller.is_moving(axis=self.axis, addr=self.addr)
    
    def wait_move(self):
        """Wait until the motor stops moving"""
        return self.controller.wait_move(axis=self.axis, addr=self.addr)


class PicomotorDevice:
    def __init__(self, controller, addr):
        self.controller = controller
        self.addr = addr

        self.axis_list = self.get_all_axes()
        self.axes = [ PicomotorAxis(controller, addr, axis) for axis in self.axis_list ]

    def get_axis(self, axis = None, index = None):
        """Get the axis object for the specified axis or index"""
        if axis is not None:
            return self.axes[self.axis_list.index(axis)]
        if index is not None:
            return self.axes[index]
        return None
    
    def get_all_axes(self):
        """Get a list of all axes for the device"""
        return self.axis
    
    def get_positions(self):
        """Get the current positions of all axes"""
        return self.controller.get_position("all", self.addr)

class PicomotorController:
    def __init__(self, index):
        self.controller = Newport.Picomotor8742(conn=index, multiaddr=True)
        addr, conflict = self.controller.get_addr_map()
        self.device_addresses = addr
        self.devices = [ PicomotorDevice(self.controller, addr) for addr in self.device_addresses ]
    
    def get_device(self, addr = None, index = None):
        """Get the device object for the specified address or index"""
        if addr is not None:
            return self.devices[self.device_addresses.index(addr)]
        if index is not None:
            return self.devices[index]
        return None
    
    def get_all_devices(self):
        """Get a list of all devices connected to the controller"""
        return self.devices
    
    def close(self):
        """Close the connection to the controller, releasing the resources"""
        self.controller.close()
        