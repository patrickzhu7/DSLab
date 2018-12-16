from pprint import pprint
import json
import os
import requests
import sys
from shutil import copyfile
import multiprocessing

from mtgsdk import Card, Set

SCRYFALL_SETS = "https://api.scryfall.com/sets/"

def get_set_mIds(mtg_set):
	set_cards_mIds = set()

	res = requests.get(SCRYFALL_SETS + mtg_set).json()
	set_uri = res['search_uri']
	set_res = requests.get(set_uri)

	while True:
		set_data = set_res.json()['data']
		for card in set_data:
			multiverse_ids = card['multiverse_ids']
			for id in multiverse_ids:
				set_cards_mIds.add(id)
		
		if set_res.json()['has_more']:
			set_res = requests.get(set_res.json()['next_page'])
		else: break
	
	return set_cards_mIds


def parse_json(deck_json):
	with open(deck_json, 'r') as jsonfile:
		deck = json.load(jsonfile)
	
	return deck

def filter_deck(set_mIds, deck_json, out_json):
	try:
		deck = parse_json(deck_json)['mainboard']
		for card in deck:
			if int(card) in set_mIds:
				continue
			else:
				return 

		copyfile(deck_json, out_json)
	except:
		print("Filter error")

def main():
	set_mIds = get_set_mIds(sys.argv[1])
	pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
	for file in os.listdir(sys.argv[2]):
		if file.endswith(".json"):
			pool.apply_async(
				filter_deck,
				args=(set_mIds, sys.argv[2]+"/"+file, sys.argv[3]+"/"+file, )
			)
	
	pool.close()
	pool.join()

if __name__ == "__main__":
	main()