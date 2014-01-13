# poll?
# compress periodically?

import  urllib.request
import  json
import  time
import  logging
import  os
import  pickle
from    xml.etree       import ElementTree

PARSING_MAP = {
  'id'          : lambda e: e.find('id').text,
  'name'        : lambda e: e.find('name').text,
  'lat'         : lambda e: float(e.find('lat').text),
  'long'        : lambda e: float(e.find('long').text),
  'avail_bikes' : lambda e: int(e.find('nbBikes').text),
  'empty_docks' : lambda e: int(e.find('nbEmptyDocks').text),
  'updatets'    : lambda e: int(e.find('latestUpdateTime').text)
  }

POLLING_INTERVAL = 10 # a minute
UPDATES_DIR = 'updates'

###
# misc

def _foo(paths):
  for p in paths:
    with open(p) as f:
      x = f.readline()
    with open('%s.pickle' % p, 'wb') as f:
      pickle.dump(json.loads(x), f)

def _bar(x):
  with open(x, 'rb') as f:
    return pickle.load(f)

###
# parsing

def prune(update):
  '''return a condensed version with only the update with just the necessary information'''
  d = dict()
  for updatets, up in update.items():
    for u in up:
      d[u['id']] = {k: v for k, v in u.items() if k in ['avail_bikes', 'empty_docks', 'updatets']}
  return d

def get_delta(update):
  pass

def xml2json(root):
  stations = []
  for station in root.findall('station'):
    s = dict()
    for attrib in PARSING_MAP:
      s[attrib] = PARSING_MAP[attrib](station)
    stations.append(s)
  return json.dumps({root.get('lastUpdate'): stations}, sort_keys=True)

def fetch():
  req = urllib.request.urlopen('https://toronto.bixi.com/data/bikeStations.xml')
  raw_data = req.read()
  if raw_data:
    xml = ElementTree.fromstring(raw_data)
    return xml2json(xml)

def poll(delay=None, as_json=False):
  delay = delay or POLLING_INTERVAL
  if not os.path.exists(UPDATES_DIR):
    os.mkdir(UPDATES_DIR)
  baseline = fetch()
  running = True
  while(running):
    snap = fetch()
    if snap != baseline: # we have an update
      logging.info('update found!')
      o = json.loads(snap)
      ts = list(o.keys())[0]
      # save it out!
      if as_json:
        with open(os.path.join(UPDATES_DIR, ts), 'a') as f:
          f.write(snap)
      else:
        with open(os.path.join(UPDATES_DIR, '%s.pickle' % ts), 'wb') as f:
          pickle.dump(prune(o), f)

      baseline = snap

    time.sleep(delay)
    logging.info('slept %s seconds. yawn...' % POLLING_INTERVAL)

if __name__ == '__main__':
  poll()
