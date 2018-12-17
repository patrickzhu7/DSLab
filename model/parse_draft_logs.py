import json
import numpy as np
import pandas as pd
from os import listdir
from os.path import isfile, join
from multiprocessing import cpu_count, Manager, Pool

def add_draft_to_dataframe(df, draft_file, card_dict, start_index):
    """
    Add rows to dataframe with first 281 columns referring to the current deck, the next 281 columns 
    representing current board, and last column representing the card picked by its ID.
    
    output: DataFrame, note that DataFrame is not changed in place
    """
    count = 0
    current_deck = np.zeros(281)
    with open(draft_file, 'r') as f:
        if(f.readline() == '<h1>Server Error (500)</h1>'):
            print(draft_file)
            return df
        for i in range(10): # get rid of starting lines
            f.readline()
            
        for a in range(3): #do this 3 times (for each pack)
            for i in range(2): #get rid of "-- M19 --""
                f.readline()  
            for b in range(15, 0, -1):
                f.readline() # get rid of empty
                f.readline() # get rid of "Pack X pick X"
                current_board = np.zeros(281)
                current_y = np.zeros(1)
                for i in range(b):  
                    line = f.readline()
                    card_id = card_dict[line[4:].rstrip()]
                    
                    if(line[0:3] == "-->"):
                        current_y = card_id
                    
                    current_board[card_id - start_index] += 1
                row = pd.Series(np.concatenate([current_deck, current_board, current_y], axis=None))
                df = df.append(row, ignore_index=True)
                count += 1
                current_deck[current_y-start_index] += 1
    
    return df

def list_split(original_list, n_lists):
	avg = len(original_list) / float(n_lists)
	res = []
	last = 0.0

	while last < len(original_list):
		res.append(original_list[int(last):int(last+avg)])
		last += avg
	
	return res

def task(args):
	df = pd.DataFrame()
	for file in args[0]:
		df = add_draft_to_dataframe(df=df, draft_file='../M19_draft_logs/' + file, card_dict=args[1], start_index=args[2])
	
	return df

def main():
	# PREPROCESSING - KEEP THIS INTACT
	id_to_card = {} # map card ID to card name (may be unnecessary)
	card_to_id = {}
	card_map = [] # index to card ID for nparray 
	start_index = 0 # ID of first card - follows convention of TOP8Draft values
	with open('M19_M19_M19_cards.txt') as f:
			for line in f:
					split = line.split(';')
					
					card_id = int(split[1].rstrip())
					card_name = split[0]
					
					card_to_id[card_name] = card_id
					id_to_card[card_id] = card_name
					card_map.append(card_id)
					
			start_index = card_map[0]

	df_col = [str(card_id) + " in Deck" for card_id in card_map] \
						+ [str(card_id) \
						+ " in Pool" for card_id in card_map] \
						+ ["Y"]

	
	# Split into N lists where N is # of cores
	onlyfiles = [f for f in listdir('../M19_draft_logs/') if isfile(join('../M19_draft_logs/', f))]
	files_split = list_split(onlyfiles, cpu_count())

	# Use list of tuples to pass args around
	args_list = []
	for split in files_split:
		args_list.append((split, card_to_id, start_index))

	# Multiproccessing part 
	pool = Pool(cpu_count())
	df = pd.concat(pool.map(task, args_list))
	pool.close()
	pool.join()
	df.to_csv('draftlogs.csv')

if __name__ == "__main__":
	main()
