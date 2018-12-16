import os
import sys
from shutil import copyfile

USER_DECK_DIR = sys.argv[1] + "/"
ALL_DECKS_DIR = sys.argv[2] + "/"

def copy_matching_draft_decks(deck_file):
	draft_id = deck_file.split('_', 1)[0]
	for file in os.listdir(ALL_DECKS_DIR):
		if file.endswith(".json") and "bot" in file and draft_id in file:
			try:
				copyfile(ALL_DECKS_DIR+file, USER_DECK_DIR+file)
			except:
				print("Copy failed")

def main():
	for file in os.listdir(USER_DECK_DIR):
		if file.endswith(".json") and "consolidated" not in file:
			copy_matching_draft_decks(file)

if __name__ == "__main__":
	main()