# DataWrapper class to make our lives easier

import os
import io
import requests
import numpy
import pandas
import mne

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

        elif fname is not None:
            self.data = numpy.load(fname, allow_pickle=True)['dat']

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

    def getMNE(self, subject, trial):
        raw = self.data[subject][trial]
        data = numpy.swapaxes(raw['V'], 0, 1)
        info = mne.create_info(data.shape[0], 1000)
        m = mne.io.RawArray(data, info)
        return m

    def getEvents(self, subject, trial, before=-400, after=1600):
        raw = self.data[subject][trial]
        V = raw['V']
        nt, nchan = V.shape
        nstim = len(raw['t_on'])

        trange = numpy.arange(before, after)
        ts = raw['t_on'][:,numpy.newaxis] + trange
        events = numpy.reshape(V[ts, :], (nstim, after - before, nchan))
        
        on = raw['t_on']
        response = raw['response']
        expected = raw['target']
        rt = raw['rt']

        return events, on, response, expected, rt


    def getEpochs(self, subject, trial, before=-400, after=1600):
        event_id = dict(wrong_response=0, correct_response=1)
        aligned, on, response, expected, rt = self.getEvents(self, subject, trial, before, after)
        data = numpy.swapaxes(aligned, 1, 2)
        info = mne.create_info(data.shape[1], 1000)

        # events = np.zeros((len(data), 3), dtype=int)
        # events[0] = np.arange(len(data))
        # events[1] = after-before
        # events[2] = response == expected

        events = numpy.vstack((numpy.arange(len(data)), numpy.ones(len(data))*(after-before), response == expected)).astype(int)

        #events = np.sort(events, axis=0)
        epochs = mne.EpochsArray(data=data, info=info, event_id=event_id, events=events)

        return epochs

        

