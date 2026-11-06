import json
import re
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.request import urlopen

from bs4 import BeautifulSoup

OUTPUT = Path('data/research-web')
OUTPUT.mkdir(parents=True, exist_ok=True)


def read(url):
    with urlopen(url, timeout=30) as response:
        return response.read()


def collect(source, entries):
    target = OUTPUT / f'{source}.json'
    records = json.loads(target.read_text()) if target.exists() else []
    known = {item['url'] for item in records}
    added = 0
    for entry in entries:
        if entry['url'] in known:
            continue
        page = BeautifulSoup(read(entry['url']), 'html.parser')
        title = page.select_one('h1').get_text(' ', strip=True)
        main = page.select_one('main')
        text = main.get_text('\n', strip=True)
        text = text[text.index(title):]
        if source == 'indiefront':
            text = text.split('\n标签\n')[0]
        else:
            text = re.split(r'\n讨论\s*\(', text)[0]
        records.append({**entry, 'title': title, 'bodyText': text,
                        'source': source, 'collectedAt': datetime.now().isoformat()})
        known.add(entry['url'])
        added += 1
        temporary = target.with_suffix('.json.tmp')
        temporary.write_text(json.dumps(records, ensure_ascii=False, indent=2))
        temporary.replace(target)
        time.sleep(1)
    print(f'{datetime.now().isoformat()} {source} 新增 {added} 篇，累计 {len(records)} 篇', flush=True)


listing = BeautifulSoup(read('https://indiefront.cn/articles/'), 'html.parser')
entries = []
for link in listing.select('a.group[href^="/articles/"]'):
    date = re.search(r'\d{4}-\d{2}-\d{2}', link.get_text(' ', strip=True))
    entries.append({'url': 'https://indiefront.cn' + link['href'],
                    'publishedAt': date.group() if date else None})
collect('indiefront', entries)

feed = ET.fromstring(read('https://solo.xin/rss.xml'))
entries = []
for item in feed.findall('channel/item'):
    entries.append({'url': item.findtext('link'),
                    'publishedAt': parsedate_to_datetime(item.findtext('pubDate')).isoformat(),
                    'author': item.findtext('author')})
collect('solo', entries)
