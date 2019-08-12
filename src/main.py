import kivy
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from functools import partial
import numpy as np
import cv2
import sys,os
import _pickle as cPickle
from threading import Thread
import datetime
from kivy.config import Config
import keyboard
kivy.require('1.9.0')

# from levels import main_game,original_game
import src.MUSE_Server as mps


def readMuse(path):
    global server,round_set,user_id, round_id, quit
    intro = open('test', 'w')
    server = mps.initialize(intro)
    server.start()
    round_id = None
    prev_round = round_id
    while(True):
        if round_id != prev_round:
            eeg_name = ('/').join((path,str(round_set) + "_" + str(round_id)))
            out = open(eeg_name, 'w')
            server.f = out
            prev_round = round_id
        if quit:
            server.stop()
            break


def readFrames(path):
    global round_set, User_ID, round_id, quit, modality, store_data_path
    frameCounter = 1
    cap = cv2.VideoCapture(0)
    frame_struct = []

    while (True):
        ret, frame = cap.read()
        if frameCounter % 10 == 0:
            # cv2.imshow('frame',frame)
            if round_set > len(frame_struct) - 1:
                frame_struct.append([])
            frame_struct[round_set].append(frame)
            fname = str(round_set) + "_" + str(round_id) + "_" + str(frameCounter) + "_" + str(
                datetime.datetime.time(datetime.datetime.now())) + ".jpg"
            cv2.imwrite(os.path.join(path, fname), frame)
        frameCounter += 1

        if quit:
            filename = store_data_path + "/images/user_" + User_ID + '_' + modality + "/data"
            np.save(filename, frame_struct)
            break

    # When everything done, release the capture
    cap.release()
    sys.exit()
    # cv2.destroyAllWindows()


# Initialize variables
class NbackGame(FloatLayout):


class NbackApp(App):
    def build(self):
        return NbackGame()


def main(game,user_id,stimuli,data_path):
    """
    This is the main function of the game. The starting point.

    :param game: Type of game. Two possible inputs. 0-back = '0', 2-back = '2'
    :param user: User ID. dtype = str. eg: 'test_user', '0', '1', '2'...
    :param stimuli: Type of Stimuli. Two possible stimuli. Visual = 'v', audio '0'
    :param data_path: Location to store the data. In my case "/media/akilesh/data/fatigue_fitbit"
    :return: No return value.
    """

    global User_ID, email, modality, round_set, round_id, quit, game_type, store_data_path
    Config.set('graphics', 'width', str(1000))
    Config.set('graphics', 'height', str(1000))

    # Parameter initialization
    store_data_path =data_path
    game_type = game
    round_set = 0
    quit = False

    # Create path to store images if not there
    path_im = store_data_path+ '/images/'
    if not os.path.exists(path_im):
        os.makedirs(path_im)
        path_im = os.path.abspath(path_im)

    # Create path to store eeg if not there
    path_eeg = store_data_path + '/eeg/'
    if not os.path.exists(path_eeg):
        os.makedirs(path_eeg)
        path_eeg = os.path.abspath(path_eeg)

    user_folder_name = "user_"+user_id+"_"+stimuli
    User_ID = user_id

    path_im = path_im + user_folder_name
    if not os.path.exists(path_im):
        os.makedirs(path_im)
    path_eeg = path_eeg + user_folder_name
    if not os.path.exists(path_eeg):
        os.makedirs(path_eeg)

    # Run game and recording into threads
    thread1 = Thread(target=NbackApp().run)
    thread1.start()

    thread2 = Thread(target=readFrames, args=(path_im,))
    thread2.start()

    thread3 = Thread(target=readMuse, args=(path_eeg,))
    thread3.start()

    thread1.join()
    thread2.join()
    thread3.join()


if __name__ == '__main__':
   main('m','test_user','v','/media/akilesh/data/fatigue_fitbit')