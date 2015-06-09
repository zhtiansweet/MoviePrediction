__author__ = 'tianzhang'

import csv

with open("movies.csv", 'rU') as moviefile:
    reader = csv.reader(moviefile)
    reader.next()
    movie = {}
    for line in moviefile:
        splitted = line.rstrip().split(',')
        genres = splitted[-1].rstrip().split('|')
        movie[int(splitted[0])] = genres

print movie[23]
print movie[3]
print list(set(movie[23]).intersection(movie[3]))