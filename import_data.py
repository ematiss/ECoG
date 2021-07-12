import os
import requests
import numpy as np
import seaborn as sns
import pandas as pd
from matplotlib import rcParams
from matplotlib import pyplot as plt
from nilearn import plotting
from nimare import utils


def download():
	fname = 'memory_nback.npz'
	url = "https://osf.io/xfc7e/download"

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


def main():
	download()
	exit(0)

if __name__ == "__main__":
	main()