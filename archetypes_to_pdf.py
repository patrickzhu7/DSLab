"""
This file creates pdfs of the most probable archetype cards
to better visualize each archetype.
"""

from fpdf import FPDF
import json
import os
import requests
import sys
from PIL import Image
from io import BytesIO


class ArchetypePdfHandler:
    CARDS_PER_ROW = 5
    CARDS_PER_PAGE = 25

    def __init__(self):
        # original card dimensions: 448 x 680
        self._x = 0
        self._y = 0
        self._w = 41
        self._h = 57
        self._pdf = FPDF()

        self._total_count = 0
        self._archetype_count = 0

    def create_archetype_pdf(self, json_file="30_archetypes.json", out_file="yourfile.pdf"):
        with open(json_file, 'r') as fp:
            archetypes_json = json.load(fp)
            self._new_page()
            for archetype in archetypes_json:
                # print('Processing archetype ', self._archetype_count)
                for card in archetype['cards']:
                    image_url = card['image_url']
                    self._add_image(image_url)
                    self._prep_next_card_coordinates()
                    self._total_count += 1
                    self._archetype_count += 1
                self._new_page()
                self._archetype_count = 0
            self._pdf.output(out_file, 'F')

    def _new_page(self):
        self._reset_x()
        self._reset_y()
        self._pdf.add_page()

    def _add_image(self, url):
        if not url:
            return
        print('url: ', url)
        image_filename = 'temp{}.jpg'.format(self._total_count)
        ArchetypePdfHandler.get_image(url).save(image_filename)
        self._pdf.image(image_filename, self._x, self._y, self._w, self._h)
        os.remove(image_filename)

    def _prep_next_card_coordinates(self):
        self._increment_x()
        if self._archetype_count % ArchetypePdfHandler.CARDS_PER_ROW == ArchetypePdfHandler.CARDS_PER_ROW - 1:
            # Go to next row
            self._reset_x()
            self._increment_y()
        if self._archetype_count % ArchetypePdfHandler.CARDS_PER_PAGE == ArchetypePdfHandler.CARDS_PER_PAGE - 1:
            # Go to next page
            self._reset_y()
            self._pdf.add_page()

    def _reset_x(self):
        self._x = 0

    def _reset_y(self):
        self._y = 0

    def _increment_x(self):
        self._x += 42

    def _increment_y(self):
        self._y += 57

    @staticmethod
    def get_image(url):
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        return img


if __name__ == '__main__':
    pdf_handler = ArchetypePdfHandler()
    pdf_handler.create_archetype_pdf(sys.argv[1], sys.argv[2])

