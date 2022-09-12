# UPnPwn
A network security utility for testing UPnP implementations.

For the early stages of the project, the goal is to create a tool for manually interacting with UPnP devices.
Later, support for launching UPnP-specific exploits will be added.

Eventually, this tool is intended to find new UPnP bugs/vulnerabilities.

## Installation
Run `pip install -r requirements.txt`.

## Usage
Currently, UPnPwn will initialise as a UPnP client device and send the appropriate discovery packets to the local network.

To run: `python upnpwn.py`


## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

