"""
Title           : obislaser.py
Authors         : Miguel Maldonado
Date Created    : 03 Sepember 2025
Description     : A python USB controller for OBIS Laser
"""
import time
import serial
import serial.tools.list_ports

# OBIS Laser Commands (edit as needed)
CMD_QUERY_ID  = "*IDN?\r"                           # Query ID
CMD_LASER_ON  = "SOUR:AM:STAT ON\r"                 # Turn laser emission on
CMD_LASER_OFF = "SOUR:AM:STAT OFF\r"                # Turn laser emission off
CMD_SET_POWER = "SOUR:POW:LEV:IMM:AMPL {:.3f}\r"    # Set the power in Watts
CMD_GET_ERRS  = "SYST:ERR:COUN?\r"                  # Get number of errors
CMD_NEXT_ERR  = "SYST:ERR:NEXT?\r"                  # Get error message


class LaserController:
    """
    A small Python class to control a Coherent OBIS laser over a serial port.
    """

    def __init__(self, baudrate=115200, timeout=1):
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None

    def _get_laser_serial(self, baudrate=115200, timeout=1):
        """
        Scan through available COM ports, open each one, send an ID query,
        check if it matches "Coherent" or "OBIS".
        Return the port name if found, else None.
        """

        # Get a list of available ports
        ports = serial.tools.list_ports.comports()
        for p in ports:
            port_name = p.device

            try:
                # Open the port
                ser = serial.Serial(
                    port=port_name,
                    baudrate=baudrate,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    timeout=timeout
                )
                time.sleep(0.5)  # short delay

                # Flush input buffer
                ser.reset_input_buffer()

                # Send query
                ser.write(CMD_QUERY_ID.encode('ascii'))
                time.sleep(0.2)

                # Read response
                response = ser.read_all().decode('ascii', errors='ignore').strip()

                # Check if response indicates a Coherent OBIS
                if "Coherent" in response or "OBIS" in response:
                    self.port = port_name
                    return ser
            
                ser.close()
            except Exception:
                pass

        print("No OBIS laser found.")
        return None
    
    def open(self):
        self.ser = self._get_laser_serial(self.baudrate, self.timeout)
        if self.ser is not None:
            print(f"Opened serial port {self.ser.port}.")
        else:
            print(f"Failed to open serial port.")
        return self.ser is not None

    def close(self):
        """Close the serial port."""
        try:
            if self.ser is not None and self.ser.is_open:
                self.ser.close()
                print(f"Closed serial port {self.port}.")
            self.ser = None
            return True
        except Exception as e:
            print(f"Error closing serial port: {e}")
            return False

    def turn_on(self):
        """Turn the laser on."""
        if not self._check_port():
            return
        return self._send_command(CMD_LASER_ON, "Laser ON")
        

    def turn_off(self):
        """Turn the laser off."""
        if not self._check_port():
            return
        return self._send_command(CMD_LASER_OFF, "Laser OFF")

    def set_power_mw(self, power_mw):
        """
        Set the laser power in milliwatts.
        The OBIS command requires watts, so convert mW -> W.
        """
        if not self._check_port():
            return
        power_w = power_mw / 1000.0
        cmd = CMD_SET_POWER.format(power_w)
        return self._send_command(cmd, f"Set power to {power_mw} mW")

    def get_errors(self):
        """Get the error message from the laser."""
        if not self._check_port():
            return
        return self._send_command(CMD_GET_ERRS, "Error message")

    def next_error(self):
        """Get the next error message from the laser."""
        if not self._check_port():
            return
        return self._send_command(CMD_NEXT_ERR, "Next error message")

    def _send_command(self, command, label=""):
        """Send a command and read back any response."""
        if not self._check_port():
            return
        self.ser.write(command.encode("ascii"))
        time.sleep(0.1)
        return self.ser.read_all().decode("ascii").strip()

    def _check_port(self):
        if self.ser is None or not self.ser.is_open:
            print("Error: Serial port is not open.")
            return False
        return True
    
    def __del__(self):
        self.close()

# ---------------------------------------------------------------------
# Example usage (if running directly, not from Blender):
# ---------------------------------------------------------------------
if __name__ == "__main__":
    lc = LaserController()
    if not lc.open():
        print("Failed to open laser serial port.")
        exit(1)
    lc.open()

    # Turn on with 0 mW
    lc.set_power_mw(0)
    lc.turn_on()
    time.sleep(2)  # Wait 2 seconds just for demonstration

    # Set power to 20 mW
    lc.set_power_mw(20)
    time.sleep(2)

    # Turn off
    lc.turn_off()
    lc.close()
