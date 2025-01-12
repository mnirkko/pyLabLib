from ... import device_thread



class LumelRE72ControllerThread(device_thread.DeviceThread):
    """
    Lumel RE72 temperature controller device thread.

    Device args:
        - ``conn``: serial connection parameters for RS485 adapter (usually port, a tuple containing port and baudrate,
            or a tuple with full specification such as ``("COM1", 9600, 8, 'N', 1)``)
        - ``daddr``: default device Modbus address

    Variables:
        - ``measurement/f``: last measured value in the floating point format (for temperature, it is specified in degrees)
        - ``measurement/i``: last measured value in the integer format (for temperature, it is specified in 0.1 degrees)
        - ``setpoint/f``: temperature setpoint value in the floating point format (for temperature, it is specified in degrees)
        - ``setpoint/i``: temperature setpoint value in the integer format (for temperature, it is specified in 0.1 degrees)
    """
    def connect_device(self):
        with self.using_devclass("Lumel.LumelRE72Controller",host=self.remote) as cls:
            self.device=cls(conn=self.conn,daddr=self.daddr)  # pylint: disable=not-callable
    def setup_task(self, conn, daddr=1, remote=None):  # pylint: disable=arguments-differ
        self.device_reconnect_tries=5
        self.conn=conn
        self.daddr=daddr
        self.remote=remote
        self.add_job("update_measurements",self.update_measurements,0.5)
        self.add_job("update_parameters",self.update_parameters,2)
        self.add_device_command("set_setpointi",post_update=["update_measurements","update_parameters"],limit_queue=1,on_full_queue="skip_oldest")
    def update_measurements(self):
        """Update current measurements"""
        if self.open():
            self.v["measurement/f"]=self.device.get_measurementf()
            self.v["measurement/i"]=self.device.get_measurementi()
            self.v["setpoint/f"]=self.device.get_setpointf()
            self.v["setpoint/i"]=self.device.get_setpointi()
        else:
            self.v["measurement/f"]=0
            self.v["measurement/i"]=0
            self.v["setpoint/f"]=0
            self.v["setpoint/i"]=0
            self.sleep(1.)