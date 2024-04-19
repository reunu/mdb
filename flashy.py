import crypt
import subprocess
import os
import re
import serial
import shutil
import time

mount_point = "/mnt/unu"

def connect_to_uart(port='/dev/ttyUSB0'):
    try:
        # Set up serial connection
        ser = serial.Serial(port, 115200, timeout=1)
        print("Connected to "+port+" at 115200 baud.")

        # Wait for the boot string
        while True:
            line = ser.read_until().decode('utf-8', errors='ignore')
            # print(line, end='')  # Optionally print all received text to monitor what's happening
            if "Freescale i.MX6 UltraLite" in line:
                print("Detected the target boot message.")
                break
        
        # Send the spacebar key repeatedly until the prompt appears
        while True:
            ser.write(b' ')
            line = ser.read_until().decode('utf-8', errors='ignore')
            # print(line, end='')  # Optionally print all received text to monitor what's happening
            if "=>" in line:
                print("Detected the prompt. Stopping key presses.")
                ser.write(b'ums 0 mmc 1\r')
                print("Enabled UMS mode")
                break

        # Clean up
        ser.close()
        print("Connection closed.")

    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
    except KeyboardInterrupt:
        print("Interrupted by user.")
        if ser.is_open:
            ser.close()
        print("Connection closed.")

def cls():
    os.system('clear')

def format_hex_string(hex_input):
    # Remove non-alphanumeric characters
    cleaned_input = ''.join(filter(str.isalnum, hex_input))
    # Convert to uppercase
    cleaned_input = cleaned_input.upper()
    # Split into pairs of characters
    formatted_hex = ' '.join(cleaned_input[i:i+2] for i in range(0, len(cleaned_input), 2))
    return formatted_hex

def write_file(file_path, content):
    with open(file_path, 'w') as file:
        file.write(content)

def get_disks():
    """List all disks currently connected to the system."""
    lsblk = subprocess.run(['lsblk', '-d', '-o', 'NAME'], capture_output=True, text=True)
    disks = lsblk.stdout.splitlines()
    return disks[1:]  # skipping the header

def find_new_disk(initial_disks):
    current_disks = get_disks()
    new_disks = list(set(current_disks) - set(initial_disks))
    return new_disks[0] if new_disks else None

def mount_disk(disk, mount_point="/mnt/unu"):
    partition = f"/dev/{disk}1"  # Assuming the first partition
    os.makedirs(mount_point, exist_ok=True)
    subprocess.run(['mount', partition, mount_point], check=True)
    print(f"Mounted {partition} to {mount_point}")

def get_ostree_from_loader(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            if "bootargs=ostree=" in line:
                start_index = line.find("bootargs=ostree=") + len("bootargs=ostree=")
                path = line[start_index:].strip()
                return path  # Return immediately after finding the path
    return None  # Return None if the line is not found

def prompt_binary_input(question):
    while True:
        user_input = input(f"{question} (y/n): ").strip().lower()
        if user_input == 'y':
            return True
        elif user_input == 'n':
            return False
        else:
            print("Invalid input. Please enter 'y' for yes or 'n' for no.")


def install(source, target):
    if not os.path.exists(source):
        print(f"Error: Source directory {source} does not exist.")
        return

    for sourcedir in os.listdir(source):
        os.system("cp -a "+source+"/"+sourcedir+" "+target)

def write_rootpw(newpw, rootdir):
    shadow_path = rootdir+'/etc/shadow'  # Adjust the path to your external drive's shadow file

    try:
        # Read the original contents
        with open(shadow_path, 'r') as file:
            lines = file.readlines()

        # Modify the root password line
        with open(shadow_path, 'w') as file:
            for line in lines:
                if line.startswith('root:'):
                    parts = line.split(':')
                    parts[1] = newpw  # Replace the existing hash with the new hash
                    line = ':'.join(parts)
                file.write(line)

        print("The root password has been successfully updated.")

    except Exception as e:
        print(f"Failed to update the root password: {e}")

def disable_systemd_service(rootdir, service_name):
    symlink_path = os.path.join(rootdir, 'etc', 'systemd', 'system', 'multi-user.target.wants', service_name)

    try:
        # Check if the symlink exists
        if os.path.islink(symlink_path):
            # Remove the symlink
            os.unlink(symlink_path)
            print(f"Service {service_name} has been successfully disabled.")
        else:
            print(f"No symlink exists for {service_name}, no action taken.")

    except Exception as e:
        print(f"Failed to disable the service {service_name}: {e}")


def enable_systemd_service(rootdir, service_name):
    target = os.path.join('/usr/lib/systemd/system', service_name)
    symlink_path = os.path.join(rootdir, 'etc', 'systemd', 'system', 'multi-user.target.wants', service_name)

    try:
        # Ensure the target directory exists
        os.makedirs(os.path.dirname(symlink_path), exist_ok=True)

        if os.path.islink(symlink_path):
            print(f"Service {service_name} is already enabled.")
        else:
            # Create the symlink
            os.symlink(target, symlink_path)
            print(f"Service {service_name} has been successfully enabled by creating a symlink at {symlink_path}.")

    except Exception as e:
        print(f"Failed to enable the service {service_name}: {e}")

##################################################

cls()

print("!!! Please make sure the board is powered down and your UART and USB are connected !!!")

port = input("Enter UART device name (or press ENTER for the default /dev/ttyUSB0): ")
if port == "":
    port = "/dev/ttyUSB0"

cls()

connect_to_uart(port)

initial_disks = get_disks()

time.sleep(5)

cls()

new_disk = find_new_disk(initial_disks)
if new_disk:
    mount_disk(new_disk, mount_point)
    ostree = get_ostree_from_loader("/mnt/unu/boot/loader/uEnv.txt")
    rootdir = "/mnt/unu"+ostree+"/"
    print("Root directory: "+rootdir)


    # user prompts

    nfcmod = prompt_binary_input("Install NFC keycard replacement?")
    disableuplink = prompt_binary_input("Disable unu server communication?")
    gpstime = prompt_binary_input("Install GPS time mod? (also disables cloud communication)")
    if gpstime:
        disableuplink = True
    setrootpw = prompt_binary_input("Change default root password?")

    if setrootpw:
        newrootpw = input("Enter new root password: ")

    if nfcmod:
        setadminuid = prompt_binary_input("Do you want to enter an admin NFC UID now?")
        if setadminuid:
            adminuid = format_hex_string(input("Enter admin UID: "))
    else:
        setadminuid = False

    cls()
    print("----")
    print("Summary:")
    print("NFC mod: "+str(nfcmod))
    if setadminuid:
        print("Admin NFC UID: "+adminuid)
    print("GPS time mod: "+str(gpstime))
    print("Disable cloud communication: "+str(disableuplink))
    print("Change root password: "+str(setrootpw))
else:
    print("No new disk detected. Please make sure the disk is properly attached.")

if prompt_binary_input("Continue?"):
    
    cls()

    print("Working...")

    if setrootpw:
        newrootpw = crypt.crypt(newrootpw, crypt.mksalt(crypt.METHOD_SHA512))
        write_rootpw(newrootpw, rootdir)

    if nfcmod:
        install("nfc/ostree", rootdir)
        disable_systemd_service(rootdir, "unu-keycard.service")
        enable_systemd_service(rootdir, "reunu-keycard.service")
        if setadminuid:
            write_file(rootdir+"etc/reunu-keycard/master_uids.txt", adminuid)

    if disableuplink:
        disable_systemd_service(rootdir, "unu-uplink.service")
        disable_systemd_service(rootdir, "unu-modem.service")
        disable_systemd_service(rootdir, "unu-ota-update.service")
        disable_systemd_service(rootdir, "unu-activation.service")

    if gpstime:
        install("gps/ostree", rootdir)
        enable_systemd_service(rootdir, "reunu-gpsd.service")
        enable_systemd_service(rootdir, "reunu-enablemodem.service")

### end

subprocess.run(['sync'])
subprocess.run(['umount', mount_point], check=True)
print("All actions completed. Bye!")

