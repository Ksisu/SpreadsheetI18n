import json
import gspread
import os
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
load_dotenv()

CLIENT_SECRET = json.loads(os.getenv('CLIENT_SECRET'))
SHEET_URL = os.getenv('SHEET_URL')

OUTPUT_DIR = 'out'


def add_key_value_to_dict(db: dict, key: str, value: str):
    path = list(key.split('.'))
    key = path.pop()
    parent = db
    for p in path:
        if p not in parent:
            parent[p] = {}
        parent = parent[p]
    parent[key] = value


def download_translations_data() -> gspread.models.ValueRange:
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials._from_parsed_json_keyfile(CLIENT_SECRET, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_url(SHEET_URL).sheet1
    return sheet.get(f'A7:G{sheet.row_count}')


def parse_to_database(data: gspread.models.ValueRange, col_idx: int) -> dict:
    database = {}
    for d in data:
        key = d[0]
        if key == '':
            break
        value = ''
        try:
            value = d[col_idx].replace('\n', ' ').replace('\r', '')
        except:
            print(f'\033[93m[WARN]\033[0m Missing value from [{key}] col_idx: [{col_idx}]')
        add_key_value_to_dict(database, key, value)
    return database


def convert_to_play_messages(db: dict, path = '') -> str:
    result = ''
    for key in db:
        path_key = key if path == '' else path + '.' + key
        if type(db[key]) == type({}):
            result += convert_to_play_messages(db[key], path_key)
        else:
            result += f'{path_key}={db[key]}\n'
    return result


def convert_to_frontend_localization(db: dict) -> str:
    return json.dumps(db, indent=2, sort_keys=True)


def save_to_file(text: str, filename: str):
    f = open(filename, "w")
    f.write(text)
    f.close()

def main():
    print('[INFO] Download spreadsheet')
    data = download_translations_data()

    print('[INFO] Parse English [EN]')
    database_en = parse_to_database(data, 1)
    print('[INFO] Parse German [DE]')
    database_de = parse_to_database(data, 2)
    print('[INFO] Parse Hungarian [HU]')
    database_hu = parse_to_database(data, 3)
    print('[INFO] Parse Serbian [SR]')
    database_sr = parse_to_database(data, 4)
    print('[INFO] Parse Indonesian [ID]')
    database_id = parse_to_database(data, 5)

    print('[INFO] Create output directory')
    if not os.path.exists('out'):
        os.makedirs('out')

    print('[INFO] Create and save messages')
    save_to_file(convert_to_play_messages(database_en), f'{OUTPUT_DIR}/messages')
    print('[INFO] Create and save messages.de')
    save_to_file(convert_to_play_messages(database_de), f'{OUTPUT_DIR}/messages.de')
    print('[INFO] Create and save messages.hu')
    save_to_file(convert_to_play_messages(database_hu), f'{OUTPUT_DIR}/messages.hu')
    print('[INFO] Create and save messages.sr')
    save_to_file(convert_to_play_messages(database_sr), f'{OUTPUT_DIR}/messages.sr')
    print('[INFO] Create and save messages.id')
    save_to_file(convert_to_play_messages(database_id), f'{OUTPUT_DIR}/messages.id')

    print('[INFO] Create and save locale-en.json')
    save_to_file(convert_to_frontend_localization(database_en), f'{OUTPUT_DIR}/locale-en.json')
    print('[INFO] Create and save locale-de.json')
    save_to_file(convert_to_frontend_localization(database_de), f'{OUTPUT_DIR}/locale-de.json')
    print('[INFO] Create and save locale-hu.json')
    save_to_file(convert_to_frontend_localization(database_hu), f'{OUTPUT_DIR}/locale-hu.json')
    print('[INFO] Create and save locale-sr.json')
    save_to_file(convert_to_frontend_localization(database_sr), f'{OUTPUT_DIR}/locale-sr.json')
    print('[INFO] Create and save locale-id.json')
    save_to_file(convert_to_frontend_localization(database_id), f'{OUTPUT_DIR}/locale-id.json')

    print('[INFO] Finished')


if __name__ == '__main__':
    main()