#!/usr/bin/env python3
from pytradfri import Gateway
from pytradfri.api.libcoap_api import APIFactory
from pytradfri.error import PytradfriError
from pytradfri.util import load_json, save_json

import uuid
import argparse
import threading
import time

def init(CONFIG_FILE):
  parser = argparse.ArgumentParser()
  parser.add_argument(
    "host", metavar="IP", type=str, help="IP Address of your Tradfri gateway"
  )
  parser.add_argument(
    "-K",
    "--key",
    dest="key",
    required=False,
    help="Security code found on your Tradfri gateway",
  )
  args = parser.parse_args()

  if args.host not in load_json(CONFIG_FILE) and args.key is None:
    print(
      "Please provide the 'Security Code' on the back of your " "Tradfri gateway:",
      end=" ",
    )
    key = input().strip()
    if len(key) != 16:
      raise PytradfriError("Invalid 'Security Code' provided.")
    else:
      args.key = key

  conf = load_json(CONFIG_FILE)

  try:
    identity = conf[args.host].get("identity")
    psk = conf[args.host].get("key")
    api_factory = APIFactory(host=args.host, psk_id=identity, psk=psk)
  except KeyError:
    identity = uuid.uuid4().hex
    api_factory = APIFactory(host=args.host, psk_id=identity)

    try:
      psk = api_factory.generate_psk(args.key)
      print("Generated PSK: ", psk)

      conf[args.host] = {"identity": identity, "key": psk}
      save_json(CONFIG_FILE, conf)
    except AttributeError:
      raise PytradfriError(
        "Please provide the 'Security Code' on the "
        "back of your Tradfri gateway using the "
        "-K flag."
      )

  api = api_factory.request
  return api

def observe(api, device):
  def callback(updated_device):
    light = updated_device.light_control.lights[0]
    print("Received message for: %s" % light)

  def err_callback(err):
    print(err)

  def worker():
    api(device.observe(callback, err_callback, duration=300))

  threading.Thread(target=worker, daemon=True).start()
  print("Sleeping to start observation task")
  time.sleep(1)

def get_light_by_name(lights, name):
  for i,l in enumerate(lights):
    if l.name == name:
      return lights[i]
  return None

def get_hex_from_color(color):
  colors = {
    "4a418a": "Blue",
    "6c83ba": "Light Blue",
    "8f2686": "Saturated Purple",
    "a9d62b": "Lime",
    "c984bb": "Light Purple",
    "d6e44b": "Yellow",
    "d9337c": "Saturated Pink",
    "da5d41": "Dark Peach",
    "dc4b31": "Saturated Red",
    "dcf0f8": "Cold sky",
    "e491af": "Pink",
    "e57345": "Peach",
    "e78834": "Warm Amber",
    "e8bedd": "Light Pink",
    "eaf6fb": "Cool daylight",
    "ebb63e": "Candlelight",
    "efd275": "Warm glow",
    "f1e0b5": "Warm white",
    "f2eccf": "Sunrise",
    "f5faf6": "Cool white"
  }
  for i in colors:
    if colors[i] == color:
      return i