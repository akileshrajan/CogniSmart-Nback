import kivy
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.lang import Builder
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.config import Config
from kivy.core.window import Window
import numpy as np
import cv2, sys,os, datetime, re
from threading import Thread
kivy.require('1.9.0')

import MUSE_Server as mps
# from .MUSE_Server import MuseServer as mps
# import MUSE_Server as mps

# Load the kivy file
Builder.load_file("main.kv")
Clock.max_iteration = 70


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

# class KeyboardListner
# Initialize variables
class NbackMain(Screen,FloatLayout):

    def on_text_change(self, usr_id):
        global User_ID
        User_ID = str(usr_id)

    def on_blkid_change(self, b_id):
        global Block_Id
        Block_Id = b_id

    def on_gametype_change(self, g_type):
        global game_type
        game_type = int(g_type)

    def start_game(self):
        # game = nbackGame()
        # global timer
        # timer = Clock.schedule_interval(game.timercallback, 1)
        # Create path to store images if not there
        global User_ID, stimuli_type
        path_im = os.path.join(store_data_path,'images')
        if not os.path.exists(path_im):
            os.makedirs(path_im)
            path_im = os.path.abspath(path_im)

        # Create path to store eeg if not there
        path_eeg = os.path.join(store_data_path , 'eeg')
        if not os.path.exists(path_eeg):
            os.makedirs(path_eeg)
            path_eeg = os.path.abspath(path_eeg)

        user_folder_name = "user_"+User_ID+"_"+stimuli_type

        path_im = os.path.join(path_im, user_folder_name)
        if not os.path.exists(path_im):
            os.makedirs(path_im)

        path_eeg = os.path.join(path_eeg, user_folder_name)
        if not os.path.exists(path_eeg):
            os.makedirs(path_eeg)

        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = 'game_screen'
        self.manager.get_screen('game_screen').start_game()


class NbackGame(Screen,FloatLayout):
    def __init__(self, **kw):
        super(NbackGame, self).__init__(**kw)
        self.inst_path = "../AppData/Nback_visual/" # Location of the list of files we display as instructions
        self.re_pattern = '[0-9]+_'                 # Regex to read only the instruction files.
        self.inst_files = []                        # List of files that we display for instructions
        self.curr_stimuli = []
        self.key_stroke = ''
        self.user_response = []

        global total_stimuli
        self.stimuli_id = total_stimuli -1

        self.timer = None                           # timer event scheduler
        self.back_0_scheduler= None                 # 0-back event scheduler
        self.back_2_scheduler = None                # 2_back event scheduler
        self.blank_scheduler = None                 # blank image event scheduler

    def start_game(self):
        self.timer = Clock.schedule_interval(self.timercallback, 1)

    def timercallback(self, val):
        global timer_val, timer
        timer_val -= 1
        # print(timer_val)
        self.ids['timer'].text = str(timer_val)
        if timer_val == 0:
            self.ids['timer'].text = ''
            self.timer.cancel()
            self.generate_instruction()

    def generate_instruction(self):
        global game_type, Block_Id
        import numpy as np
        # print("Block ID", Block_Id, "Game type", game_type)

        self.inst_files = [item for item in os.listdir(self. inst_path) if re.match(self.re_pattern, item)]
        np.random.shuffle(self.inst_files)

        if game_type == 0:
            self.ids["instruction"].source = "../AppData/Nback_visual/inst_0-back.png"
            self.ids["instruction"].opacity = 1
            Clock.schedule_once(self.generate_0back_seq,5)

        elif game_type == 2:
            self.ids["instruction"].source = "../AppData/Nback_visual/inst_2-back.png"
            self.ids["instruction"].opacity = 1
            Clock.schedule_once(self.generate_2back_seq,5)

    def generate_0back_seq(self,_):
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

        # Take the entire list of 64 images and show it randomly. Will have 8 targets.
        self.ids["instruction"].opacity = 0
        self.back_0_scheduler = Clock.schedule_interval(self.set_instructions,2)
        # self.blank_scheduler = Clock.schedule_interval(self.set_blanks, 2)

    def generate_2back_seq(self,_):
        print(_)

    def set_instructions(self,_):
        self.ids["stimuli"].source = os.path.join(self.inst_path + self.inst_files[self.stimuli_id])
        self.ids["stimuli"].opacity = 1
        self.stimuli_id -= 1
        self.key_stroke = ''    # Setting user key stroke to empty for every round.
        self.curr_stimuli.append(self.inst_files[self.stimuli_id])
        if self.key_stroke == '':
            self.user_response.append(self.key_stroke)
        print("In set inst", self.user_response)
        if self.stimuli_id == 0:
            self.ids["stimuli"].opacity = 0
            self.back_0_scheduler.cancel()
            # self.log_and_terminate()

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):

        if keycode[1] == 'spacebar':
            # self.user_response.append(keycode[1])
            self.key_stroke = keycode[1]
            print(self.key_stroke, self.curr_stimuli)
            # self.check_response()

        return True


class NbackApp(App):
    def build(self):
        screen_mgr = ScreenManager()
        screen_mgr.add_widget(NbackMain(name='main_screen'))
        screen_mgr.add_widget(NbackGame(name='game_screen'))

        return screen_mgr


def main(stimuli, data_path):
    """
    This is the main function of the game. The starting point.

    :param game: Type of game. Two possible inputs. 0-back = '0', 2-back = '2'
    :param user: User ID. dtype = str. eg: 'test_user', '0', '1', '2'...
    :param stimuli: Type of Stimuli. Two possible stimuli. Visual = 'v', audio '0'
    :param data_path: Location to store the data. In my case "/media/akilesh/data/fatigue_fitbit"
    :return: No return value.
    """

    #defining global variables for application
    global User_ID, modality, Block_Id, quit, store_data_path, timer_val, game_type, stimuli_type

    global total_stimuli    # Total number of stimuli being presented to the user
    global correct_press    # Total number of times the user pressed the space bar for the correct target
    global correct_miss     # Total number of times the user missed the space-bar for the correct non-target
    global total_false      # Total number of times the user pressed the space-bar for the incorrect target
    global incorrect_miss   # Total number of times the user missed the space-bar for the correct target
    global score            # Overall percentage of correct hits and miss.
    global corrects_acc     # Percent of correct hits
    global incorrects_acc   # Percent of incorrect hits out of non-target.
    global reaction_time    # Reaction time for each stimuli

    Config.set('graphics', 'width', str(1500))
    Config.set('graphics', 'height', str(1000))

    # Parameter initialization
    store_data_path =data_path
    # game_type = game
    total_stimuli = 64
    # Block_Id = block_id
    quit = False
    timer_val = 5
    stimuli_type = stimuli
    # User_ID = str(user_id)
    correct_press, correct_miss, total_false, incorrect_miss = 0,0,0,0

    # Run game and recording into threads
    thread1 = Thread(target=NbackApp().run())
    thread1.start()

    # thread2 = Thread(target=readFrames, args=(path_im,))
    # thread2.start()
    #
    # thread3 = Thread(target=readMuse, args=(path_eeg,))
    # thread3.start()

    thread1.join()
    # thread2.join()
    # thread3.join()


if __name__ == '__main__':
   main('v','/media/akilesh/data/fatigue_fitbit')
   # main('v','/Users/akileshrajavenkatanarayanan/data/')
