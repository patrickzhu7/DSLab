#!./venv/bin python

import json
import os
import sys
from pprint import pprint

OUT_FILE = "consolidated_decks.json"
DECKS_PATH = sys.argv[1] + "/"
OUTPUT_PATH = sys.argv[1]+ "/" + OUT_FILE


def combine_decks(in_dir):
	decks = list()
	for file in os.listdir(in_dir):
		if file.endswith(".json") and not OUT_FILE in file:
			with open (in_dir + file) as jsonfile:
				deck = json.load(jsonfile)['mainboard']
				total = 0
				for key, value in deck.items():
					total += value
				if 45 == total:
					decks.append(deck)

	return decks

def main():
	decks = {'decks': combine_decks(DECKS_PATH)}
	with open(OUTPUT_PATH, 'w') as jsonfile:
		json.dump(decks, jsonfile)

if __name__ == "__main__":
	main()
