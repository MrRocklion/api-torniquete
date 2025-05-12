import os
import time
import threading
import logging
from dotenv import load_dotenv
from audioManager import AudioManager

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment and select GPIO manager
load_dotenv()
ENVIRONMENT = os.getenv("ENVIRONMENT", "RASPBERRY")
logger.info("Environment: %s", ENVIRONMENT)

if ENVIRONMENT == "RASPBERRY":
    from gpiosManagerRaspberry import GpiosManager
else:
    from gpiosManagerLocal import GpiosManager


doors = GpiosManager()
def rotate_turnstile(direction: str):
    if direction == "left":
        doors.left_lock_open()
    elif direction == "right":
        doors.rigth_lock_open()
    else:
        logger.error("Invalid direction for rotation: %s", direction)
        return

    start_time = time.time()
    max_duration = 7

    while time.time() - start_time < max_duration:
        if doors.read_sensor():
            while doors.read_sensor():
                if time.time() - start_time >= max_duration:
                    break
            break

    if direction == "left":
        doors.left_lock_close()
    elif direction == "right":
        doors.rigth_lock_close()

def release_tripod_arm():
    doors.special_door_open()
    time.sleep(1)
    doors.special_door_close()

class TurnstileManager(threading.Thread, GpiosManager):
    def __init__(self, rs232, stop_event, mode):
        super().__init__()
        self.rs232 = rs232
        self.stop_event = stop_event
        self.mode = mode
        self.special_pass = 0
        self.left_pass = 0
        self.right_pass = 0

    def run(self):
        while not self.stop_event.is_set():
            with self.rs232.lock:
                if self.left_pass > 0:
                    self._handle_direction_pass('left')
                elif self.right_pass > 0:
                    self._handle_direction_pass('right')
                elif self.special_pass > 0:
                    self._handle_special_pass()
                elif self.rs232.validation:
                    self._handle_rs232_pass()
            time.sleep(0.1)

    def _handle_direction_pass(self, direction):
        thread = threading.Thread(target=rotate_turnstile, args=(direction,))
        thread.start()
        thread.join()
        if direction == 'left':
            self.left_pass = max(0, self.left_pass - 1)
        elif direction == 'right':
            self.right_pass = max(0, self.right_pass - 1)

    def _handle_special_pass(self):
        thread = threading.Thread(target=release_tripod_arm)
        thread.start()
        thread.join()
        self.special_pass = max(0, self.special_pass - 1)

    def _handle_rs232_pass(self):
        if self.rs232.data[18] != '3':
            self._handle_direction_pass(self.mode)
        else:
            threading.Thread(target=release_tripod_arm).start()

    # Public API
    def generate_left_pass(self):
        self.left_pass += 1

    def generate_right_pass(self):
        self.right_pass += 1

    def generate_special_pass(self):
        self.special_pass += 1
        return "Special pass granted successfully"

    def read_sensor(self):
        return doors.read_sensor()

    def test_all_locks(self):
        doors.test_all_locks()

    def test_arrow_indicators(self):
        doors.test_arrow()

    def open_special_door(self):
        doors.unlock_special_arm()
        return {"msg": "Special door opened", "status": True}

    def close_special_door(self):
        doors.lock_special_arm()
        return {"msg": "Special door closed", "status": True}
