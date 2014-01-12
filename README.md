bixi
====

Based on bixi (https://toronto.bixi.com/), a data feed for Toronto that gives status updates on the biking stations around the city. Just thought I'd try to do something interesting with the data.

==metrics==

Right now it's mainly a helper to build the underlying data structures

==listener==

Periodically checks for updates and stores them locally.

==pickle files==

`locations.pickle` contains a dictionary of Location objects. Easy to re-generate

`dmatrix.pickle` contains the distance for each location permutation. This took some time to build with Google's DistanceMatrix API as they only allow a certain number of requests per day (and as there are around 80 stations, that's around 6,400 calls).
