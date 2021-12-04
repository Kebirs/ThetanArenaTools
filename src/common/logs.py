from datetime import datetime
from datetime import timedelta
import string
import random
import numpy as np
import os
import yaml
import functools
import time


class LogsConfigurationTemplate(object):
    def __init__(self):
        super(LogsConfigurationTemplate, self).__init__()

    @staticmethod
    def get_template():
        basic_sample_configuration = {
            'allow_logging': True,
            'allow_logging_debug': True,
            'print_logging': True,
            'print_logging_debug': True,
            'folder_name': 'logs',
            'log_life_time': 7,
            'log_file_name': 'log_{}.log'
        }
        return basic_sample_configuration


class MineErrorException(Exception):
    pass


class CodeLogsGenerator(object):
    def __init__(self):
        __letter = string.ascii_uppercase
        self.code = ''.join([__letter[random.randrange(len(__letter))] for x in range(6)])


code = CodeLogsGenerator().code


class Logs(object):
    def __init__(self, read_only=True):
        super(Logs, self).__init__()
        self._read_only_log_mode = read_only
        self._config_path = r'configuration/logs_configuration.yaml'
        self._config = self._manage_configuration()

    def log_it(self, msg, t_msg='i', sub_folder_name=''):
        self._logs_work_flow(msg, t_msg, sub_folder_name)

    def _logs_work_flow(self, msg, msg_type, sub_folder_name):
        logs_path = ''
        if not self._read_only_log_mode:
            logs_path = self._find_logs_file(sub_folder_name)
            self._remove_older_logs(logs_path)

        self._log_it(msg, msg_type, logs_path)
        pass

    @staticmethod
    def _find_logs_file(sub_folder_name):
        now = datetime.now().strftime('%Y-%m-%d')
        logs_name = f'log_{now}.log'

        logs_path = os.path.join(os.getcwd(), 'logs', sub_folder_name, logs_name)

        os.makedirs(os.path.join(os.path.abspath(os.path.dirname(logs_path))), exist_ok=True)
        # self.__create_path_to_file(logs_path)
        return logs_path

    def _log_it(self, msg, t_msg, path):
        scheme = '|{}\t|{}\n'
        t_msg = t_msg.lower()
        if t_msg.lower() == 'i':
            scheme = scheme.format('INFO', msg)

        elif t_msg.lower() == 'd':
            scheme = scheme.format('DEBUG', msg)

        elif t_msg.lower() == 'w':
            scheme = scheme.format('WARNING', msg)

        elif t_msg.lower() == 'c':
            scheme = scheme.format('CRITICAL', msg)

        elif t_msg.lower() == 'e':
            scheme = scheme.format('ERROR', msg)

        elif t_msg.lower() == '_':
            scheme = f'\n{msg}\n'

        self._custom_log(scheme, path, t_msg)

    def _custom_log(self, msg, path, t_msg):
        msg = f'{datetime.now()} | {code} {msg}'
        if t_msg == 'i' and self._config.get('allow_logging') or t_msg == 'd' and self._config.get(
                'allow_logging_debug'):

            if not self._read_only_log_mode:
                with open(path, 'a', encoding='UTF-8') as file:
                    file.write(msg)

        if t_msg == 'i' and self._config.get('print_logging'):
            print(msg)
        elif t_msg == 'd' and self._config.get('print_logging_debug'):
            print(msg)

    def _remove_older_logs(self, logs_path):
        days = self._config.get('log_life_time')
        path_to_logs = os.path.split(logs_path)[0]
        for file in os.listdir(path_to_logs):
            if 'log_' in file:
                date = file.replace('log_', '')
                date = os.path.splitext(date)[0]
                date_time = datetime.strptime(date, '%Y-%m-%d')
                if np.inf == days:
                    continue
                if date_time < datetime.today() - timedelta(days=days):
                    os.remove(path_to_logs + '/' + file)

    def _manage_configuration(self):
        if self._read_only_log_mode:
            template_config = LogsConfigurationTemplate().get_template()
            return template_config
        else:
            if not os.path.isfile(self._config_path):
                os.makedirs(os.path.join(os.path.abspath(os.path.dirname(self._config_path))), exist_ok=True)
                return self._create_configuration_file()
            else:
                template_config = LogsConfigurationTemplate().get_template()
                config = self._read_configuration_file()

                template_config.update(config)
                with open(self._config_path, 'w') as file:
                    data = yaml.dump(template_config, file)
                return template_config

    def _create_configuration_file(self):
        basic_sample_configuration = LogsConfigurationTemplate().get_template()
        # self.__create_path_to_file(self.__config_path)
        with open(self._config_path, 'a') as file:
            data = yaml.dump(basic_sample_configuration, file)
        return basic_sample_configuration

    def _read_configuration_file(self):
        with open(self._config_path, 'r', encoding='UTF-8') as file:
            configuration = yaml.load(file, Loader=yaml.FullLoader)

        return configuration


def debug_log(func):
    log = Logs()
    _name = func.__name__

    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        tic = time.perf_counter()
        _msg = f'Function: {_name}'
        log.log_it(_msg, 'd')
        # value = func(*args, **kwargs)

        try:
            value = func(*args, **kwargs)
        except Exception as e:
            log.log_it(str(e), 'c')
            raise MineErrorException(e, code)

        toc = time.perf_counter()
        elapsed_time = toc - tic
        _msg = f'Function: {str(func)} Elapsed time: {elapsed_time:0.4f} seconds'

        # Remove here
        log.log_it(_msg, 'd')
        return value

    return wrapper_timer


if __name__ == '__main__':
    l_ob = Logs()
    l_ob.log_it('Sample_message', t_msg='i')
