# DataWrapper class to make our lives easier

class DataWrapper:
    data = []

    def getTrial(self, subject, trial)
        return self.data[subject][trial]

    def __init__(self):

    def __init__(self, data: ndarray):
        data = data.copy()

    def __init__(self, url: str, fname = 'data.npz):
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
        data = np.load(fname, allow_pickle=True)['dat']