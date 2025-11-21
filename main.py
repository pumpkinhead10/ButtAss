import asyncio
import ctypes
import subprocess
from pyfiglet import figlet_format

from pymobiledevice3.tunneld.api import async_get_tunneld_devices
from pymobiledevice3.services.dvt.dvt_secure_socket_proxy import DvtSecureSocketProxyService
from pymobiledevice3.services.dvt.instruments.location_simulation import LocationSimulation

from pymobiledevice3.usbmux import list_devices
from pymobiledevice3.lockdown import create_using_usbmux
from pymobiledevice3.services.amfi import AmfiService
from pymobiledevice3.exceptions import DeviceHasPasscodeSetError
from pymobiledevice3.services.mobile_image_mounter import auto_mount


def developer_mode_on():
    lockdown = create_using_usbmux(list_devices()[0].serial)
    if not lockdown.paired:
        lockdown.pair()
    if not lockdown.developer_mode_status:
        try:
            AmfiService(lockdown).enable_developer_mode()
            asyncio.run(auto_mount(lockdown))
        except DeviceHasPasscodeSetError: 
            print("[Error] Device has a passcode set")
            print("Remove the passcode")
            print("Privacy & Security -> [scroll down] -> Developer Mode -> On")
            exit(0)
    
    lockdown.close()

async def get_device():
    await asyncio.create_subprocess_exec(
        "pymobiledevice3", "remote", "tunneld",
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
    )
    attempt = 0
    while attempt < 10:
        try:
            rsds =  await async_get_tunneld_devices()

            if rsds:
                return rsds[0]
            else:
                await asyncio.sleep(2)
        except OSError as e:
            if getattr(e, "winerror", None) == 1231:
                await asyncio.sleep(2)
            else:
                return None

        attempt += 1
    
def setLocation(latitude, longitude):
    developer_mode_on()
    device = asyncio.run(get_device())
    if device == None:
        print("[ERROR] NO DEVICES FOUND")
        exit(-1)
    if device == None:
        return None
    with DvtSecureSocketProxyService(device) as dvt:
        LocationSimulation(dvt).clear()
        LocationSimulation(dvt).set(latitude, longitude)
        print(f"[SUCCESS] Location set to {latitude}, {longitude}")
    
    
if __name__ == "__main__":
    if not (ctypes.windll.shell32.IsUserAnAdmin() != 0):
        print("[ERROR] THIS PROGRAM REQUIRES ADMINISTRATIVE PRIVILEGES!")
        exit(-1)

    print(figlet_format("ButtAss", font="slant"))
    print("IOS location spoofer, written by pumpkinhead10")
    
    print("ButtAss – For Educational & Research Use Only")
    print("--------------------------------------------------------")
    print("This software is created solely for learning, testing, and")
    print("security research. It must NOT be used to cheat, fake")
    print("location-based attendance, violate school policies, break")
    print("local laws, or interfere with any services.")
    print("")
    print("By using this tool, you accept full responsibility for your")
    print("actions. The author (pumpkinhead10) is not liable for any")
    print("misuse, damage, academic violations, or legal consequences")
    print("resulting from improper use.")
    print("")
    print("Use ethically. Do not break the law.")


    print("1) Singapore Institute of Management")
    print("2) Singapore University of Social Sciences")
    print("3) Singapore Polytechnic")
    print("4) 19th street (Yangon)")
    print("5) custom")
    print("6) exit")

    while True:
        user = input(": ")
        match user.strip():
            case "1":
                setLocation(1.3295728138309617, 103.77622813639634)
            case "2":
                setLocation(1.3292955176478871, 103.77630398057424)
            case "3":
                setLocation(1.3098936850448175, 103.77750657687632)
            case "4":
                setLocation(16.774979791056207, 96.14948163665635)
            case "5":
                latitudeitude = float(input("latitudeitude: "))
                longitude = float(input("longitude: "))
                setLocation(latitudeitude, longitude)
            case "6":
                exit(0)
            case _:
                pass
    


#   @@@ My Approach @@@
#create a tcp tunnel to forward data frames from pc to iphone via usb (pymobiledevice3 remote tunneld)
#   -> tunneld automically:
#       -> connect and -
#       -> send rsdHello to each devices
#       -> get rsd lists(services and ids)
#open dvt socket to locatiion service and set


# local tunnel(map to usb) -> QUIC over usb -> RSD(only initial time) -> Dvt(servie) -> local tunnel map to usb -> iphone


