from os import listdir, path
import requests

M19_DIR_PATH = path.join('..', 'M19_DECKS')
DOWNLOAD_DIR = 'M19_draft_logs'
MIN_DRAFT_ID = 30000
BASE_URL = 'http://www.top8draft.com/downloadDraft/'


def download_draft_log(draft_number, player_name, save_filename):
    """
    Download a draft log
    """
    try:
        download_url = BASE_URL + str(draft_number) + '/' + player_name
        response = requests.get(download_url)

        with open(save_filename, 'wb') as fp:
            if response.content:
                fp.write(response.content)
                return
            # We can't just check the status code for bad urls
            # because they still return a 200 status code
            print('----- ERROR:: draft_num:{} player_name:{} -----'.format(draft_number, player_name))
    except Exception:
        print('----- ERROR:: draft_num:{} player_name:{} -----'.format(draft_number, player_name))


def get_deck_info(deck_json_filename):
    """
    Return the draft number and real player name.
    """
    file_no_ext = get_file_no_ext(deck_json_filename)
    info = file_no_ext.split('_')
    draft_id = info[0]
    player_name = info[1]
    return draft_id, player_name


def get_file_no_ext(filename):
    return path.splitext(filename)[0]


if __name__ == '__main__':
    only_files = [f for f in listdir(M19_DIR_PATH) if path.isfile(path.join(M19_DIR_PATH, f))]
    count = 0
    for file in only_files:
        if count % 1000 == 0:
            print('Working...: ', count)
        count += 1

        file_path = path.join(M19_DIR_PATH, file)
        download_filename = get_file_no_ext(file) + '.txt'
        download_file_path = path.join(DOWNLOAD_DIR, download_filename)
        if file.endswith('.json') and not file == 'consolidated_decks.json':
            draft_id, player_name = get_deck_info(file)
            if int(draft_id) >= MIN_DRAFT_ID:
                download_draft_log(draft_id, player_name, download_file_path)

