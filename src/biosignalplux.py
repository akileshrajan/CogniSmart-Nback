import plux, datetime, time


class bcolors:
    ENDC = '\033[0m'

    ERROR = '\033[1;31m'
    WARNING = '\033[30;41m'

    GOOD =  '\033[1;96m'

    BOLD = '\033[1m'

    MBIENT = '\033[34m'
    BCI = '\033[35m'
    PLUX = '\033[36m'

# Initialize Plux Device
dev = None

# Initialize Plux Loop Interrupt
exitPluxLoop = False

plux_file = None

PluxLoggingFlag = None

ready = 0

paused = False

class MyDevice(plux.MemoryDev):
    # Callbacks override
    def onRawFrame(self, nSeq, data):
        global exitPluxLoop
        global PluxLoggingFlag
        global plux_file
        global paused
        if PluxLoggingFlag:

            if plux_file is not None:
                plux_file.write("{0:s}, {1:f}, {2:f}\n".format(str(datetime.datetime.time(datetime.datetime.now())), data[0], data[1]))
            else:
                print (bcolors.ERROR + "--Plux-- ERROR at RawFrame() - Can't write to file" + bcolors.ENDC)

        # if nSeq % 1000 == 0 and not paused:
        #    print (bcolors.PLUX + "--Plux-- ", nSeq, data  , bcolors.ENDC)# Print out a data frame every 1000 frames

        if exitPluxLoop:
            print (bcolors.GOOD + "--Plux-- Exiting Plux Loop" + bcolors.ENDC)
            return True

        return False

    def onEvent(self, event):
        if type(event) == plux.Event.DigInUpdate:
            print (bcolors.PLUX + '--Plux-- Digital input event - Clock source:', event.timestamp.source,
                   ' Clock value:', event.timestamp.value, ' New input state:', event.state, bcolors.ENDC)
        elif type(event) == plux.Event.SchedChange:
            print ('--Plux-- Schedule change event - Action:', event.action,
                   ' Schedule start time:', event.schedStartTime)
        elif type(event) == plux.Event.Sync:
            print ('--Plux-- Sync event:')
            for tstamp in event.timestamps:
                print (' Clock source:', tstamp.source, ' Clock value:', tstamp.value)
        elif type(event) == plux.Event.Disconnect:
            print ('--Plux-- Disconnect event - Reason:', event.reason)
            return True # Exit loop() after receiving a disconnect event
        return False
        
    def onInterrupt(self, param):
        print ('--Plux-- Interrupt:', param)
        return False

    def onTimeout(self):
        print ('--Plux-- Timeout')
        return False

    def onSessionRawFrame(self, nSeq, data):
        print (self.f, nSeq, self.lastDigState,)
        for val in data:
            print (self.f, val,)
        print (self.f)
        if nSeq % 1000 == 0:
            print ('--Plux-- Session:', nSeq, data)
        return False

    def onSessionEvent(self, event):
        if type(event) == plux.Event.DigInUpdate:
            print ('--Plux-- Session digital input event - Clock source:', event.timestamp.source,
                   ' Clock value:', event.timestamp.value, ' New input state:', event.state)
            self.lastDigState = 1 if event.state else 0
        elif type(event) == plux.Event.Sync:
            print ('--Plux-- Session sync event:')
            for tstamp in event.timestamps:
                print (' Clock source:', tstamp.source, ' Clock value:', tstamp.value)
        return False


def PluxDataFile(path, user_id, block_id, game_type):
    global plux_file

    try:
        # current_time = datetime.datetime.now().strftime('%Y-%m-%d__%H.%M.%S.%f')
        if block_id == "Baseline":
            _filename = "%s/Plux-%s_%s.csv" % (path, str(user_id),str(block_id))
        else:
            _filename = "%s/Plux-%s_%s_%s.csv" % (path, str(user_id),str(block_id),str(game_type))

        if plux_file is not None:
            plux_file.close()
            plux_file = None

        plux_file = open(_filename, "w")
        plux_file.write("{0}, {1}, {2}\n".format('Time', 'ECG', 'GSR'))
        print (bcolors.PLUX + "--Plux-- %s is created" % _filename + bcolors.ENDC)

    except Exception as e:
        print (bcolors.ERROR + "--Plux-- Error: Inside PluxDataFile()" + bcolors.ENDC)
        print (e)
        exit(0)


def PluxConnect():
    global dev
    global exitPluxLoop
    global PluxLoggingFlag
    global ready

    try:
        dev = MyDevice("00:07:80:4D:2E:DE")  # MAC address of device

        props = dev.getProperties()  # get and print device properties
        if props is  not None:
            print (bcolors.GOOD + "--Plux-- Connection is established" + bcolors.ENDC)

        # PluxLoggingFlag = False
        exitPluxLoop = False


        dev.start(1000, 0x03, 16)  # 1000 Hz, ports 1-2, 16 bits
        print (bcolors.GOOD + "--Plux-- Started Streaming" + bcolors.ENDC)

        ready = 1

        dev.loop()  # returns after receiving 10000 frames (onRawFrame() returns True)
        # print "--Plux-- Stopping Plux Connection"
        time.sleep(0.01)
        dev.stop()
        print (bcolors.GOOD + "--Plux-- Stopped Plux Connection" + bcolors.ENDC)

    except Exception as e:
        print (bcolors.ERROR +  "--Plux-- Error: Inside PluxConnect()" + bcolors.ENDC)
        ready = -1
        print(bcolors.ERROR + str(e) + bcolors.ENDC)
        if (dev):
            dev.close()
        # exit(0)


def PluxStart(path, User_ID, Block_Id, game_type):
    global dev
    global exitPluxLoop
    global PluxLoggingFlag
    global paused

    PluxDataFile(path, User_ID, Block_Id, game_type)

    PluxLoggingFlag = True
    exitPluxLoop = False
    paused = False

    print(bcolors.GOOD + "--Plux-- Starting to Log Data" + bcolors.ENDC)


def PluxPause():
    global PluxLoggingFlag
    global exitPluxLoop
    global paused
    global plux_file

    print(bcolors.GOOD + "--Plux-- Pausing Plux " + bcolors.ENDC)

    exitPluxLoop = False
    PluxLoggingFlag = False
    paused = True

    if plux_file is not None:
        time.sleep(0.01)
        plux_file.close()
        plux_file = None
        print(bcolors.GOOD + "--Plux-- Closed Plux File " + bcolors.ENDC)


def PluxRestart(path, User_ID, Block_Id, game_type):
    global dev
    global exitPluxLoop
    global PluxLoggingFlag
    global paused

    PluxDataFile(path, User_ID, Block_Id, game_type)

    exitPluxLoop = False
    PluxLoggingFlag = True
    paused = False

    print(bcolors.GOOD + "--Plux-- Re-Starting to Log Data" + bcolors.ENDC)


def PluxClose():
    global dev
    global plux_file
    global exitPluxLoop
    global PluxLoggingFlag

    PluxLoggingFlag = False
    exitPluxLoop = True

    if dev is not None:
        # print "--Plux-- Closing Plux Connection after 0.1s"
        time.sleep(0.2)
        dev.close()
        print(bcolors.GOOD + "--Plux-- Closed Plux Connection" + bcolors.ENDC)
    else:
        print(bcolors.ERROR + "--Plux-- Error: Dev is not initialized - Line 233" + bcolors.ENDC)
        # exit()

    if plux_file is not None:
        # print "--Plux-- Closing Plux File after 0.01s"
        time.sleep(0.01)
        plux_file.close()
        plux_file = None
        print(bcolors.GOOD + "--Plux-- Closed Plux File" + bcolors.ENDC)

######  Comments  ######

# convert Time from Seconds to Readable time
#       print datetime.datetime.fromtimestamp(1549592260.189008).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
#       print datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')