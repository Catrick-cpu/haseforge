# haseforge/forge.py

import math as m
import time

from .gpio import init_gpio, step_motor
from .kinematics import calc_angles
from .logger import log, banner
from .server import create_server


class HaseForge:
    def __init__(self):

        # STATUS (komplett übernommen)
        self.status = {
            "theta1": 0.0,
            "theta2": 0.0,
            "rot": 0.0,
            "counter_m1": 0,
            "counter_m2": 0,
            "counter_m3": 0,
            "steps_m1_total": 0,
            "steps_m2_total": 0,
            "steps_m3_total": 0,
            "x": 100,
            "z": 300,
        }

        # HARDWARE CONFIG
        self.M1_STEP, self.M1_DIR = 17, 27
        self.M2_STEP, self.M2_DIR = 22, 23
        self.M3_STEP, self.M3_DIR = 5, 6

        self.L1, self.L2 = 500, 525
        self.STEPS_PER_ROUND = 200

        self.gpio_error = 1
        self.log_buffer = []

    # 🚀 INIT SYSTEM
    def init(self):
        banner("HASEFORGE ROBOT ARM")
        self.gpio_error = init_gpio()
        log("HaseForge ready 🔧")

    # 📜 LOGGING
    def log(self, msg):
        log(msg)
        self.log_buffer.append(msg)
        if len(self.log_buffer) > 100:
            self.log_buffer.pop(0)

    # 🧠 IK
    def calc_angles(self, x, z):
        return calc_angles(x, z, self.L1, self.L2)

    # ⚙️ STEP MOTOR
    def step(self, step_pin, dir_pin, direction):
        step_motor(step_pin, dir_pin, direction, self.gpio_error)

    # 🎯 EASING (original behalten)
    def ease_in_out(self, t):
        return 0.5 - 0.5 * m.cos(m.pi * t)

    # 🌐 SERVER START

    def run(self):
        app = create_server(self)
        app.run(host="0.0.0.0", port=5050)