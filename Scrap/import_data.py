import os
import requests
import numpy as np
import seaborn as sns
import pandas as pd
from matplotlib import rcParams
from matplotlib import pyplot as plt
from nilearn import plotting
from nimare import utils


def download(fname, url):
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


def load(fname):
	data = np.load(fname, allow_pickle=True)['dat']
	return data

def time_lock(data, before, after):
	nt, nchan = V.shape
	nstim = len(dat['t_on'])

	# use a timerange from 400ms before to 1600ms after the stimulus onset
	trange = np.arange(-400, 1600)
	ts = dat['t_on'][:,np.newaxis] + trange
	V_epochs = np.reshape(V[ts, :], (nstim, 2000, nchan))
	return aligned

def main():
	fname = 'memory_nback.npz'
	url = "https://osf.io/xfc7e/download"

	download(fname, url)
	data = load(fname)
	exit(0)

if __name__ == "__main__":
	main()