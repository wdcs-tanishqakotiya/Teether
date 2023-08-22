import configparser
import os.path


class ReadConfig:
    cwd = os.getcwd()
    parent_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
    config = configparser.RawConfigParser()

    file_path = os.path.join(parent_path, 'Config', 'config.ini')
    if os.path.exists(file_path):
        config.read(file_path)

    def end_url(self):
        for sec in self.config.sections():
            if sec == 'environment.stagging':
                URL = self.config.get('environment.stagging', 'end_url')
                return URL

    def executors(self):
        Dict = {}
        for sec in self.config.sections():
            if sec == 'executors':
                key_value_list = self.config.items(sec)
                for key, value in key_value_list:
                    Dict[key] = value
                return Dict
