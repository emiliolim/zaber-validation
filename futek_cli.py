import clr
import System
clr.AddReference("FUTEK.Devices")
import FUTEK.Devices
from FUTEK.Devices import DeviceRepository

"""
Controls Futek Loadcell
Connects/Disconnects loadcell
Displays loadcell information
"""
class FUTEKDeviceCLI:
    def __init__(self):
        self.oFUTEKDeviceRepoDLL = self.connect()
        # Initialize and check for connected FUTEK devices (particularly USB225)
        devices = self.oFUTEKDeviceRepoDLL.DetectDevices()
        self.USB225_A = devices[0] if devices else None
        self.USB225_B = devices[1] if len(devices) > 1 else None
        self.USB225_C = devices[2] if len(devices) > 2 else None

        self.ModelNumber_A = FUTEK.Devices.Device.GetModelNumber(self.USB225_A)
        self.ModelNumber_B = FUTEK.Devices.Device.GetModelNumber(self.USB225_B) if self.USB225_B else "N/A"
        self.ModelNumber_C = FUTEK.Devices.Device.GetModelNumber(self.USB225_C) if self.USB225_C else "N/A"
        print(f"Model Number A: {self.ModelNumber_A}")
        print(f"Model Number B: {self.ModelNumber_B}")
        print(f"Model Number C: {self.ModelNumber_C}")  

        self.SerialNumber_A = FUTEK.Devices.Device.GetInstrumentSerialNumber(self.USB225_A)
        self.SerialNumber_B = FUTEK.Devices.Device.GetInstrumentSerialNumber(self.USB225_B) if self.USB225_B else "N/A"
        self.SerialNumber_C = FUTEK.Devices.Device.GetInstrumentSerialNumber(self.USB225_C) if self.USB225_C else "N/A"
        print(f"Serial Number A: {self.SerialNumber_A}")
        print(f"Serial Number B: {self.SerialNumber_B}")
        print(f"Serial Number C: {self.SerialNumber_C}")

        self.UnitCode_A = FUTEK.Devices.DeviceUSB225.GetChannelXUnitOfMeasure(self.USB225_A, 0)
        self.UnitCode_B = FUTEK.Devices.DeviceUSB225.GetChannelXUnitOfMeasure(self.USB225_B, 0) if self.USB225_B else "N/A"
        self.UnitCode_C = FUTEK.Devices.DeviceUSB225.GetChannelXUnitOfMeasure(self.USB225_C, 0) if self.USB225_C else "N/A"
        print(f"Unit of Measure A: {self.UnitCode_A}")
        print(f"Unit of Measure B: {self.UnitCode_B}")
        print(f"Unit of Measure C: {self.UnitCode_C}")

        self.OpenedConnection = True

        self.SamplingRate = FUTEK.Devices.DeviceUSB225.GetChannelXSamplingRate(self.USB225_A, 0)
        # available sampling rates: ['2.5', '5', '10', '16.6', '20', '50', '60', '100', '400', '1200', '2400', '4800']
        print(f"Sampling Rate: {self.SamplingRate} Hz")
        self.USB225_A.SetChannelXSamplingRate(0, "100") # Set sampling rate to 60 hz to adjust to python's loop speed
        self.USB225_B.SetChannelXSamplingRate(0, "100")
        if self.USB225_C:
            self.USB225_C.SetChannelXSamplingRate(0, "100")

        self.NormalData = FUTEK.Devices.DeviceUSB225.GetChannelXReading(self.USB225_A, 0)
        print(f"Sensor Reading: {self.NormalData:.3f}")

    def getNormalData_A(self):
        return FUTEK.Devices.DeviceUSB225.GetChannelXReading(self.USB225_A, 0)

    def getNormalData_B(self):
        return FUTEK.Devices.DeviceUSB225.GetChannelXReading(self.USB225_B, 0)

    def getNormalData_C(self):
        return FUTEK.Devices.DeviceUSB225.GetChannelXReading(self.USB225_C, 0)

    def connect(self):
        try:
            print("FUTEK Devices DLL initialized.")
            return FUTEK.Devices.DeviceRepository()
        except Exception as e:
            print(f"Error initializing FUTEK Devices DLL: {e}")
            return

    def stop(self):
        if not self.OpenedConnection:
            print("No open connection to close.")
            return

        self.oFUTEKDeviceRepoDLL.DisconnectAllDevices()
        if self.oFUTEKDeviceRepoDLL.DeviceCount > 0:
            print("A device is still connected.")
        else:
            print("Session closed.")

        self.SerialNumber = ""
        self.ModelNumber = ""
        self.UnitCode = 0

        self.OpenedConnection = False

    def exit(self):
        if self.OpenedConnection:
            self.stop()
        print("Exiting the CLI...")
        #System.Environment.Exit(0)

if __name__ == '__main__':
    cli = FUTEKDeviceCLI()
    while True:
        command = input("Enter command (start/stop/exit): ").strip().lower()
        if command == 'start':
            a= cli.getNormalData_A()
            b= cli.getNormalData_B()
            print(f"Sensor Reading A: {a:.3f}")
            print(f"Sensor Reading B: {b:.3f}")
        elif command == 'stop':
            cli.stop()
        elif command == 'exit':
            cli.exit()
        else:
            print("Unknown command. Please enter 'start', 'stop', or 'exit'.")
