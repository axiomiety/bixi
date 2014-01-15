import  unittest
import  listener
import  metrics
from    mock      import Mock, patch

class DistanceMatrixTest(unittest.TestCase):
 
  locations = [metrics.Location(id=1,name='north pole',lat=0.1,long=-1.1),
               metrics.Location(id=2,name='east pole',lat=9.1,long=-7.7),
               metrics.Location(id=3,name='south pole',lat=9.1,long=-2.3)]

  @patch('builtins.open')
  @patch('os.path.isfile')
  @patch('metrics.DistanceMatrix.getLocations')
  @patch('metrics.DistanceMatrix.fetch')
  @patch('metrics.DistanceMatrix.gen_url')
  def test_batchLoadDistanceMatrix(self, gen_url, fetch, getLocations, os_path_isfile, builtins_open):
    
    # bit messy, but it allows us to mock quite a few unpickling/file reading bit
    from io import BytesIO
    import pickle
    b = BytesIO()
    o = {'remaining_location_pairs': [(2,3)], 'distance_matrix': {1: {2: 555}}}
    builtins_open.return_value      = b
    builtins_open.__exit__          = Mock(return_value=True)
    pickle.dump(o, b)
    b.seek(0)
    os_path_isfile.return_value     = True

    fetch.return_value              = None
    gen_url.return_value            = ''
    getLocations.return_value       = self.locations

    #TODO: would be nice to be able to run with dryrun=False but
    # it causes issues as it's reading from a closed file
    # maybe there's a better way to do this
    dm = metrics.DistanceMatrix._batchLoadDistanceMatrix(dryrun=True)
    gen_url.assert_called_with(self.locations[1], self.locations[2])
    self.assertEqual(dm, o)

class ListenerTest(unittest.TestCase):
  
  @classmethod
  def setUpClass(cls):
    s = '''<?xml version='1.0' encoding='UTF-8'?><stations lastUpdate="1388933822252" version="2.0"><station><id>1</id><name>Jarvis St/ Carleton St</name><terminalName>7055</terminalName><lastCommWithServer>1388933151006</lastCommWithServer><lat>43.66207</lat><long>-79.37617</long><installed>true</installed><locked>false</locked><installDate/><removalDate/><temporary>false</temporary><public>true</public><nbBikes>8</nbBikes><nbEmptyDocks>7</nbEmptyDocks><latestUpdateTime>1388899793575</latestUpdateTime></station><station><id>5</id><name>Church St/ Alexander St</name><terminalName>7044</terminalName><lastCommWithServer>1388933649708</lastCommWithServer><lat>43.6636</lat><long>-79.3806</long><installed>true</installed><locked>false</locked><installDate/><removalDate/><temporary>false</temporary><public>true</public><nbBikes>3</nbBikes><nbEmptyDocks>12</nbEmptyDocks><latestUpdateTime>1388903405786</latestUpdateTime></station></stations>'''
    from xml.etree import ElementTree
    cls.xml = ElementTree.fromstring(s)
    unittest.TestCase.setUpClass()

  def test_jsonEquivalent(self):
    j = listener.xml2json(self.xml)
    expected = '''{"1388933822252": [{"avail_bikes": 8, "empty_docks": 7, "id": "1", "lat": 43.66207, "long": -79.37617, "name": "Jarvis St/ Carleton St", "updatets": 1388899793575}, {"avail_bikes": 3, "empty_docks": 12, "id": "5", "lat": 43.6636, "long": -79.3806, "name": "Church St/ Alexander St", "updatets": 1388903405786}]}'''
    self.assertEqual(expected, j)

  def test_get_delta(self):
    u1 = {'1': {'updatets': 1389664469715, 'avail_bikes': 13, 'empty_docks': 10},
          '2': {'updatets': 1389677556074, 'avail_bikes': 11, 'empty_docks': 8}}
    u2 = {'1': {'updatets': 1389664469715, 'avail_bikes': 15, 'empty_docks': 8},
          '2': {'updatets': 1389677556074, 'avail_bikes': 6, 'empty_docks': 13}}

    expected = {'1': {'avail_bikes': -2, 'empty_docks': 2},
                '2': {'avail_bikes': 5, 'empty_docks': -5}}
    self.assertEqual(listener.get_delta(u1, u2), expected)

  def test_prune(self):
    import json
    o = listener.prune(json.loads(listener.xml2json(self.xml)))
    expected = {'1': {'avail_bikes': 8, 'empty_docks': 7, 'updatets': 1388899793575},
                '5': {'avail_bikes': 3, 'empty_docks': 12, 'updatets': 1388903405786}}
    self.assertEqual(o, expected)

if __name__ == '__main__':
  unittest.main()
