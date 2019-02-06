from tkinter import *
from tkinter.filedialog import askdirectory
import sys
import glob
from tkinter.messagebox import showinfo
import serial
import datetime
import time
import serial.tools.list_ports
import csv


# List available serial ports on this computer
def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]

    elif  sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')

    elif  sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')

    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:

        try:
            s = serial.Serial(port,9600, timeout=10)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


# Initialise TKinter
root = Tk()


class Application:
    directory = None
    available_inputs = None
    selected_input_dropdown = None
    settings_selected_input = False
    settings_selected_save_location = False
    settings_start_serial = False

    def __init__(self, master):
        # Must find if there is serial posts first
        self.available_inputs = serial_ports()
        if len(self.available_inputs) < 1:
            print('No available serial ports')
            master.destroy()
            return
        print('Found Serial Ports! \nApp Started')
        self.available_inputs.insert(0, '(Select serial input)')

        # Select Logger Inputs
        self.select_logger_label = Label(master, text="Select logger input:")
        self.select_logger_label.grid(column=0, row=0, sticky=E)
        self.input_variable = StringVar(master)
        self.input_variable.set(self.available_inputs[0])
        self.selected_input_dropdown = OptionMenu(master, self.input_variable, *self.available_inputs,
                                                  command=self.dropdown_callback)
        self.selected_input_dropdown.grid(column=1, row=0)

        # Select Logger Save Location
        self.select_save_location_label = Label(master, text="Select root folder to save:")
        self.select_save_location_label.grid(column=0, row=1)
        self.selected_location = Label(master, text="(Not Selected)")
        self.selected_location.grid(column=1, row=1)

        self.select_save_location_button = Button(master, text="Select", command=self.load_directory)
        self.select_save_location_button.grid(column=2, row=1)

        # Help Button
        self.start_button = Button(master, text="Help", command=self.help)
        self.start_button.grid(column=4, row=0)

        # About Button
        self.start_button = Button(master, text="About", command=self.about)
        self.start_button.grid(column=4, row=1)
        root.grid_rowconfigure(3, minsize=50)

        # Start Button
        self.start_button = Button(master, text="Start", command=self.start)
        self.start_button.grid(column=0, row=4)

        # Start Button
        self.stop_button = Button(master, text="Stop", command=self.stop)
        self.stop_button.grid(column=1, row=4)

        root.grid_columnconfigure(3, minsize=50)

        # Current Reading
        root.grid_rowconfigure(5, minsize=100)
        self.current_reading_label = Label(master, text="(Not initialised)")
        self.current_reading_label.grid(column=0, row=6, columnspan=4)

        self.stop_button.configure(state=DISABLED)
        self.start_button.configure(state=DISABLED)
        # self.start_loop()

    def load_directory(self):
        self.directory = askdirectory()
        self.selected_location['text'] = self.directory
        self.settings_selected_input = True
        if self.settings_selected_input and self.settings_selected_save_location:
            self.start_button.configure(state=NORMAL)

    def dropdown_callback(self, selection):
        global global_current_input, settings_selected_save_location
        global_current_input = selection
        self.settings_selected_save_location = True
        if self.settings_selected_input and self.settings_selected_save_location:
            self.start_button.configure(state=NORMAL)

    def stop(self):
        self.stop_button.configure(state=DISABLED)
        self.start_button.configure(state=NORMAL)
        self.settings_start_serial = False

    def start(self):
        self.start_button.configure(state=DISABLED)
        self.stop_button.configure(state=NORMAL)
        self.settings_start_serial = True

        #Create initial csv file
        location=self.selected_location['text']
        if sys.platform.startswith('win'):
            with open(location + "\\" + "weatherStationDataLog.csv", "w", newline='') as out_file:
                writer = csv.writer(out_file)
                writer.writerow(('Date', 'Time', 'Direction', 'Speed', 'Temperature'))
                out_file.close()
        else:
            with open(location + "/" + "weatherStationDataLog.csv", "w", newline='') as out_file:
                writer = csv.writer(out_file)
                writer.writerow(('Date', 'Time', 'Direction', 'Speed', 'Temperature'))
                out_file.close()
        #
        self.start_loop()

    def start_loop(self):
        if self.settings_start_serial:
            #print("TestStatement")
            self.serial_recorder()
        root.after(1000, self.start_loop)

    @staticmethod
    def help():
        showinfo('Help', "Visit https://github.com/Hanavcm/WeatherStation-Data-Logger")

    @staticmethod
    def about():
        showinfo("About", "Wenjing Zheng\n22126041@student.uwa.edu.au\n\nConor Hanavan\n21303234@student.uwa.edu.au\n\nhttps://github.com/Hanavcm")

    def serial_recorder(self):
        #print("EnteredSerialRecorder.../n")
        try:
            data = str(datetime.datetime.now())
            serialconnection = serial.Serial(global_current_input, baudrate = 9600, timeout=5, rtscts=False, dsrdtr=False, bytesize=serial.EIGHTBITS, parity = serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)

            #channel 0
            serialconnection.write("#010\r\n".encode('UTF-8'))
            reading0 = serialconnection.readline().decode('UTF-8')
            #channel 1
            serialconnection.write("#011\r\n".encode('UTF-8'))
            reading1 = serialconnection.readline().decode('UTF-8')
            #channel 2
            serialconnection.write("#012\r\n".encode('UTF-8'))
            reading2 = serialconnection.readline().decode('UTF-8')

            #Wind Direction Calculation
            windDir = reading0[2:10]                                            #slice longer than string just in case
            dir= float(windDir)                                                 #convert to float
            direction = round((dir - 3.612)*22.5, 2)                            #calculate and round
            if dir >= 4.112 and dir < 5.112:
                #Direction is NNE
                savedDir = "Wind Direction: NNE ({})°".format(direction)

            elif  dir >= 5.112 and dir < 6.112:
                #Direction is NE
                savedDir = "Wind Direction: NE ({})°".format(direction)

            elif dir >= 6.112 and dir < 7.112:
                #Direction is ENE
                savedDir = "Wind Direction: ENE ({})°".format(direction)

            elif dir >= 7.112 and dir < 8.112:
                #Direction is E
                savedDir = "Wind Direction: E ({})°".format(direction)

            elif dir >= 8.112 and dir < 9.112:
                #Direction is ESE
                savedDir = "Wind Direction: ESE ({})°".format(direction)

            elif dir >= 9.112 and dir < 10.112:
                #Direction is SE
                savedDir = "Wind Direction: SE ({})°".format(direction)

            elif dir >= 10.112 and dir < 11.112:
                #Direction is SSE
                savedDir = "Wind Direction: SSE ({})°".format(direction)

            elif dir >= 11.112 and dir < 12.112:
                #Direction is S
                savedDir = "Wind Direction: S ({})°".format(direction)

            elif dir >= 12.112 and dir < 13.112:
                #Direction is SSW
                savedDir = "Wind Direction: SSW ({})°".format(direction)

            elif dir >= 13.112 and dir < 14.112:
                #Direction is SW
                savedDir = "Wind Direction: SW ({})°".format(direction)

            elif dir >= 14.112 and dir < 15.112:
                #Direction is WSW
                savedDir = "Wind Direction: WSW ({})°".format(direction)

            elif dir >= 15.112 and dir < 16.112:
                #Direction is W
                savedDir = "Wind Direction: W ({})°".format(direction)

            elif dir >= 16.112 and dir < 17.112:
                #Direction is WNW
                savedDir = "Wind Direction: WNW ({})°".format(direction)

            elif dir >= 17.112 and dir < 18.112:
                #Direction is NW
                savedDir = "Wind Direction: NW ({})°".format(direction)

            elif dir >= 18.112 and dir < 19.112:
                #Direction is NNW
                savedDir = "Wind Direction: NNW ({})°".format(direction)

            else:
                #Direction is outside of range, ie NORTH
                savedDir = "Wind Direction: N ({})°".format(direction)

            #---Wind Direction Calculations Complete and saved into 'savedDir'

            #Wind Speed Calculation
            windspeed = reading1[2:10]                                          #initial wind reading in mA
            windspeednum = float(windspeed)                                     #convert from string to float
            speed = round((windspeednum - 3.612)*60/16, 2)                      #convert mA to m/s and round
            savedSpeed = "\nWind Speed: {} m/s".format(speed)
            #---Wind speed Calculated and saved into 'savedSpeed'

            #Temperature Calculations
            currentTemp = reading2[2:10]                                        #initial temp reading in mA
            numTemp = float(currentTemp)                                        #convert from string to float
            temp = round(((numTemp - 3.612)*100/16) - 30, 2)                    #convert from mA to Degrees Celsius and round
            savedTemp = "\nTemperature: {} °C\n\n".format(temp)
            #---Temperature calculated and saved into 'savedTemp'

            #Output all data
            rawData = str(data) + " \n" + str(direction) + " " + str(speed) + " " + str(temp) + "\n" #potentially redundant to create and then split (1/2)
            displayedData = str(data)+ "\n" + savedDir + savedSpeed + savedTemp       #displayedData Variable combines all
            #print(rawData)                                                #print in terminal output
            self.current_reading_label['text'] = displayedData                  #print to gui output
            outputData = rawData.replace("\n","").split(" ")                    #potentially redundant to create and then split (2/2)
            print(outputData)
            self.write_to_file(data=outputData, location=self.selected_location['text'])     #write output to file

        except Exception:
            print("TestStatementException")
            pass

    @staticmethod
    def write_to_file(data, location):

        #current = "{:%Y%m%d}".format(datetime.datetime.now())
        if sys.platform.startswith('win'):
            with open(location + "\\" + "weatherStationDataLog.csv", "a", newline='') as out_file:
                writer = csv.writer(out_file)
                writer.writerow(data)
        else:
            with open(location + "/" + "weatherStationDataLog.csv", "a", newline='' ) as out_file:
                writer = csv.writer(out_file)
                writer.writerow(data)
        out_file.close()



root.title('UWA OzGrav Weather  Data Logger - Version 1.6')
root.geometry("600x400")
print("Starting App...\nFinding Serial Ports...\nIt might take up to 30 seconds to start..")
app = Application(root)
root.mainloop()
