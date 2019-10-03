import numpy as np
import threading, time, cv2, sys, os, datetime

import biosignalplux as bsp
import MUSE_Server as mps

global quit

quit = False


class SensorsHandler(threading.Thread):
    def __init__(self, thread_name, path,user_id, block_id, game_type):
        threading.Thread.__init__(self)
        self.name = thread_name
        self.save_path = path
        self.user_id = user_id
        self.block_id = block_id
        self.game_type = game_type
        self.ExitThread = False
        self.Restart = False

        if self.name =="Plux":
            self.path_bsp = None
        if self.name == "Camera":
            self.path_im = None
        if self.name == "Muse":
            self.path_eeg = None

        self.muse_thread = None
        self.cam_thread = None

    def run(self):
        if self.name =="Plux":
            print("## Connecting biosignalsplux sensors ##")
            self.connect_sensor()

        while not self.ExitThread:
            time.sleep(0.0001)

        print("## Closing Thread##",self.name)

    def connect_sensor(self):
        """
        Handler Function to connect to the biosignalsplux sensor and create a file to write the data
        :return: None
        """
        if self.name == "Plux":
            bsp.PluxConnect()
        else:
            pass

    def start_sensor(self):
        """
        Handler Function to start recording the sensor data
        :return:
        """
        if self.name == "Plux":
            self.path_bsp = os.path.join(self.save_path, 'bsp')
            if not os.path.exists(self.path_bsp) and self.block_id != "Practice":
                os.makedirs(self.path_bsp)
                self.path_bsp = os.path.abspath(self.path_bsp)

            # Start recording the BiosignalsPlux
            bsp.PluxLoggingFlag = True
            bsp.PluxStart(self.path_bsp, self.user_id, self.block_id, self.game_type)

        elif self.name == "Camera":
            # print("## in camera")
            self.path_im = os.path.join(self.save_path, 'images')
            if not os.path.exists(self.path_im) and self.block_id != "Practice":
                os.makedirs(self.path_im)
                self.path_im = os.path.abspath(self.path_im)

            # Start recording Camera
            self.cam_thread = threading.Thread(target=read_camera, args=(self.path_im, self.user_id
                                                                         , self.block_id, self.game_type,))
            self.cam_thread.start()
            # self.read_camera()
        elif self.name == "Muse":
            # print("In muse thread")
            # Create path to store eeg if not there
            self.path_eeg = os.path.join(self.save_path, 'eeg')
            if not os.path.exists(self.path_eeg) and self.block_id != "Practice":
                os.makedirs(self.path_eeg)
                self.path_eeg = os.path.abspath(self.path_eeg)

            # Start recording the Muse
            self.muse_thread = threading.Thread(target=read_muse, args=(self.path_eeg, self.user_id
                                                                         , self.block_id, self.game_type,))
            self.muse_thread.start()
            # read_muse(self.path_eeg, self.user_id, self.block_id, self.game_type)

    def close_sensor(self):
        """
        Handler function to disconnect and close the sensor
        :return: None
        """
        global quit
        quit = True   # Set variable to stop Muse, camera

        if self.name == "Plux":
            # Set variable to stop recording from biosignalsplux
            bsp.exitPluxLoop = True
            bsp.PluxClose()

        self.ExitThread = True


def read_camera(path,user_id, block_id, game_type):
    global quit
    frameCounter = 1
    cap = cv2.VideoCapture(0)
    frame_struct = []

    while True:
        ret, frame = cap.read()
        file_name = os.path.join(path,
                                 str(user_id) + '_' + str(block_id) + '_' + str(game_type) + '_' + str(frameCounter)
                                 + '_' + str(datetime.datetime.time(datetime.datetime.now())) + '.jpg')
        cv2.imwrite(file_name, frame)
        # print("## frame write")
        frameCounter += 1

        if quit:
            # print("LALALALALA")
            cap.release()
            break

    # When everything done, release the capture
    # cap.release()
    sys.exit()
    # cv2.destroyAllWindows()


def read_muse(path,user_id, block_id, game_type):
    global quit
    intro = open('test', 'w')
    server = mps.initialize(intro)
    server.start()

    while True:
        eeg_name = os.path.join(path, str(user_id) + "_" + str(block_id) + "_" + str(game_type))
        out_file = open(eeg_name, 'a')
        # print(server.f)
        server.f = out_file

        if quit:
            server.stop()
            out_file.close()
            server.free()
            break