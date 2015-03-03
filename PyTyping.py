#TKinter is the GUI library
from tkinter import *
import time
import os
import platform
import serial
from serial.serialutil import SerialException

'''
Input File:
    The input file is a text file called "strings.txt"
    The first line if the file will be the port you want the
    serrial output to connect to. For Windows it be COM* (COM1, COM2, COM3...)
    and for linux it will be in your /dev/ folder (Some common places:
    /dev/stty, /dev/ttyUSB1) It will read each line of the text file and
    store it. It is recomended that strings are ten words or less to fit
    on the screen.
'''

#Open File
file = open("strings.txt", 'r')

#Get Port from first line
port = file.readline().strip('\n')

#Read in the rest of the strings
strings = []
for i in file:
    if i != '\n':   #Check for empty lines
        strings.append( (i.strip('\n'),i.count(' ')+1) )

'''
strings is a list of pairs read from the file. The first part
of the pair (i.strip('\n')) reads in the string and removes the
newline, the second part (i.count(' ')+1)) counts the number
if spaces in the string. The number of spaces is another way
of keeping track of the number of words in the string.
'''
        
class GUI:

    def __init__(self):

        #Main window area
        self.root = Tk()

        #Exit key command bound to the root window "Ctl-Alt-e"
        self.root.bind("<Control-Alt-e>", lambda x: self.root.destroy())

        #Adds components to the window
        self.start_screen()

        #Starts the mainloop for the window
        self.root.mainloop()


    #The start screen is the "Press space when ready screen"
    def start_screen(self):

        #Set to full screen
        self.root.attributes("-fullscreen", True)

        ###The bufferes are padding to set other components in different parts of the screen###
        buffer1 = self.create_buffer_frame(self.root)

        #Create a label to display text
        label1 = Label(self.root, text="Press spacebar to start test.", font=("Calibri", 35))
        label1.pack()

        ###With a buffer on top and bottom, the text becomes centered###
        buffer2 = self.create_buffer_frame(self.root)

        #Tuple contsining the window elements
        window_objects=(buffer1, label1, buffer2)

        #On any key press move onto the next "slide"
        self.root.bind("<KeyPress>", lambda x: self.on_space(x, window_objects))
        
    def on_space(self, event, to_destroy):

        #to_destroy has the previous slides window objects, which are going to be replaced
        to_destroy[0].destroy()
        to_destroy[1].destroy()
        to_destroy[2].destroy()

        #Unbinds the keypress and starts the test
        self.root.unbind("<KeyPress>")
        self.start_test()

    #Adds new components to the GUI and starts the typing test
    def start_test(self):

        #Hides the mouse
        self.root.config(cursor='none')
        
        #Creates a buffer above the text
        self.create_buffer_frame(self.root)
        
        #Opens the serial port
        serial = Sendpack(Strings.port)

        #Checks if port is open, throws error if not
        if not serial.is_open():
            messagebox.showerror("Port","Could not connect to " + Strings.port)
            self.root.destroy()
            return

        #starts the key logger
        logger = Record(serial)
        Container(self.root, logger, Strings.strings)
         
        
        #Creates a buffer below the text
        self.create_buffer_frame(self.root)        
        
    #Creates a frame that is used for padding
    def create_buffer_frame(self,parent):
        frame = Frame(parent)
        frame.pack(expand=True, fill=BOTH)
        return frame

##################################################################################

#The container class controls the text box and text entry field in the GUI   
class Container:
    #Counter to keep track of current string
    count = 0

    #Was last slide a break slide?
    skip_last_slide = False

    #Counter for slides displayed. Used to keep track of when to display a break slide
    num_slides = 1

    #Class constructor
    def __init__(self, root, log, strings):

        #Creates the logger which handles output to a file
        self.logging = log

        #Sets font and ready variable
        self.font = ("Arial", 33)

        #Saves the strings variable
        self.strings = strings

        #Sets the string
        self.set_next_string()

        #Makes a container to hold the text and text field
        self.makeContainer(root)
    

    def makeContainer(self, root):
        #New frame container
        container = Frame(root)
        container.pack()

        #Creates the text area for typing
        textArea = Entry(container, font=self.font)
        #Key Bindings for the text area
        textArea.bind('<Return>', self.on_enter)
        textArea.bind('<KeyPress>', self.on_key_press)
        #Get focus and pack
        textArea.focus_set()
        textArea.pack(fill='x',side=BOTTOM)
        
        #Text label containing the text the user will be typing
        label = Label(container, text=self.text, font=self.font, pady=20)
        label.pack(fill='x')

        #Assign them to class variables
        self.C = container
        self.T = textArea
        self.L = label
        

    #Sets the next string to be displayed
    def set_next_string(self):
        try:
            #Put current string into the logger
            self.logging.set_text(self.strings[self.count])
            #Make that string the one to display
            self.text = self.strings[self.count][0]
            #increment counter
            self.count += 1
            return False
        
        except IndexError:
            #When it hits the end of the array, display "Finished" and exit
            Label(self.C, text="Finished", font=self.font).pack()
            self.T.destroy()
            return True
            
    #on key press, put character into logger 
    def on_key_press(self, event):
        self.logging.input(event.char)
        
    #Actions to take when the enter key is hit
    def on_enter(self, event):
        
        #destroys current label
        self.L.destroy()
        
        #If the last slide was not a intermediate slide
        #flush output
        if not self.skip_last_slide:
            self.logging.flush()
        
        #If five slides have displayed, show break slide
        if self.num_slides == 5:
            self.break_slide()
        else:
            self.relabel()
            
    #Reconfigures the text field and resets the label text for the next slide to display
    def relabel(self):

        #Increment counter
        self.num_slides += 1
        self.skip_last_slide = False

        #If not in last slide, procede
        if  not self.set_next_string():
            
            #Get text character length
            width = len(self.text)

            #Delete last component
            self.T.delete(0, END)
            #Set focus and pack
            self.T.focus_set()
            self.T.pack(fill='x', side=BOTTOM)

            #Create a new label to display
            self.L = Label(self.C, text=self.text, font=self.font, pady=25)
            self.L.pack(fill='x')
 
    #Creates a intermediate slide that displays wpm and errors
    def break_slide(self):

        #Reset flag and counter
        self.skip_last_slide = True
        self.num_slides = 0

        #Hide text box
        self.T.pack_forget()

        #String to display on the intermediate slide
        status = "Good job!\n\nWPM = " + "{:.1f}".format(self.logging.get_wpm())
        status += "\nErrors = " + str(self.logging.get_error())
        status += "\n\nLets try to go a little faster this time!\n\n(Press enter to continue)"

        #Create new label and pack
        self.L = Label(self.C, text=status, font=self.font, pady=25)
        self.L.pack()
################################################################################################
'''
While the user is typing, all of that information (key press, time presses, correct key press, type of key press)
is stored in a list in memory. When the user switches between slides, that information is
outputed to a new line in the output file and cleared from memory.
'''
class Record:

    #Variable to hold the number of words in a string
    num_words=0
    
    #Prealocate some memory for the list
    list=[]*999

    #Keeps track of current location in the list
    list_pointer = 0

    #Time variable to keep track of when they first start typing
    time_first=0
    
    first=True

    #Array to keep track of words per minute for each string
    wpm = []

    #Class constructor
    def __init__(self, serial):
        #Creates a local serial variable
        self.serial = serial

        #Create empty string that will hold what has been typed
        self.current_string=""
        #No errors to start with
        self.error_num = 0
        #Is the first string
        self.string_num = 1

        #Creates the directory to store output
        self.name_dir()

    #Class destructor
    #When this object is destroyed, flush the output of the list if it is not null   
    def __del__(self):
        if self.list!=[]:
            self.flush()

        #Close the file
        self.file.close()

            
    def name_dir(self):
       
        #Folder location for the output files based on date
        self.output_folder = "output/Experiments "+time.strftime("%m-%d-%Y")+"/"

        #Makes directory, dosn't override existing ones
        os.makedirs(self.output_folder, exist_ok=True)

        cnt = 1
        #Checks if that file already exists by incrementing through all file names in the folder
        for i in os.listdir(self.output_folder):                        
            if (i[:10] == "Experiment" and int(i[:-4][11:]) >= cnt):
                cnt = int(i[:-4][11:])+1

        '''
        Files are outputed as "Experiment (number).csv"
        When checking if the file exists:
            i[:10] = "Experiment"    checks the first ten characters against the string "Experiment"
            cnt = (the maximum file number found) + 1
            i[:-4] removes the last four characters (the ".csv")
            [11:]  removes the first eleven characters ("Experiment" + Space)
            That just leaves a number in the form of a string, which is converted by the int() function
        '''
        
        #Output file location + name  
        self.output_file = self.output_folder+"Experiment "+str(cnt)+".csv"

        #Create output file
        self.file = open( self.output_file , 'w' )

    #Sets the current string to be outputed
    def set_text(self, text_pair):
        
        #Sets the string and number of words
        self.sample = text_pair[0]
        self.num_words = text_pair[1]
        
        #Clears list and typed string
        self.current_string=""
        self.list=[]
        
    def flush(self):

        self.string_num += 1

        if len(self.current_string) < 1:
            return
        
        #Keeps track of the total error numbers
        self.error_num += string_err(self.sample, self.current_string)

        #Adds the list to a itterator which allows us to easly iterate through the list
        itterator = iter(self.list)
        
        
        #Records the first value in the list outside of the loop because its easier that way
        first = self.list[0]
        self.file.write( str(self.string_num) + ', ' + first[0]+ ', 0, 0, ' + '"%s"' % first[2]+ ', ' + first[3]+'\n');

        #Skip that first element
        next(itterator)

        #Temporary variables for calculations
        word_time = 0
        word_count = 0
        wpm = 0
        
        #Records the start time
        time = int(first[1]*1000)
        stime = time

        #Outputs: (string numbert, type(KeyPress or Delete), time from start, time since last, current typed string, key press)
        for i in itterator:
            #Calculate the time from beginning and difference from last key press
            diff = int(i[1]*1000) - time
            sdiff = int(i[1]*1000) - stime
            time = int(i[1]*1000)

            #Write to file
            self.file.write( str(self.string_num) + ', ' + i[0] + ', '+str(sdiff) + ', '+str(diff) + ', ' + '"%s"' % i[2] + ', '+i[3]+'\n');
    

        #Calculate words per minute for this string
        wpm = (sdiff/ 1000 / 60 / self.num_words)

        #Adds it to the class list
        self.wpm.append(1/wpm)

        
    #function to check for errors in a string
    #uses the longest common subsequence algorithm
    #first string should be the correct one
    def string_err(n,m):
        a = [[0]*(len(m)+1)]*(len(n)+1)
    
        for i in range(1, len(n)):
            for j in range(1, len(m)):
                if n[i] == m[j]:
                    a[i][j] = a[i][j] + 1
                else:
                    a[i][j] = max(a[i][j-1], a[i-1][j])

        return len(n)-a[len(n)-1][len(m)-1]-1   

    #Function to record time and send serial pulse at key press
    def input(self, char):

        #Filters out odd key presses like shift
        if char == '':
            return

        #Sends a serial package
        self.serial.send()

        #Checks for delete key
        if char=="\x08":
            #Records the delete
            #If character is space, then output "Space" not ' '
            if self.current_string[-1:] == ' ':
                self.list.append(("Delete", time.time(), self.current_string, 'Space'))
            else:
                self.list.append(("Delete", time.time(), self.current_string, self.current_string[-1:]))

            #Removes last element of string
            self.current_string = self.current_string[:-1]
        else:
            self.current_string += char

            #Replaces space character with 'Space'
            if char==' ':
                char="Space"

            #Records the keypress
            self.list.append(("KeyInput", time.time(), self.current_string[:-1], char))

    
    #Averages the words per min and returns it
    def get_wpm(self):
        avg_wpm = 0
        count = 1

        #Iterates through list of wpm, adds them, then divides by number of them
        for i in self.wpm:
            count += 1
            avg_wpm += i
        

        self.wpm = []
        return avg_wpm/count

    #Returns the number of errors
    def get_error(self):
        error = self.error_num
        self.error_num = 0
        return error

    #Checks if port is open
    def check_port(self):
        return self.serial.is_open()
#####################################################################
    
class Sendpack:

    #Predefined data packet that is sent over serial
    package=bytes("\x56\x5a\x00\x01\x0b\x01\xf2", 'UTF-8')

    #Class constructor
    def __init__(self,pt):
        self.connected = False

        #Attempts to connect to the port
        try:
            self.connection = serial.Serial(pt)
            self.connected = True
        except SerialException:
            print("This is not the port your looking for... Move along.")
            return
        
        self.settings()
    
    #Sets the serial port connection settings
    def settings(self):
        self.connection.baudrate = 57600
        self.connection.bytesize = serial.EIGHTBITS
        self.connection.parity = serial.PARITY_NONE
        self.connection.stopbits = serial.STOPBITS_ONE
    
    #Sends the predefined package called 'package' at the top
    def send(self):
        if self.connection.isOpen():
            self.connection.write(self.package)

    #if connected, return true
    def is_open(self):
        return self.connected
    
    #Closes the port when program closes 
    def __del__(self):
        if self.connected:
            self.connection.close()



#Main loop
if __name__=='__main__':
    GUI()
