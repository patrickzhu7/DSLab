import json
import os
import sys
from threading import Thread, BoundedSemaphore
from shutil import copyfile

from mtgsdk import Card

MAX_THREADS = 8
DIR = "decks_by_set/"
thread_pool = BoundedSemaphore(MAX_THREADS)

def most_printings(mainboard):
	for card in mainboard:
		printings = Card.find(card).printings
		for printing in printings:
			print(printing)

def determine_set(file):
	mtg_set = "FUCK"

	deck = parse_json(sys.argv[1]+file)
	mb = deck['mainboard']

	for card in mb:
		printings = Card.find(card).printings
		if 1 == len(printings):
			mtg_set = printings[0]
			break
	
	print(mtg_set)
	return mtg_set

def parse_json(deck_file):
	with open(deck_file, 'r') as jsonfile:
		deck = json.load(jsonfile)

	return deck

def organize_by_set(file):
	thread_pool.acquire()

	try:
		mtg_set = determine_set(file)
		if not os.path.exists(DIR+mtg_set):
			os.makedirs(DIR+mtg_set)
		try:
			copyfile(sys.argv[1]+file, DIR+mtg_set+'/'+file)
		except:
			print("Copy failed")

	finally:
		thread_pool.release()

def main():
	for file in os.listdir(sys.argv[1]):
		if file.endswith('.json'):
			Thread(
				target=organize_by_set,
				args=(file, )
			).start()

if __name__ == "__main__":
	main()