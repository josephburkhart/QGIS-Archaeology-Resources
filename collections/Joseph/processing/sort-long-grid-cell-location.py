# -*- coding: utf-8 -*-
"""
Created on Sun Aug 15 12:52:09 2021

@author: Joseph

This is a script that sorts a list of grid cell values of the form <row>.<col>.<num>
to make the list easier for humans to read. The sorted list is ordered first by 
ascending <row>, then by ascending <col>, and finally by ascending <num>. All
grid cell values are separated by semi-colons.
"""
import csv
from collections import namedtuple

def cell_order(cell):
    """Returns a tuple that will be used to sort cells. Note that leftmost elements in a tuple are 
    considered more important in comparisons
    
    Ref: https://stackoverflow.com/questions/16865372/how-to-do-hierarchical-sorting-in-python"""
    return (cell.row, all_cols.index(cell.col), int(cell.num))

def sort_locations(locations, delim_in, delim_out):
    """Takes a string that is list of grid cell ids and returns a string listing the same cell ids
    but with a newly defined delimiter and sorted according to cell_order()"""
    # Create structure with namedtuple (makes sorting easier)
    Cell = namedtuple('Cell', ['row', 'col', 'num'])
    loc_cells_unsorted = [Cell(c.split('.')[0], c.split('.')[1], c.split('.')[2]) for c in locations.split(delim_in)] #list comprehension
    
    # Sort the structured list in ascending order first according to row, then col, and finally num
    loc_cells_sorted = sorted(loc_cells_unsorted, key=cell_order)
    
    # Create loc_sorted
    loc_sorted = ''
    for c in loc_cells_sorted:
        #determine current end character for loc_sorted
        if loc_cells_sorted.index(c) == (len(loc_cells_sorted)-1):
            endchar = ''
        else:
            endchar = delim_out
        loc_sorted = loc_sorted + (c.row + '.' + c.col + '.' + c.num) + endchar
    
    return loc_sorted

# Grid Row and Col information
all_rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q']
all_cols = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII', 'XIII', 'XIV', 'XV',
        'XVI', 'XVII', 'XVIII', 'XIX', 'XX']

# Columns of interest in the data
cola = 1 #unique FeatureIDs
colb = 2 #lists of grid cell ids

# Import data
with open('FeatureTraceAndGrid5mIntersections_sortedlong.csv', newline='', encoding='utf-8-sig', mode='w') as outfile:
     with open('FeatureTraceAndGrid5mIntersections_cleaned.csv', newline='', encoding='utf-8-sig') as infile:
        csvwriter = csv.writer(outfile, delimiter=',')
        csvreader = csv.reader(infile, delimiter=',')
        header = next(csvreader, None)      #first line of the csv is now removed from csvreader (https://stackoverflow.com/questions/42903157/how-to-use-csv-reader-object-multiple-times)
        
        # Write the header to outfile
        csvwriter.writerow(header)
        
        # Container for the rows from the CSV file
        rows = list(csvreader)
        rows = sorted(rows, key=lambda r: r[cola])
        
        # Do the sorting and write to outfile
        for row in rows:
            row[colb] = sort_locations(locations=row[colb], delim_in=', ', delim_out='; ')
            csvwriter.writerow(row)