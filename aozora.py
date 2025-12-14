#!/usr/bin/env python

from io import BytesIO
import re
import sys
import zipfile
import requests

def get_page(url):
    if not url.startswith('http'):
        with open(url, 'rb') as fp:
            return fp.read()
        raise Exception(f'Failed to read local file: {url}.')

    resp = requests.get(url)
    if resp.status_code != 200:
        raise Exception(f'HTTP failure. Code {resp.status_code}.')

    return resp.content


def parse_zipped(zipped_data):
    zp = zipfile.ZipFile(BytesIO(zipped_data))
    text_files = [z for z in zp.infolist() if z.filename.lower().endswith('.txt')]
    if len(text_files) == 0:
        raise Exception("Can't find any text file in the Zip.")

    info = text_files[0]
    with zp.open(info) as fp:
        text_bytes = fp.read()
        text = text_bytes.decode('shift-jis', errors='replace')

    return text


def sanitize_aozora(text):
    # --- (55個) とその間はメタデータ/注釈なので空行と入れ替える。
    first = text.find('-'*55, 0)
    second = text.find('-'*55, first+55)
    text = text[:first] + text[second+55:]

    # ［］（全角角括弧）はタイポグラフィカルな注意なので抜く
    text = re.sub(r'［.+?］', '', text)

    # 《》はルビなので抜く。｜（全角縦棒）もルビの範囲を示す記号なので抜く。
    text = re.sub(r'《.+?》', '', text)
    text = text.replace('｜', '')

    # 最後の底本情報も抜く。
    last = text.rfind('\r\n\r\n');
    text = text[:last]

    return text


def get_aozora(url):
    zipped_data = get_page(url)
    text = parse_zipped(zipped_data)
    sanitized = sanitize_aozora(text)

    return sanitized


def parse_text_into_sentences(text):
    paragraphs = [par for par in re.split(r'[\r\n]+', text) if len(par) > 0]
    sentences = []
    for par in paragraphs:
        sentences.extend([s.strip() for s in re.split(r'。[」』]*', par) if len(s) > 0])

    return sentences


if __name__ == '__main__':
    import sys
    url = sys.argv[1]
    text = get_aozora(url)
    print(text)

    sentences = parse_text_into_sentences(text)
    print('\n'.join(sentences))
