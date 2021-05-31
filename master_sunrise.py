#!/usr/bin/python3
from pytradfri import Gateway
import modules.functions as functions
from pprint import pprint

import time

CONFIG_FILE = "tradfri_standalone_psk.conf"
LIGHT_NAME = "Master bedroom"
LIGHT_COLOR = "Sunrise"
TRANSITION_TIME_MIN = 15
TRANSITION_DIMMER_PERCENT = 50
api = functions.init(CONFIG_FILE=CONFIG_FILE)

def run():
  gateway = Gateway()
  devices_command = gateway.get_devices()
  devices_commands = api(devices_command)
  devices = api(devices_commands)

  print(devices)

  def dump_devices():
    pprint([d.name for d in devices])

  dump_devices()

  lights = [dev for dev in devices if dev.has_light_control]

  light = None
  if lights:
    light = functions.get_light_by_name(lights=lights, name=LIGHT_NAME)
  else:
    print("No lights found!")

  if light:
    functions.observe(api=api, device=light)

    # Set dimmer to 0 (reinitialize)
    dim_command = light.light_control.set_dimmer(0)
    api(dim_command)
    time.sleep(.5)

    # Set color to "Sunrise"
    hex_color = functions.get_hex_from_color(LIGHT_COLOR)
    color_command = light.light_control.set_hex_color(hex_color)
    api(color_command)
    time.sleep(.5)

    dim_command = light.light_control.set_state(1)
    api(dim_command)
    time.sleep(.5)

    dimmer_value = int(TRANSITION_DIMMER_PERCENT*2.54)
    transition_min_value = TRANSITION_TIME_MIN*600
    dim_command = light.light_control.set_dimmer(dimmer_value, transition_time=transition_min_value)
    api(dim_command)

    print("Sleeping for {} seconds".format(TRANSITION_TIME_MIN*60))
    time.sleep(TRANSITION_TIME_MIN*60)
    print("Transition done!")

if __name__ == "__main__":
  run()
