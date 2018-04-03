import re
import csv


def createCsv(file, header=None):
    with open(file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)

def addRowCsv(file, row):
    with open(file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(row)

def strip_emoji(text):
    RE_EMOJI = re.compile("[\U00010000-\U0010ffff]", flags=re.UNICODE)

    return RE_EMOJI.sub(r'', text)

