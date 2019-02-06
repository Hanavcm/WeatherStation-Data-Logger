# WeatherStationLogger

#####  This is a GUI script written for the University of Western Australia OzGrav to log weather at the Gingin Site.
#####  Modified by Wenjing Zheng and Conor Hanavan
#####  Originally written by Jason Gan https://github.com/jason-gan/WeatherStationLogger

#####  Requirements:
1. Python 3.6+
2. Tkinter (Should be installed on MacOS by default)
3. Pyserial (Latest is ideal)
4. Windows or OSX compatible
5. Serial data input (in this case ADAM4017 with a RS485/232 to USB converter) connected to host computer


##### Instructions:
First check that the serial input is connected properly:
For Windows:
- Open Command Prompt (Type CMD into the start menu and hit enter)
- Enter the command 'mode' this will display CON and all COM ports connected, 
    as it is physically connected it will likely show in COM 2/3/4
- Exit CMD


For OSX
- Open Terminal
- Check what is in /dev.tty/*, as it should display a USB-Serial option or something similar.
- Exit Terminal


Alternatively, Use the ADAM/APAX (windows only) utility to check that the input is connected properly. This can be downloaded from their website.


Next, Simply run the script and the GUI will be initiated (proviced serial connection is properly done - this can take around 30 seconds to find all the connected and available serial ports). Then, select the serial input from the drop down box, and select a save location for the datalog file. After, hit the start button, and let it run!


The Script will simply output the current readings to a CSV file approximately everty 15 seconds. If you stop and start recording again - it will completely wipe the CSV File.
It is recommended to copy/backup the CSV data file at least once a day. This can be included in future implementations...



---

###### Known Issues:
Sometimes, windows installations of python will not include pip - which should be installed to get Tkinter and Pyserial. This can be a little fiddly at times and can increase the set up time.


If the usb to serial converter is properly plugged in, but nothing is registering on the COM ports - it is almost certainly a driver issue. Try deleting the drivers and reinstalling them from the internet (this can all be done from the windows control panel).


If the wind speed sensor is spun backwards (nigh impossible in practicality) it will result in an exception being thrown, this is fine - as it simply loops back and tries to read again, this exception is not saved to the csv output file.


