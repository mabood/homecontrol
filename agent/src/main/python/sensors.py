import logging
import constants


class SensorManager(object):
    def __init__(self, sensors_config):
        self.hasThermometer = eval(sensors_config[constants.AGENT_CONFIG_KEY_THERMOMETER])
        if self.hasThermometer:
            logging.info('Sensor \'%s\' is enabled.' % constants.AGENT_CONFIG_KEY_THERMOMETER)
            self.thermometer_device_dir = sensors_config[constants.AGENT_CONFIG_KEY_THERMOMETER_DIR]
            self.thermometer_device_file = sensors_config[constants.AGENT_CONFIG_KEY_THERMOMETER_FILE]


