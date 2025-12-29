
import usb.core
import usb.util
from escpos.printer import Usb

def find_usb_printer():
    """
    Automatically detects a USB thermal printer and returns its VID & PID.
    """
    # Find all USB devices
    devices = usb.core.find(find_all=True)

    for device in devices:
        # Check if the device class is 'Printer' (class code 7)
        if device.bDeviceClass == 7:
            print(f"Printer Found: VID={hex(device.idVendor)}, PID={hex(device.idProduct)}")
            return device.idVendor, device.idProduct

    print("No USB printer found.")
    return None, None