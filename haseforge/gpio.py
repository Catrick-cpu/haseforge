# haseforge/gpio.py

import time

gpio_error = 1
GPIO = None


def init_gpio():
    global GPIO, gpio_error

    for i in range(1, 4):
        try:
            import RPi.GPIO as GPIO
            GPIO.setmode(GPIO.BCM)

            gpio_error = 0
            print("GPIO initialized")
            return gpio_error

        except ImportError:
            gpio_error = 1
            print("GPIO failed try", i)

    return gpio_error


def step_motor(STEP_PIN, DIR_PIN, direction, gpio_error):
    if gpio_error == 0:
        GPIO.output(DIR_PIN, GPIO.HIGH if direction else GPIO.LOW)
        GPIO.output(STEP_PIN, GPIO.HIGH)
        GPIO.output(STEP_PIN, GPIO.LOW)
    else:
        print(f"[SIM] Step {STEP_PIN} dir {direction}")