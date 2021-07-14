# DataWrapper class to make our lives easier

import os
import io
import requests
import numpy
import pandas

class DataWrapper:
    data = []

    def __init__(self, url: str = None, fname: str = None, data = None):

        if url is not None and fname is not None:
            if not os.path.isfile(fname):
                print("Loading file...")
                try:
                    r = requests.get(url)
                except requests.ConnectionError:
                    print("!!! Failed to download data !!!")
                else:
                    if r.status_code != requests.codes.ok:
                        print("!!! Failed to download data !!!")
                    else:
                        with open(fname, "wb") as fid:
                            fid.write(r.content)
            self.data = numpy.load(fname, allow_pickle=True)['dat']

        elif url is not None:
            try:
                r = requests.get(url)
            except requests.ConnectionError:
                print("!!! Failed to download data !!!")
            else:
                if r.status_code != requests.codes.ok:
                    print("!!! Failed to download data !!!")
                else:
                    self.data = numpy.load(io.BytesIO(r.content), allow_pickle=True)['dat']


        elif data is not None:
            self.data = data
        else:
            pass


    def getTrial(self, subject, trial):
        return self.data[subject][trial]

    def getTrialDataFrame(self, subject, trial):
        raw = self.data[subject][trial]

        dataframe = pandas.DataFrame(data=None, columns=['Time', 'Channel', 'Voltage', 'Stimulus On', 'Stimulus Off', 'Response', 'Expected'])

        for channel in range(len(raw['V'][0])):
            cframe = pandas.DataFrame()
            cframe.insert(0, "Time", pandas.to_datetime(numpy.arange(0, len(raw['V'])), unit='ms', origin=0))
            cframe.insert(1, "Channel", channel*numpy.ones(len(raw['V'])))
            cframe.insert(2, "Voltage", raw['V'][:, channel], allow_duplicates=True)
            cframe.insert(3, "Stimulus On", numpy.zeros(len(raw['V'])), allow_duplicates=True)
            cframe.insert(4, "Stimulus Off", numpy.zeros(len(raw['V'])), allow_duplicates=True)
            cframe.insert(5, "Response", numpy.zeros(len(raw['V'])), allow_duplicates=True)
            cframe.insert(6, "Expected", numpy.zeros(len(raw['V'])), allow_duplicates=True)
            cframe.at[raw['t_on'], "Stimulus On"] = True
            cframe.at[raw['t_off'], "Stimulus Off"] = True
            #cframe.at[raw['t_on'], "Response"] = raw['response'] == 1
            #cframe.at[raw['t_on'], "Expected"] = raw['target'] == 1
            dataframe = dataframe.append(cframe, ignore_index=True)

        return dataframe

