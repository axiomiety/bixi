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

def get_delta(fr, to):
  d = {}
  #TODO: do we care about keys in to but not in fr? (ie, new stations)
  # maybe we should just check the common keys
  for loc_id, upd in fr.items():
    delta = {}
    for k in ['avail_bikes', 'empty_docks']:
      delta[k] = upd[k] - to.get(loc_id, {}).get(k, 0)
    d[loc_id] = delta
  return d

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
  raw_data = bytearray()
  while True:
    raw = req.read()
    if not raw: break
    raw_data.extend(raw)
  if raw_data:
    raw_data = bytes(raw_data)
    try:
      xml = ElementTree.fromstring(raw_data)
    except ElementTree.ParseError as e:
      logging.error('Could not parse string as xml: %s' % raw_data)
      raise e
    return xml2json(xml)

def poll(delay=None, as_json=False):
  delay = delay or POLLING_INTERVAL
  if not os.path.exists(UPDATES_DIR):
    os.mkdir(UPDATES_DIR)
  baseline = json.loads(fetch())
  running = True
  while(running):
    snap = json.loads(fetch())
    if snap.keys() != baseline.keys(): # we have an update
      logging.info('update found!')
      ts = list(snap.keys())[0]
      # save it out!
      if as_json:
        with open(os.path.join(UPDATES_DIR, ts), 'a') as f:
          f.write(json.dumps(snap))
      else:
        with open(os.path.join(UPDATES_DIR, '%s.pickle' % ts), 'wb') as f:
          pickle.dump(prune(snap), f)

      baseline = snap

    time.sleep(delay)
    logging.info('slept %s seconds. yawn...' % POLLING_INTERVAL)

if __name__ == '__main__':
  poll()
