# Home Control
An exploration in automation and control of the home using low-cost, single-board computers and a wireless LAN.

### Agent
The "Agent" is deployed on site to collect data and perform home control operations, integrating with sensors and external devices in the home. Agents send sensor data and receive commands from the Home Control "Base" over the local area network.

### Base
The "Base" is a central hub that interfaces between internet-based automation systems such as HomeKit and the deployed "Agents" in the home. The Base listens for updates from Agents and maintains time-based records of sensor data. The Base exposes controls to HomeKit by integrating with [Homebridge](https://homebridge.io).

## Raspberry Pi Setup 
Follow these steps to install Home Control on your system

### Installation
Installing Home Control on Raspberry Pi requires a few prerequisite installation steps before running the setup scripts.
```
$ sudo apt-get update
$ sudo apt-get install git
$ sudo apt-get install vim
$ sudo apt-get install pip
$ sudo apt-get install python3-venv
```
Clone the repository, and from the project root directory run the install script
```
$ cd path/to/homecontrol
$ scripts/install.sh
```
To ensure that Home Control is launched automatically after device boot, edit `rc.local`.
```
$ sudo vim /etc/rc.local

# Add the following line before exit 0:

sudo -H -u pi sh -c 'cd  /absolute/path/to/homecontrol && ./scripts/launch.sh base' &
```

### USB Speaker Setup
Instructions paraphrased from [this blog post.](https://www.jeffgeerling.com/blog/2022/playing-sounds-python-on-raspberry-pi)
Plug the USB speaker into the Raspberry Pi and confirm that it is discovered properly
```
$ cat /proc/asound/modules
 1 snd_usb_audio
```
You may also see a 0 for a built-in device. By default, the ALSA (Advanced Linux Sound Architecture) audio system will default to device 0. Switch to device 1 (the `snd_usb_audio` device) by configuring either the global `/etc/asound.conf` file, or a user-local `~/.asoundrc` file.
```
$ vim ~/.asoundrc

pcm.!default {
        type hw
        card 1
}

ctl.!default {
        type hw
        card 1
}
```
test the configuration with ASLA
```
$ speaker-test -c2 -twav -l7
```

### Thermal Sensor Setup
To setup the 3-wire thermal sensor with raspberry pi GPIO, first enable GPIO in boot config
 ```
$ sudo vim /boot/config.txt
```
Add the following line anywhere in the file:
```
dtoverlay=w1-gpio
```
Enable the drivers to interface with the thermal sensor:
```
$ sudo modprobe w1-gpio
$ sudo modprobe w1-therm
```
Reboot
```
$ sudo reboot
```
With the sensor connected, find the detected device and note its name in the following directory:
```
$ ls /sys/bus/w1/devices/
```
You should see a linked directory for the device such as "28-03189779d98f" in the following:
```
$ ls -al
total 0
drwxr-xr-x 2 root root 0 .
drwxr-xr-x 4 root root 0 ..
lrwxrwxrwx 1 root root 0 28-03189779d98f -> ../../../devices/w1_bus_master1/28-03189779d98f
lrwxrwxrwx 1 root root 0 w1_bus_master1 -> ../../../devices/w1_bus_master1
```
The thermal sensor can be read by opening the w1_slave file within the device directory:
```
$ cat /sys/bus/w1/devices/28-03189779d98f/w1_slave 
a2 01 55 05 7f a5 a5 66 ce : crc=ce YES
a2 01 55 05 7f a5 a5 66 ce t=26125
```
Now that we have an active thermal sensor connected, add the sensor directory to the agent config override file
```
$ cd path/to/homecontrol
$ $ vim agent/conf/agent-override.conf
thermometer_enabled=1
thermometer_device_dir=/sys/bus/w1/devices/28-03189779d98f 
thermometer_device_file=w1_slave
```
	
## Running Home Control
Use the launch script to launch the intended Home Control application
```
$ cd path/to/homecontrol
$ scripts/launch.sh agent
```
