import requests
import datetime
import cloudscraper
import pandas as pd
from lxml import html
from functools import wraps
from socket import timeout
from src.common.logs import *
from requests.exceptions import RequestException

thetan = []


class ListsInit(object):
    def __init__(self):
        super(ListsInit, self).__init__()

    @staticmethod
    def thetan_output(data):
        thetan.append(data)


class Retry(object):
    def __init__(self, times, exceptions, pause=1, retreat=1,
                 max_pause=None, cleanup=None):
        self.times = times
        self.exceptions = exceptions
        self.pause = pause
        self.retreat = retreat
        self.max_pause = max_pause or (pause * retreat ** times)
        self.cleanup = cleanup

    def __call__(self, func):

        @wraps(func)
        def wrapped_func(*args):
            for i in range(self.times):
                pause = min(self.pause * self.retreat ** i, self.max_pause)
                try:
                    return func(*args)
                except self.exceptions:
                    if self.pause is not None:
                        time.sleep(pause)
                    else:
                        pass
            if self.cleanup is not None:
                return self.cleanup(*args)

        return wrapped_func


class Common(ListsInit):
    def __init__(self):
        super(Common, self).__init__()
        # self.mail, self.password = self.__read_password_login_from_config()
        self.headers = ''
        self.session = requests.Session()
        self.previous_request_time = 0
        self.delay = 3

    def failed_call(*args):
        print(f"Failed call link {args[1]}")

    retry = Retry(times=5, pause=1, retreat=2, cleanup=failed_call,
                  exceptions=(RequestException, timeout))

    @staticmethod
    def writer():
        dfs = {
            'Thetan Arena Marketplace': pd.DataFrame(thetan),
        }
        now = datetime.now().strftime('%Y-%m-%d')
        writer = pd.ExcelWriter(f"output/thetan-mp-output-{now}.xlsx", engine='xlsxwriter')
        for sheet_name, df in dfs.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            # wb = writer.book
            # worksheet = writer.sheets[sheet_name]
            #
            # text_format = wb.add_format({'text_wrap': True, 'valign': 'top'})
            #
            # for idx, col in enumerate(df):
            #     series = df[col]
            #     max_len = max((series.astype(str).map(len).max(),
            #                    len(str(series.name)))) + 1
            #     if max_len > 100:
            #         worksheet.set_column(idx, idx, max_len / 5, text_format)
            #     else:
            #         worksheet.set_column(idx, idx, max_len, text_format)
        writer.save()
        # glassdoor.clear()

    @staticmethod
    def clean_df(list_of_dicts):
        df = pd.DataFrame(list_of_dicts).apply(lambda x: pd.Series(x.dropna().values))
        return df

    @staticmethod
    def clean_data(data):
        clean = [x.strip().replace('\n', '').replace('  ', '') for x in data]
        clean = list(filter(None, clean))
        clean = ', '.join(clean)
        return clean

    def extract(self, source, xpath, data, key):
        target = html.fromstring(source).xpath(xpath)
        target = self.clean_data(target)
        # if '$' in target:
        #     target = target.replace('$', '').replace('(', '')
        #     target = f'{target} $'
        data[key] = target
        return target

    @staticmethod
    def string_strip(raw_element, to_replace=[]):
        clean_string = raw_element
        for repl in to_replace:
            clean_string = clean_string.strip().replace(repl, '')
        return clean_string

    @staticmethod
    def iter_elem_xpath_string(elements, data, title=''):
        for idx, x in enumerate(elements):
            element = x.xpath('string()').strip().replace('\n', '').replace('\r', '')
            data[f'{title} {idx + 1}'] = element

    @retry
    def get_response(self, url):
        s = cloudscraper.create_scraper()
        r = s.get(url)
        r.encoding = 'UTF-8'

        if r.status_code != 200:
            print(f'{r.status_code} |{url}')
            r.raise_for_status()

        return r

    @staticmethod
    def raise_for_status(r):
        if r.status_code != 200:
            r.raise_for_status()

    @staticmethod
    def write_into_file(path: str, elements: list):
        with open(path, 'a') as f:
            for el in elements:
                f.write(f'{el}\n')

    @staticmethod
    def load_from_file(path: str):
        with open(path, 'r') as f:
            elements = f.readlines()
            elements = [x.replace('\n', '') for x in elements]
        return elements

    @staticmethod
    def timestamp_to_date(timestamp):
        try:
            date = datetime.fromtimestamp(timestamp)
        except:
            return ''
        return date

    @staticmethod
    def open_yaml(path) -> dict:
        with open(path, 'r') as file:
            file = yaml.load(file, Loader=yaml.FullLoader)
        return file

    @staticmethod
    def isfloat(value):
        try:
            float(value)
            return True
        except ValueError:
            return False
