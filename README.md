# THE FOLLOWING INSTRUCTIONS ARE OUT OF DATE #

## Preliminary Flashing Instructions

The following steps are intended for those familiar with hardware modification and software configuration. Many of these steps will be automated in a future script.

### Caution
Proceed only if you are confident in your understanding of the process. Incorrect handling may permanently damage your scooter.

**Important**: This procedure is recommended only for individuals who are experienced with soldering and the Linux command line. If you are not, it is advisable to wait for more user-friendly instructions.

### Instructions

1. **Soldering Connection**: Attach pins to the MDB. Ensure a connection through a 3.3V USB UART interface.
2. **Interrupt Boot Process**: Within the first few seconds of powering on, repeatedly press the [space] bar until a command prompt appears.
3. **Connection**: Connect your Linux-based computer to the Mini USB port on the MDB.
4. **Bootloader Command**: At the bootloader prompt, type `ums 0 mmc 1`.
5. **Disk Identification**: Identify the external disk drive and its partition. This can be achieved using `fdisk` or `lsblk` commands.
6. **Mount Partition**: Proceed to mount the identified partition.
7. **Locate OStree Branch**: Determine the OStree branch in use by examining the `bootargs` parameter within `/boot/loader/uEnv.txt`.
8. **Copy NFC Directory**: Transfer the contents of the `nfc/ostree` directory from this repository into your OStree root directory.
8. **Copy NFC Directory**: Transfer the `nfc/home` directory from this repository into the MDB root directory.
9. **Service Symlink Removal**: Delete the `etc/systemd/system/multi-user.target.wants/unu-keycard.service` symlink from your OStree root.
10. **Root Password Update**: Update the root password in your OStree's `etc/shadow` file with a password of your choosing.

After completing these steps, unmount the drive, reconnect the DBC to the MDB, and restart the MDB. Upon reboot, you should be able to access the serial console using your new password.

Stop the `reunu-keycard` service via executing `systemctl stop reunu-keycard.service`. To obtain NFC readings, run `nfcDemoApp poll`. When you scan the token intended as the "master key", note the UID. Add this UID to `/home/root/reunu-keycard/master_uids.txt` using `vi` or `cat`.

Following a system reboot, you will be able to use the master key for registering keycards.

