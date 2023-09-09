import os
import random
import time
from datetime import datetime

ENV = 'production'  # dev, production
BROWSER = 'chrome'
PARAMS = []
WORKSPACE = None
PROFILE_NAME = None
APP_PATH = None

SESSION_ID = str(int(time.time())) + str(random.randrange(10000, 99999))

KDB_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.join(KDB_DIR, os.pardir)

DATA_DIR = os.path.join(ROOT_DIR, 'data')
DATA_TEMP_DIR = os.path.join(DATA_DIR, 'temp', datetime.now().strftime("%Y-%m-%d"))
PROFILES_DIR = os.path.join(ROOT_DIR, 'profiles')

CONFIG_DIR = os.path.join(KDB_DIR, 'config')
REPORT_TEMPLATE_DIR = os.path.join(CONFIG_DIR, 'report_template')
DRIVER_DIR = os.path.join(KDB_DIR, 'drivers')
SCRIPT_DIR = os.path.join(KDB_DIR, 'scripts')
LOG_DIR = os.path.join(KDB_DIR, 'logs')

OUTPUT_DIR = os.path.join(ROOT_DIR, 'output')

XML_REPORT_DIR = os.path.join(OUTPUT_DIR, 'xml', SESSION_ID)
HTML_REPORT_DIR = os.path.join(OUTPUT_DIR, 'html', SESSION_ID)
DATA_REPORT_DIR = os.path.join(OUTPUT_DIR, 'data', SESSION_ID)
SCREENSHOTS_REPORT_DIR = os.path.join(HTML_REPORT_DIR, 'screenshots')

XML_REPORT_FILE = 'xml_report_main.xml'
APPIUM_LOCK_FILE = '~/.appium.lock'
BUILD_LOCK_FILE = 'build.lock'


def init_folder_config_structure(kdb_root_dir):
    #
    ROOT_DIR = kdb_root_dir

    DATA_DIR = os.path.join(ROOT_DIR, 'data')
    DATA_TEMP_DIR = os.path.join(DATA_DIR, 'temp', datetime.now().strftime("%Y-%m-%d"))
    PROFILES_DIR = os.path.join(ROOT_DIR, 'profiles')

    CONFIG_DIR = os.path.join(ROOT_DIR, 'config')
    REPORT_TEMPLATE_DIR = os.path.join(CONFIG_DIR, 'report_template')
    DRIVER_DIR = os.path.join(ROOT_DIR, 'drivers')
    SCRIPT_DIR = os.path.join(ROOT_DIR, 'scripts')
    LOG_DIR = os.path.join(ROOT_DIR, 'logs')

    OUTPUT_DIR = os.path.join(ROOT_DIR, 'output')

    XML_REPORT_DIR = os.path.join(OUTPUT_DIR, 'xml', SESSION_ID)
    HTML_REPORT_DIR = os.path.join(OUTPUT_DIR, 'html', SESSION_ID)
    DATA_REPORT_DIR = os.path.join(OUTPUT_DIR, 'data', SESSION_ID)
    SCREENSHOTS_REPORT_DIR = os.path.join(HTML_REPORT_DIR, 'screenshots')
