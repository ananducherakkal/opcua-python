import random
from mqtt_connector import opcuaVars

def trigger (name):
    if name in opcuaVars:
        random_value = random.randint(1, 10)
        opcuaVars[name].write_value(random_value)