# Home Control
An exploration in automation and control of the home using low-cost, single-board computers and a wireless LAN.

### Agent
The "Agent" is deployed on site to collect data and perform home control operations, integrating with sensors and external devices in the home. Agents send sensor data and receive commands from the Home Control "Base" over the local area network.

### Base
The "Base" is a central hub that interfaces between internet-based automation systems such as HomeKit and the deployed "Agents" in the home. The Base listens for updates from Agents and maintains time-based records of sensor data. The Base exposes controls to HomeKit by integrating with [Homebridge](https://homebridge.io).

## Getting Started
Follow these steps to install Home Control on your system

### Raspberry Pi Setup 
Installing Home Control on Raspberry Pi requires a few prerequisite installation steps before running the setup scripts.
```
$ sudo apt-get update
```
Make sure git is installed (necessary for "*-lite" Raspbian images)
```
$ sudo apt-get install git
```
Install pip
```
$ sudo apt-get install pip
```
Install python3-venv enabling the virtual python3 environment
```
$ sudo apt-get install python3-venv
```
Clone the repository, and from the project root directory run the install script passing the intended installation type
```
$ cd path/to/homecontrol
$ scripts/install.sh agent
```
## Running Home Control
Use the launch script to launch the intended Home Control application
```
$ cd path/to/homecontrol
$ scripts/launch.sh agent
```
