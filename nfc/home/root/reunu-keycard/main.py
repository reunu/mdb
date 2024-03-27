import os
import pty
import shlex
import subprocess
import threading
import time
from PN7150 import PN7150

# Assuming the output from the NFC reader contains lines that look like "UID : [UID_VALUE]"
_OUTPUT_UID_PREFIX = 'NFCID1 :'
AUTHORIZED_UIDS_FILE = 'authorized_uids.txt'
MASTER_UIDS_FILE = 'master_uids.txt'
KEYCARD_SCRIPT = '/home/root/keycard.sh'
LED_SCRIPT = '/home/root/ledcontrol.sh'
GREEN_LED_SCRIPT = '/home/root/greenled.sh'
_CMD_POLL = '/usr/sbin/nfcDemoApp poll'


class PN7150Extended(PN7150):
    def __init__(self, nfc_demo_app_location='/usr/sbin'):
        super().__init__(nfc_demo_app_location)
        self.authorized_uids = self._load_authorized_uids(AUTHORIZED_UIDS_FILE)
        self.master_uids = self._load_master_uids(MASTER_UIDS_FILE)
        self._learn_mode = False
        self._newUIDs = []
        subprocess.run([GREEN_LED_SCRIPT, '0'], shell=False)

    @staticmethod
    def _load_authorized_uids(file_path):
        with open(file_path, 'r') as file:
            return [line.strip() for line in file.readlines()]

    @staticmethod
    def _load_master_uids(file_path):
        with open(file_path, 'r') as file:
            return [line.strip() for line in file.readlines()]

    @staticmethod
    def _write_authorized_uids(file_path, uids):
        with open(file_path, 'w') as file:
            for uid in uids:
                file.write("%s\n" % uid)

    def _read_thread(self):
        cmd = _CMD_POLL.format(nfc_demo_app_path=self._nfc_demo_app_path)
        master, self._slave = pty.openpty()
        self._proc = subprocess.Popen(shlex.split(cmd), stdin=subprocess.PIPE, stdout=self._slave, stderr=self._slave)
        stdout = os.fdopen(master)

        self._read_running = True
        while self._read_running:
            try:
                line = stdout.readline()
                if _OUTPUT_UID_PREFIX in line:
                    uid = line.split(_OUTPUT_UID_PREFIX)[-1].strip().replace('\'', '').strip()
                    if not self._learn_mode:
                        if uid in self.master_uids:
                            print(f"Master UID detected: {uid} - Switching to learn mode")
                            self._learn_mode = True
                            subprocess.run([LED_SCRIPT, '3', 'fade06_brake_off_to_full.bin'], shell=False)
                            subprocess.run([LED_SCRIPT, '7', 'fade06_brake_off_to_full.bin'], shell=False)
                        elif uid in self.authorized_uids:
                            print(f"Authorized UID detected: {uid} - Executing script")
                            subprocess.run([GREEN_LED_SCRIPT, '1'], shell=False)
                            subprocess.run([KEYCARD_SCRIPT], shell=False)
                            time.sleep(1)
                            subprocess.run([GREEN_LED_SCRIPT, '0'], shell=False)
                        else:
                            print(f"Unauthorized UID detected: {uid}")
                    else:
                        if uid in self.master_uids:
                            print(f"Master UID detected: {uid} - Switching off learn mode")
                            self._learn_mode = False
                            subprocess.run([LED_SCRIPT, '3', 'fade12_license_full_to_off.bin'], shell=False)
                            subprocess.run([LED_SCRIPT, '7', 'fade12_license_full_to_off.bin'], shell=False)
                            if len(self._newUIDs) == 0:
                                print('nothing learned')
                            else:
                                for newUID in self._newUIDs:
                                    print(newUID)
                                self._write_authorized_uids(AUTHORIZED_UIDS_FILE, self._newUIDs)
                                self.authorized_uids = self._load_authorized_uids(AUTHORIZED_UIDS_FILE)
                            self._newUIDs = []
                        else:
                            print(f"UID detected: {uid} - Learning")
                            subprocess.run([GREEN_LED_SCRIPT, '1'], shell=False)
                            self._newUIDs.append(uid)
                            subprocess.run([LED_SCRIPT, '1', 'fade10_blinker.bin'], shell=False)
                            subprocess.run([LED_SCRIPT, '1', 'fade10_blinker.bin'], shell=False)
                            subprocess.run([LED_SCRIPT, '1', 'fade10_blinker.bin'], shell=False)
                            time.sleep(1)
                            subprocess.run([GREEN_LED_SCRIPT, '0'], shell=False)

            except (IOError, OSError):
                pass

    def start_reading(self):
        print("Starting NFC tag reading with UID checking...")
        super().start_reading()

# Example usage
if __name__ == "__main__":
    pn7150 = PN7150Extended()
    pn7150.start_reading()

