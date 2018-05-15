import threading
import traceback

import sys

import digiroad.digiroadInit as digiroad
from digiroad.util import Logger


class CardatThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        print("Starting CAr Routing Data Analysis")
        try:
            digiroad.main()
        except Exception as err:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            Logger.getInstance().exception(''.join('>> ' + line for line in lines))
            raise err


cardatThread = CardatThread()
cardatThread.start()
