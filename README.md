# Home Control
An exploration in automation and control of the home using low-cost, single-board computers and a wireless LAN.

## Agent
The "Agent" is deployed on site to collect data and perform home control operations, integrating with sensors and external devices in the home. Agents send sensor data and receive commands from the Home Control "Base" over the local area network.

## Base
The "Base" is a central hub that interfaces between internet-based automation systems such as HomeKit and the deployed "Agents" in the home. The Base listens for updates from Agents and maintains time-based records of sensor data. The Base exposes controls to HomeKit by integrating with [Homebridge](https://homebridge.io).
