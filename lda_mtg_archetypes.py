import json
import re
import sys
from io import BytesIO

import gensim
import numpy as np
import requests
from six import iteritems

from PIL import Image

def getCard(id):
    """
    Returns card JSON based on ID from Scryfall API
    """
    r = requests.get('https://api.scryfall.com/cards/multiverse/' + str(id))
    data = r.json()
    try:
        name = data['name']
    except KeyError:
        name = ''
    try:
        url = data['image_uris']['normal']
    except KeyError:
        url = ''
    return name, url

def getImage(url):
    """
    Returns "normal" image JPEG from Scryfall Image Library
    """
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    return img

class MyCorpus(object):
	def __init__(self, decks_json, card_dictionary):
		self.decks_json = decks_json
		self.card_dictionary = card_dictionary
	
	def __iter__(self):
		with open(self.decks_json) as jsonfile:
			data = json.load(jsonfile)

			for deck in data['decks']:
				cleaned_decklist = []

				for card_name in deck:
					card_count = deck[card_name]

					for i in range(card_count):
						cleaned_decklist.append(card_name)

				yield self.card_dictionary.doc2bow(cleaned_decklist)


def get_gensim_dictionary(decks_json):
	with open(decks_json) as jsonfile:
		data = json.load(jsonfile)
		card_dictionary = gensim.corpora.Dictionary([card.strip() for card in deck] for deck in data['decks'])

    # remove cards that appear only once
		once_ids = [tokenid for tokenid, docfreq in iteritems(card_dictionary.dfs) if docfreq == 1]
		card_dictionary.filter_tokens(once_ids)

		# remove gaps in id sequence after words that were removed
		card_dictionary.compactify()

		return card_dictionary

def train_model(corpus_memory_friendly, archetypes=30, iterations=30):
	alpha_prior = [1.0 / archetypes] * archetypes
	beta_prior  = [1.0 / archetypes] * len(corpus_memory_friendly.card_dictionary.keys())
	return gensim.models.ldamodel.LdaModel(
		corpus=corpus_memory_friendly,
		id2word=corpus_memory_friendly.card_dictionary,
		num_topics=archetypes,
		passes=iterations,
		alpha = alpha_prior,
		eta = beta_prior
	)

def export_archetypes(lda, num_archetypes=15, num_cards=45, outfile="30_archetypes.json"):
    """
    Export the top most probable cards per archetype to a json file.
    """
    with open(outfile, 'w') as f:
        archetypes_list = []
        for archetype_id in range(num_archetypes):
            archetype_json = {}
            archetype_json['archetype_id'] = archetype_id
            archetype_json['num_cards'] = num_cards
            archetype_json['cards'] = []
            for card_id, prob in np.array(lda.show_topic(archetype_id, topn=num_cards)):
                card_name, image_url = getCard(card_id)
                archetype_json['cards'].append({'card_id': card_id,
                                                'probability': prob,
                                                'card_name': card_name,
                                                'image_url': image_url})
            archetypes_list.append(archetype_json)
        json.dump(archetypes_list, f)

def main():
	decks_json = sys.argv[1]
	out_json = sys.argv[2]

	print(decks_json)
	print(out_json)

	gensim_dict = get_gensim_dictionary(decks_json)
	corpus_memory_friendly = MyCorpus(decks_json=decks_json, card_dictionary=gensim_dict)
	lda = train_model(corpus_memory_friendly=corpus_memory_friendly)
	export_archetypes(lda=lda, outfile=out_json)

if __name__ == "__main__":
	main()
