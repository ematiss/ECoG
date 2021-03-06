# DataWrapper class to make our lives easier

import os
import io
from types import DynamicClassAttribute
import requests
import numpy
import pandas
import mne


class DataWrapper:
    """The DataWrapper class provides an easy to use abstraction for the data provided in the NMA ECoG dataset."""

    data = []

    def __init__(self, url: str = None, fname: str = None, data=None):
        """Constructor for wrapper.

        Args:
            url (str, optional): URL to dataset. Defaults to None.
            fname (str, optional): Filename if saving/loading locally. Defaults to None.
            data ([type], optional): Array of raw data. Defaults to None.
        """

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
            self.data = numpy.load(fname, allow_pickle=True)["dat"]

        elif url is not None:
            try:
                r = requests.get(url)
            except requests.ConnectionError:
                print("!!! Failed to download data !!!")
            else:
                if r.status_code != requests.codes.ok:
                    print("!!! Failed to download data !!!")
                else:
                    self.data = numpy.load(io.BytesIO(r.content), allow_pickle=True)[
                        "dat"
                    ]

        elif fname is not None:
            self.data = numpy.load(fname, allow_pickle=True)["dat"]

        elif data is not None:
            self.data = data
        else:
            pass

    def getTrial(self, subject, trial):
        """Return raw data for subject in a specific trial in the format provided by dataset.

        Args:
            subject (int): Subject index
            trial (int): Trial index

        Returns:
            ndarray: dataset for retrieved trial
        """
        return self.data[subject][trial]

    def getTrialDataFrame(self, subject, trial):
        """Return trial data for subject in a specific trial in a pandas dataframe.

        Args:
            subject (int): Subject index
            trial (int): Trial index

        Returns:
            dataframe: trial data in dataframe
        """
        raw = self.data[subject][trial]

        dataframe = pandas.DataFrame(
            data=None,
            columns=[
                "Time",
                "Channel",
                "Voltage",
                "Stimulus On",
                "Stimulus Off",
                "Response",
                "Expected",
            ],
        )

        for channel in range(len(raw["V"][0])):
            cframe = pandas.DataFrame()
            cframe.insert(
                0,
                "Time",
                pandas.to_datetime(numpy.arange(0, len(raw["V"])), unit="ms", origin=0),
            )
            cframe.insert(1, "Channel", channel * numpy.ones(len(raw["V"])))
            cframe.insert(2, "Voltage", raw["V"][:, channel], allow_duplicates=True)
            cframe.insert(
                3, "Stimulus On", numpy.zeros(len(raw["V"])), allow_duplicates=True
            )
            cframe.insert(
                4, "Stimulus Off", numpy.zeros(len(raw["V"])), allow_duplicates=True
            )
            cframe.insert(
                5, "Response", numpy.zeros(len(raw["V"])), allow_duplicates=True
            )
            cframe.insert(
                6, "Expected", numpy.zeros(len(raw["V"])), allow_duplicates=True
            )
            cframe.at[raw["t_on"], "Stimulus On"] = True
            cframe.at[raw["t_off"], "Stimulus Off"] = True
            # cframe.at[raw['t_on'], "Response"] = raw['response'] == 1
            # cframe.at[raw['t_on'], "Expected"] = raw['target'] == 1
            dataframe = dataframe.append(cframe, ignore_index=True)

        return dataframe

    def getMNE(self, subject, trial):
        """Return MNE object for trial.

        Args:
            subject (int): Subject index
            trial (int): Trial index

        Returns:
            MNEobj: MNE data object
        """
        raw = self.data[subject][trial]
        data = numpy.swapaxes(raw["V"], 0, 1)
        info = mne.create_info(data.shape[0], 1000)
        m = mne.io.RawArray(data, info)
        return m

    def getEvents(self, subject, trial, before=-400, after=1600):
        """Time lock the events in a trial.

        Args:
            subject (int): Subject index
            trial (int): Trial index
            before (int, optional): Milliseconds before event. Defaults to -400.
            after (int, optional): Milliseconds after event. Defaults to 1600.

        Returns:
            ndarray: Array in the shape [event][time][channel]
            ndarray: Array of event timestamps
            ndarray: Array of recorded responses
            ndarray: Array of expected responses
            ndarray: Array of reaction times. Offset from event timestamp.

        """
        raw = self.data[subject][trial]
        V = raw["V"]
        nt, nchan = V.shape
        nstim = len(raw["t_on"])

        trange = numpy.arange(before, after)
        ts = raw["t_on"][:, numpy.newaxis] + trange
        events = numpy.reshape(V[ts, :], (nstim, after - before, nchan))

        on = raw["t_on"]
        response = raw["response"]
        expected = raw["target"]
        rt = raw["rt"]

        return events, on, response, expected, rt

    def getEpochs(self, subject: int, trial: int, before=-400, after=1600):
        """Return MNE Epoch data for trial.

        Args:
            subject (int): Subject index
            trial (int): Trial index
            before (int, optional): Event offset before response. Defaults to -400.
            after (int, optional): Event offset after response. Defaults to 1600.

        Returns:
            EpochsArray: MNE EpochsArray for specific trial.
        """
        event_id = dict(wrong_response=0, correct_response=1)
        aligned, on, response, expected, rt = self.getEvents(
            subject=subject, trial=trial, before=before, after=after
        )
        data = numpy.swapaxes(aligned, 1, 2)
        info = mne.create_info(data.shape[1], 1000)

        events = numpy.column_stack(
            (
                numpy.arange(len(data), dtype=int),
                numpy.ones(len(data), dtype=int) * (after - before),
                (response == expected).astype(int),
            )
        )

        # events = np.sort(events, axis=0)
        epochs = mne.EpochsArray(data=data, info=info, event_id=event_id, events=events)

        return epochs
