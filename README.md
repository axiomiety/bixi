bixi
====

Based on bixi (https://toronto.bixi.com/), a data feed for Toronto that gives status updates on the biking stations around the city. Just thought I'd try to do something interesting with the data.

## metrics.py ##

Right now it's mainly a helper to build the underlying data structures

## listener.py ##

Periodically checks for updates and stores them locally.

## pickle files ##

`locations.pickle` contains a dictionary of Location objects. Easy to re-generate

`dmatrix.pickle` contains the distance for each location permutation. This took some time to build with Google's DistanceMatrix API as they only allow a certain number of requests per day (and as there are around 80 stations, that's around 6,400 calls).

## updates ##

Contains some sample consecutive updates. It's worth noting that dumping the update as a JSON string is roughly 12K, but pickling it out it's 7.7K. And even that is probably not all that necessary - all we really need are a baseline and delta updates. Trimming the update, we can get this down to 3.2K. But at one update every minute, it's still around 4.6M a day.
