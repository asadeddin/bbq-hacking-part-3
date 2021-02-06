import pygatt
import datetime
import requests

# Connect to the device
connect_key = bytearray.fromhex("2107060504030201b8220000000000") # Update this with correct connection key you obtained in part 2
enable_notifications = bytearray.fromhex("0b0100000000") # This value is correct, no need to update
bbq_mac = "34:14:b5:47:26:7a" # Update this with your BBQ device's MAC address


adapter = pygatt.GATTToolBackend()

def fahrenheit(celcius):
    return int(round(celcius * (9/5.0) + 32))

# Process and save the realtime data
def handle_notification(handle, value):
    """
    handle -- integer, characteristic read handle the data was received on
    value -- bytearray, the data returned in the notification
    """
    temps = {"mac":bbq_mac, "timestamp": str(datetime.datetime.now())}
    for i in range(0,8,2):
        celcius = int(int.from_bytes(value[i:i+2], "little") / 10)
        f_degrees = fahrenheit(celcius)
        temps[f"probe_{int(i/2)+1}"] = f_degrees
    try:
        r = requests.post('http://127.0.0.1:5000/smart_thermo', json=temps)
        print(r.status_code)
    except:
        pass



try:
    adapter.start()

    try:
        print("Trying to connect")
        device = adapter.connect(bbq_mac,timeout=20)
    except:
        print("Couldn't connect to the device, retrying...")
        device = adapter.connect(bbq_mac,timeout=20)

    # Send the connection key to the 0x29
    print("Pairing with the device...")
    device.char_write_handle(0x0029, connect_key)
    # Enable notifications by writing to 0x34
    device.char_write_handle(0x0034, enable_notifications)
    print("Connected with the device.")

    # Subscribe and listen for notifications of the realtime data
    try:
        device.subscribe("0000fff4-0000-1000-8000-00805f9b34fb", callback=handle_notification)
    except Exception as e:
        try:
            device.subscribe("0000fff4-0000-1000-8000-00805f9b34fb", callback=handle_notification)
        except:
            pass

    input("Enter any key to quit....")


finally:
    adapter.stop()
