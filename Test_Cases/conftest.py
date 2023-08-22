import inspect
import json
import logging
import os.path
import shutil
import time
from datetime import date
from logging import Logger
from typing import Dict, Any
import allure
import pyscreenrec as pyscreenrec
import pytest
from pytest import StashKey, CollectReport
from selenium import webdriver
from moviepy.editor import VideoFileClip

from Utility.ReadConfig import ReadConfig

phase_report_key = StashKey[Dict[str, CollectReport]]()
OUTPUT_DIR = os.path.join(os.getcwd(), "Test_Cases", "Test_output")
RELEASE_DIR = os.path.join(os.getcwd(), 'Release')


@pytest.fixture(scope='class')
def driver_setup(request):
    global driver
    logs = _get_config_logs()

    browser = request.config.getoption('--browser')

    conf = ReadConfig()
    URL = conf.end_url()
    logs.info(f'{URL}index')

    if browser == 'Chrome':
        options = webdriver.ChromeOptions()
        options.add_argument(
            f"--load-extension={RELEASE_DIR}/{ReadConfig().executors()['buildname']}")
        options.add_experimental_option('prefs', {
            'download.default_directory': os.path.join(OUTPUT_DIR, 'mnemonics')
        })
        options.accept_insecure_certs = True
        driver = webdriver.Chrome(options=options)
    elif browser == 'Firefox':
        options = webdriver.FirefoxOptions()
        options.accept_insecure_certs = True
        driver = webdriver.Firefox(options=options)
    elif browser == 'Edge':
        driver = webdriver.Edge()
    elif browser == 'Safari':
        driver = webdriver.Safari()
    else:
        raise Exception('Select Valid Browser from the List:: {Chrome, Firefox, Edge, Safari}')
    logs.info(f'{str(driver.session_id), str(browser)}')
    driver.maximize_window()
    driver.implicitly_wait(15)
    create_json(f'caps.json', driver.capabilities)
    request.cls.driver = driver
    yield
    driver.quit()
    if driver.session_id is not None:
        driver.stop_client()


def pytest_addoption(parser):
    parser.addoption('-B', '--browser', action='store', default="Chrome",
                     help=f"Select From the given List' :('Chrome', 'Firefox', 'Edge', 'Safari')")

    parser.addoption('--repeat', default=None, type=int, action='store', help='Number of times to repeat each test')


@pytest.fixture(scope='class', autouse=True)
def allure_env(request):
    ALLURE_ENVIRONMENT_PROPERTIES_FILE = 'Environment.properties'
    ALLUREDIR_OPTION = '--alluredir'
    logs = _get_config_logs()
    platformName = None
    yield
    if '_blockchain' not in request.node.name:
        try:
            load_json = open(os.path.join(os.getcwd(), 'caps.json'))
            driver_caps = json.load(load_json)
            platformName = driver_caps['platformName']
        except Exception as e:
            logs.warning(e)
    else:
        platformName = None
    conf = request.config.getoption(ALLUREDIR_OPTION)

    env = {
        'Operating.System': platformName,
        'Environment': 'Staging',
        'Application': 'Shuttle-Wallet-Web',
        'App.Path': ReadConfig().end_url()
    }
    with open(os.path.join(conf, ALLURE_ENVIRONMENT_PROPERTIES_FILE), 'w') as write:
        for key in env.keys():
            data = f'{key}={env.get(key)}\n'
            write.write(data)
    shutil.copy(os.path.join(os.getcwd(), 'categories.json'), conf)

    executor = {
        "name": ReadConfig().executors()['name'],
        'buildUrl': ReadConfig().executors()['buildurl'],
        'buildName': ReadConfig().executors()['buildname'],
        "reportName": "Shuttle-Wallet-Web"
    }
    create_json(os.path.join(conf, 'executor.json'), executor)


def _get_config_logs() -> Logger:
    logger_name = inspect.stack()[1][3]
    log = logging.getLogger(logger_name)
    file_path = os.path.join(OUTPUT_DIR, 'Logs')
    logfile = logging.FileHandler(filename=f'{file_path}/conf_logs_{date.today()}.log')
    log_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(filename)s:%(lineno)s %(message)s")
    logfile.setFormatter(log_formatter)
    log.addHandler(logfile)
    log.setLevel(logging.INFO)
    return log


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item):
    logs = _get_config_logs()
    outcome = yield
    report = outcome.get_result()
    logs.info(report.nodeid)
    if '_blockchain' in report.nodeid or '_api' in report.nodeid:
        pass
    else:
        if report.when == 'call' or report.when == "setup" or report.when == 'teardown':
            xfail = hasattr(report, 'wasxfail')
            if (report.skipped and xfail) or (report.failed and not xfail):
                item.stash.setdefault(phase_report_key, {})[report.when] = report
                file_name = time.strftime("%m_%d_%H%M_%S") + "_" + report.nodeid.split('::')[2] + ".png"
                logs.info(file_name)
                _capture_screenshot(file_name)


def pytest_generate_tests(metafunc):
    # Add --repeat cmd arg at the time of Executing test to execute one test case multiple times
    # eg: pytest -vs -rA --repeat 3 test_login.py -k one where test Case name is test_one()
    logs = _get_config_logs()
    if metafunc.config.option.repeat is not None:
        count = int(metafunc.config.option.repeat)
        logs.info(metafunc.config.option.repeat)

        if 'invocationCount' not in metafunc.fixturenames:
            metafunc.fixturenames.append('invocationCount')
            logs.info(metafunc.fixturenames)

            metafunc.parametrize('invocationCount', range(count))


@pytest.fixture(scope='class', autouse=True)
def screen_recording(request):
    global video_name, mp4
    recorder = pyscreenrec.ScreenRecorder()
    test_name = request.node.name
    logs = _get_config_logs()
    if '_api' in test_name or '_blockchain' in test_name:
        logs.info(f'This is API Test Case:: {test_name}')
        yield None
    else:
        logs.info(f'===== Screen Recording Test_Name::{test_name} =====')
        filepath = os.path.join(OUTPUT_DIR, 'Videos')
        if '[' or ']' in test_name:
            video_name = f'{time.strftime("%m_%d_%H%M_%S")}_{test_name.split("[")[0]}'
            mp4 = os.path.join(filepath, f'{video_name}.mp4')
            recorder.start_recording(mp4)
            yield
            recorder.stop_recording()
            time.sleep(3)
            try:
                if os.path.exists(mp4):
                    webm = os.path.join(filepath, f'{video_name}.webm')

                    video_clip = VideoFileClip(mp4)
                    video_clip.write_videofile(webm, codec="libvpx")

                    # raw_mp4 = ffmpeg.input(mp4)
                    # raw_webm = ffmpeg.output(raw_mp4, webm)
                    # ffmpeg.run(raw_webm)
                    if os.path.exists(webm):
                        duration_clip = __get_vid_duration(webm)
                        logs.info(f'====== Duration of Clip ----- {duration_clip}')
                        if duration_clip >= 1.00:
                            with open(webm, 'rb') as vd_read:
                                allure.attach(vd_read.read(), name=test_name,
                                              attachment_type=allure.attachment_type.WEBM)
            except Exception as err:
                logs.error(err)


def __get_vid_duration(filename) -> Any | None:
    logs = _get_config_logs()
    try:
        clip = VideoFileClip(filename)
        if clip.duration is not None:
            return clip.duration
    except (AttributeError, Exception) as err:
        logs.error(f'Video Clip has no Start Point: --- {err}')
    return None


def create_json(filename, data):
    PROJECT_PATH = os.path.join(os.getcwd(), filename)
    if os.path.exists(PROJECT_PATH):
        save_file = open(os.path.join(PROJECT_PATH), "w")
    else:
        save_file = open(os.path.join(PROJECT_PATH), "x")
    json.dump(data, save_file, indent=6)
    save_file.close()


def _capture_screenshot(name):
    IMAGES_DIR_PATH = os.path.join(OUTPUT_DIR, "Images", name)
    _get_config_logs().info(f'_Capture_screenShot:::{IMAGES_DIR_PATH}')
    try:
        driver.get_screenshot_as_file(IMAGES_DIR_PATH)
        allure.attach(driver.get_screenshot_as_png(), name=name, attachment_type=allure.attachment_type.PNG)
    except Exception as e:
        _get_config_logs().exception('Fail to take screen-shot: {}'.format(e))
