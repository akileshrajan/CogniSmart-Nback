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
import pandas as pd
import cv2, sys, os, datetime, re, time
from threading import Thread

kivy.require('1.9.0')

import MUSE_Server as mps
from src.sequences import practice_0back, practice_2back, seq_2back
# from .MUSE_Server import MuseServer as mps
# import MUSE_Server as mps

# Load the kivy file
Builder.load_file("main.kv")
Clock.max_iteration = 70


def readMuse(path):
    global server, round_set, user_id, round_id, quit
    intro = open('test', 'w')
    server = mps.initialize(intro)
    server.start()
    round_id = None
    prev_round = round_id
    while (True):
        if round_id != prev_round:
            eeg_name = ('/').join((path, str(round_set) + "_" + str(round_id)))
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
class NbackMain(Screen, FloatLayout):
    def __init__(self, **kw):
        super(NbackMain,self).__init__(**kw)
        self.path_usr = None
        self.path_eeg = None
        self.path_im = None

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
        global User_ID, store_data_path, Block_Id
        user_folder_name = "user_" + str(User_ID)
        # self.path_usr = os.path.join(store_data_path,user_folder_name)
        user_folder = os.path.join(store_data_path,user_folder_name)
        if not os.path.exists(user_folder):
            os.mkdir(user_folder)
            user_folder = os.path.abspath(user_folder)

        block_folder_name = 'block'+str(Block_Id)
        self.path_usr = os.path.join(user_folder, block_folder_name)
        if not os.path.exists(self.path_usr):
            os.mkdir(self.path_usr)
            self.path_usr = os.path.abspath(self.path_usr)

        self.path_im = os.path.join(self.path_usr, 'images')
        if not os.path.exists(self.path_im):
            os.makedirs(self.path_im)
            self.path_im = os.path.abspath(self.path_im)

        # Create path to store eeg if not there
        self.path_eeg = os.path.join(self.path_usr, 'eeg')
        if not os.path.exists(self.path_eeg):
            os.makedirs(self.path_eeg)
            self.path_eeg = os.path.abspath(self.path_eeg)

        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = 'game_screen'
        self.manager.get_screen('game_screen').start_game()


class NbackGame(Screen, FloatLayout):
    def __init__(self, **kw):
        super(NbackGame, self).__init__(**kw)
        self.inst_path = "../AppData/Nback_visual/"  # Location of the list of files we display as instructions
        self.re_pattern = '[0-9]+_'  # Regex to read only the instruction files.
        self.inst_files = []  # List of files that we display for instructions
        self.curr_stimuli = []
        self.stimuli = ''
        self.key_stroke = ''
        self.user_response = []
        self.expected_resp = []     # Expected responses for 2-back tasks

        self.stimuli_id = 0

        self.start_time = None  # start time for each round
        self.end_time = None # end time for each round

        self.back_0_scheduler, self.practice_0back_scheduler = None, None  # 0-back event scheduler
        self.back_2_scheduler, self.practice_2back_scheduler = None, None  # 2_back event scheduler

    def start_game(self):
        self.timer = Clock.schedule_interval(self.timercallback, 1)

    def timercallback(self, _):
        """
        Function to generate the countdown at the beginning of the game.
        :param _:
        :return: No return value
        """
        global timer_val, timer
        timer_val -= 1
        # print(timer_val)
        self.ids['timer'].text = str(timer_val)
        if timer_val == 0:
            self.ids['timer'].text = ''
            self.timer.cancel()
            self.check_gametype()

    def check_gametype(self):
        """
        Function to check game time and start setting instructions
        :return:
        """
        global game_type, Block_Id, total_stimuli

        # print("Block ID", Block_Id, "Game type", game_type)
        if game_type == 0 and Block_Id not in 'Practice':
            self.ids["instruction"].source = "../AppData/Nback_visual/inst_0-back.png"
            self.ids["instruction"].opacity = 1
            Clock.schedule_once(self.generate_0back_seq, 5)
            self.inst_files = [item for item in os.listdir(self.inst_path) if re.match(self.re_pattern, item)]
            # print(self.inst_files)
            np.random.shuffle(self.inst_files)
            total_stimuli = 64
        elif game_type == 2 and Block_Id not in 'Practice':
            self.ids["instruction"].source = "../AppData/Nback_visual/inst_2-back.png"
            self.ids["instruction"].opacity = 1
            Clock.schedule_once(self.generate_2back_seq, 6)
            total_stimuli = 64
        elif game_type == 0 and Block_Id == 'Practice':
            self.ids["instruction"].source = "../AppData/Nback_visual/inst_0-back.png"
            self.ids["instruction"].opacity = 1
            total_stimuli = 16
            Clock.schedule_once(self.generate_0back_practice, 5)
        elif game_type == 2 and Block_Id == 'Practice':
            self.ids["instruction"].source = "../AppData/Nback_visual/inst_2-back.png"
            self.ids["instruction"].opacity = 1
            total_stimuli = 16
            Clock.schedule_once(self.generate_2back_practice, 6)

    def generate_0back_seq(self, _):
        """
        Function to generate 0-back instructions
        :param _: dt
        :return: None
        """
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

        # Take the entire list of 64 images and show it randomly. Will have 8 targets.
        self.ids["instruction"].opacity = 0
        self.back_0_scheduler = Clock.schedule_interval(self.generate_0back_inst, 2)

    def generate_0back_practice(self,_):
        """
        Function to generate 0-back sequence for practice. For practice, we will use predefined sequence.
        It will be same for everyone.
        :param _: dt
        :return: None
        """
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self.ids["instruction"].opacity = 0
        self.inst_files = practice_0back()
        self.practice_0back_scheduler = Clock.schedule_interval(self.generate_0back_inst, 2)

    def generate_2back_seq(self, _):
        global total_stimuli
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

        # Take the entire list of 64 images and show it randomly. Will have 8 targets.
        self.ids["instruction"].opacity = 0
        files_list = [item for item in os.listdir(self.inst_path) if re.match(self.re_pattern, item)]
        self.inst_files, self.expected_resp = seq_2back(files_list, total_stimuli)
        self.back_2_scheduler = Clock.schedule_interval(self.generate_2back_inst, 2.5)

    def generate_2back_practice(self,_):
        """
        Function to generate 2-back sequence for practice. For practice, we will use predefined sequence.
        It will be same for everyone.
        :param _:
        :return:
        """
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self.ids["instruction"].opacity = 0
        self.inst_files, self.expected_resp = practice_2back()
        self.practice_2back_scheduler = Clock.schedule_interval(self.generate_2back_inst, 2)

    def generate_0back_inst(self, _):

        self.start_time = time.time()   # Starting the timer for calculation reaction time

        global total_stimuli, reaction_time, game_type
        # print("In set inst", self.user_response)
        if self.stimuli_id >= total_stimuli:
            self.ids["stimuli"].opacity = 0
            if Block_Id == 'Practice':
                self.practice_0back_scheduler.cancel()
            else:
                self.back_0_scheduler.cancel()
            self._log_and_terminate()
        else:
            self.stimuli = self.inst_files[self.stimuli_id]     # grabbing the first instruction
            self.stimuli_id += 1    # looping through the list of stimuli

        self.ids["stimuli"].source = os.path.join(self.inst_path + self.stimuli)    # setting the stimuli label
        self.ids["stimuli"].opacity = 1

        self.key_stroke = ''  # Setting user key stroke to empty for every round.
        self.curr_stimuli.append(self.stimuli)
        self.user_response.append('')
        reaction_time.append(0)

    def generate_2back_inst(self, _):
        self.start_time = time.time()       # Starting the timer for calculation reaction time

        global total_stimuli, reaction_time, game_type

        if self.stimuli_id >= total_stimuli:
            self.ids["stimuli"].opacity = 0
            if Block_Id == 'Practice':
                self.practice_2back_scheduler.cancel()
            else:
                self.back_2_scheduler.cancel()
            self._log_and_terminate()
        else:
            self.stimuli = self.inst_files[self.stimuli_id]     # grabbing the first instruction
            self.stimuli_id += 1    # looping through the list of stimuli

        self.ids["stimuli"].source = os.path.join(self.inst_path + self.stimuli)    # setting the stimuli label
        self.ids["stimuli"].opacity = 1
        self.key_stroke = ''  # Setting user key stroke to empty for every round.
        self.curr_stimuli.append(self.stimuli)
        self.user_response.append('')
        reaction_time.append(0)

    def set_blanks(self, _):
        self.ids["stimuli"].source = os.path.join(self.inst_path + 'blank.png')    # setting the stimuli label
        self.ids["stimuli"].opacity = 1

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        global reaction_time, game_type

        if keycode[1] == 'spacebar':
            print(len(reaction_time), self.stimuli_id)
            self.end_time = time.time()
            reaction_time[self.stimuli_id-1] = (round((self.end_time - self.start_time),4))
            self.user_response[self.stimuli_id-1] = keycode[1]
            self.key_stroke = keycode[1]
            # print(self.key_stroke, self.curr_stimuli)
            if 'heart' in self.stimuli and game_type == 0:
                self.positive_feedbeck()
            elif 'heart' not in self.stimuli and game_type == 0:
                self.negative_feedback()
            elif game_type == 2:
                if self.expected_resp[self.stimuli_id-1] == 1:
                    self.positive_feedbeck()
                elif self.expected_resp[self.stimuli_id-1] == 0:
                    self.negative_feedback()
        elif keycode[1] == 'escape':
            App.get_running_app().stop()
        else:
            self.end_time = time.time()
            reaction_time[self.stimuli_id-1] = (round((self.end_time - self.start_time),4))
            self.user_response[self.stimuli_id-1] = 'wrong_key'
            self.key_stroke = keycode[1]
            self.negative_feedback()

        return True

    def _log_and_terminate(self):
        print(len(self.user_response), len(self.curr_stimuli), '\n', self.curr_stimuli, '\n', self.user_response)

        global User_ID, Block_Id, game_type, quit
        quit = True
        if game_type == 0:
            self._check_0back_response()    # check user's response for each round
        elif game_type == 2:
            self._check_2back_response()    # check user's response for each round

        global total_stimuli
        global correct_press, incorrect_press, incorrect_miss, correct_miss, score, reaction_time

        # convert the numpy arrays into a data frame and save it to a file
        final_data = pd.DataFrame()
        final_data['Stimuli'] = self.curr_stimuli
        final_data['User Resp'] = self.user_response
        final_data['Expected Resp'] = self.expected_resp
        final_data['Total corr press'] = correct_press
        final_data['Total incor press'] = incorrect_press
        final_data['Total corr miss'] = correct_miss
        final_data['Total incorr miss'] = incorrect_miss
        final_data['Score'] = score
        final_data['Reaction Time'] = reaction_time

        # get save path
        # file_save_path = self.manager.get_screen('main_screen').path_usr
        #
        # op_filename = str(User_ID)+'_'+str(Block_Id)+'_'+str(game_type)+'.csv'
        file_path = os.path.join(self.manager.get_screen('main_screen').path_usr, str(User_ID)+'_'+str(Block_Id)+'_'+str(game_type)+'.csv')
        print(final_data,'\n', file_path)
        export_csv = final_data.to_csv(file_path, index=None, header= True)

        App.get_running_app().stop()

    def _check_0back_response(self):
        global correct_press, incorrect_press, incorrect_miss, correct_miss     # final list
        corr_press, incorr_press, corr_miss, incorr_miss = 0, 0, 0, 0

        for idx, item in enumerate(self.curr_stimuli):
            if 'heart' in item and self.user_response[idx] == 'spacebar':
                corr_press +=1
            elif 'heart' not in item and self.user_response[idx] != 'spacebar':
                corr_miss += 1

            elif 'heart' not in item and self.user_response[idx] == 'spacebar' or self.user_response[idx] == 'wrong_key':
                incorr_press += 1

            elif 'heart' in item and self.user_response[idx] != 'spacebar':
                incorr_miss += 1

            # Append data into the final list
            correct_press.append(corr_press)
            correct_miss.append(corr_miss)
            incorrect_press.append(incorr_press)
            incorrect_miss.append(incorr_miss)
            # Score is calculated as the difference between the total correct percent and total wrong percent.
            score.append((((corr_press+corr_miss) / total_stimuli) * 100) - (((incorr_miss + incorr_press)/total_stimuli)*100))

    def _check_2back_response(self):
        global correct_press, incorrect_press, incorrect_miss, correct_miss     # final list
        corr_press, incorr_press, corr_miss, incorr_miss = 0, 0, 0, 0

        for idx, item in enumerate(self.user_response):
            if self.user_response[idx] == 'spacebar' and self.expected_resp[idx] == 1:
                corr_press += 1
            elif self.user_response[idx] != 'spacebar' and self.expected_resp[idx] == 0:
                corr_miss += 1
            elif self.user_response[idx] == 'spacebar' or self.user_response[idx] == 'wrong_key' and self.expected_resp[idx] ==0:
                incorr_press += 1
            elif self.user_response[idx] != 'spacebar' and self.expected_resp[idx] == 1:
                incorr_miss += 1

            # Append data into the final list
            correct_press.append(corr_press)
            correct_miss.append(corr_miss)
            incorrect_press.append(incorr_press)
            incorrect_miss.append(incorr_miss)
            # Score is calculated as the difference between the total correct percent and total wrong percent.
            score.append((((corr_press+corr_miss) / total_stimuli) * 100) - (((incorr_miss + incorr_press)/total_stimuli)*100))

    # Helper functions to generate audio feedback
    def positive_feedbeck(self):
        sound = SoundLoader.load('../AppData/correct_sound.wav')
        sound.play()

    def negative_feedback(self):
        sound = SoundLoader.load('../AppData/wrong_sound.wav')
        sound.play()


class NbackApp(App):
    def build(self):
        screen_mgr = ScreenManager()
        screen_mgr.add_widget(NbackMain(name='main_screen'))
        screen_mgr.add_widget(NbackGame(name='game_screen'))

        return screen_mgr


def main(stimuli, data_path):
    """
    This is the main function of the game. The starting point.
    :param stimuli: Type of Stimuli. Two possible stimuli. Visual = 'v', audio '0'
    :param data_path: Location to store the data. In my case "/media/akilesh/data/fatigue_fitbit"
    :return: No return value.
    """

    # defining global variables for application
    global User_ID, modality, Block_Id, quit, store_data_path, timer_val, game_type, stimuli_type

    global total_stimuli  # Total number of stimuli being presented to the user
    global correct_press  # Total number of times the user pressed the space bar for the correct target
    correct_press = []

    global correct_miss  # Total number of times the user missed the space-bar for the correct non-target
    correct_miss = []

    global incorrect_press  # Total number of times the user pressed the space-bar for the incorrect target
    incorrect_press = []

    global incorrect_miss  # Total number of times the user missed the space-bar for the correct target
    incorrect_miss = []

    global score  # Overall percentage of correct hits and miss minus the total number of incorrect hits and miss.
    score = []

    global reaction_time  # Reaction time for each stimuli
    reaction_time = []

    Config.set('graphics', 'width', str(1500))
    Config.set('graphics', 'height', str(1000))

    # Parameter initialization
    store_data_path = data_path
    # game_type = game

    # Block_Id = block_id
    quit = False
    timer_val = 5
    stimuli_type = stimuli
    # User_ID = str(user_id)

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
    # main('v', '/Users/akileshrajavenkatanarayanan/data/')
