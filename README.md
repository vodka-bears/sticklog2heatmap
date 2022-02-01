# sticklog2heatmap
Draw a heatmap of RC sticks from OpenTX logs or USB HID device
## sticklog2heatmap.py
The tool that draws a png file with the heatmap
### Usage:
```
python sticklog2heatmap.py
```
Opens all csv files in current directory
```
python sticklog2heatmap.py [filename1.csv]...[filenameN.csv]
```
Clear as is
```
python sticklog2heatmap.py [dirname]
```
Opens all csv files in dirname
### Requirements:
- numpy
- cv2
- matplotlib

Install with pip or any other preferred way
## hid2sticklog.py
The tool to grab logs from the radio handset connected to the computer e.g. when flying in a simulator
### Usage:
Simply run the script with python. If threre's more than one supported device in system the script will prompt.
### Requirements:
- hid from pip or anywhere else
- [hidapi library](https://github.com/libusb/hidapi/releases) file in the same directory depending on your platform (e.g. hidapi.dll for windows)