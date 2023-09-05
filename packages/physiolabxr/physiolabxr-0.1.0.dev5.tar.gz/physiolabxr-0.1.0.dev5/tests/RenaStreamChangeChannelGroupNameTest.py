"""
If you have get file not found error, make sure you set the working directory to .../RealityNavigation/physiolabxr
Otherwise, you will get either import error or file not found error
"""

# reference https://www.youtube.com/watch?v=WjctCBjHvmA
import os
import sys
from multiprocessing import Process

import pytest
from PyQt6 import QtWidgets
from pytestqt.qtbot import QtBot
from physiolabxr.configs.configs import AppConfigs
AppConfigs(_reset=True)  # create the singleton app configs object

from physiolabxr.ui.MainWindow import MainWindow
from physiolabxr.startup.startup import load_settings
from tests.TestStream import LSLTestStream


@pytest.fixture
def app(qtbot: QtBot):
    print('Initializing test fixture for ' + 'Visualization Features')
    print(os.getcwd())
    # ignore the splash screen and tree icon
    app = QtWidgets.QApplication(sys.argv)
    # app initialization
    load_settings(revert_to_default=True, reload_presets=True)  # load the default settings
    test_renalabapp = MainWindow(app=app, ask_to_close=False)  # close without asking so we don't pend on human input at the end of each function test fixatire
    # test_renalabapp.show()
    qtbot.addWidget(test_renalabapp)
    return test_renalabapp

def teardown_function(function):
    """ teardown any state that was previously setup with a setup_method
    call.
    """
    pass

def test_change_channel_name(app_main_window, qtbot) -> None:
    '''
    Adding active stream
    :param app:
    :param qtbot:
    :return:
    '''
    test_stream_name = 'TestStreamName'
    p = Process(target=LSLTestStream, args=(test_stream_name,))
    p.start()


    print("Test complete, killing sending-data process")
    p.kill()  # stop the dummy LSL process


def test_change_group_name(app_main_window, qtbot) -> None:
    '''
    Adding active stream
    :param app:
    :param qtbot:
    :return:
    '''
    test_stream_name = 'TestStreamName'
    p = Process(target=LSLTestStream, args=(test_stream_name,))
    p.start()


    print("Test complete, killing sending-data process")
    p.kill()  # stop the dummy LSL process

def test_change_channel_name_multiple_times(app_main_window, qtbot) -> None:
    '''
    Adding active stream
    :param app:
    :param qtbot:
    :return:
    '''
    test_stream_name = 'TestStreamName'
    p = Process(target=LSLTestStream, args=(test_stream_name,))
    p.start()


    print("Test complete, killing sending-data process")
    p.kill()  # stop the dummy LSL process


def test_change_channel_name_in_changed_group(app_main_window, qtbot) -> None:
    test_stream_name = 'TestStreamName'
    p = Process(target=LSLTestStream, args=(test_stream_name,))
    p.start()


    print("Test complete, killing sending-data process")
    p.kill()  # stop the dummy LSL process

def test_change_channel_name_after_create_new_group(app_main_window, qtbot) -> None:
    # add new preset
    # create group
    # rearrange channels between groups
    test_stream_name = 'TestStreamName'
    p = Process(target=LSLTestStream, args=(test_stream_name,))
    p.start()


    print("Test complete, killing sending-data process")
    p.kill()  # stop the dummy LSL process