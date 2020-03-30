import configparser

BASE_SERVER = 'BASE_SERVER'


def read_config(config_file_abs_path):
    parser = configparser.ConfigParser()
    parser.read(config_file_abs_path)
    return parser
