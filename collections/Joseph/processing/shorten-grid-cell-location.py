# -*- coding: utf-8 -*-
"""
Created on Sun Aug 15 12:52:09 2021

@author: Joseph

This is a script that shortens a list of grid cell values of the form <row>.<col>.<num>
to make the list easier for humans to read. The sorted list is ordered first by 
ascending <row>, then by ascending <col>, and finally by ascending <num>. The form of
the final list is <row>.<col>.<num>,<num>,...<num>; <row>.<col>.<num>; ... ;
"""
import csv
from collections import namedtuple

def sort_and_shorten_locations(locations, col_order, delim_in, delim_out):
    """Takes a string that is list of grid cell ids and returns a string listing the same cell ids
    but with a newly defined delimiter and sorted according to cell_order()"""
    Cell = namedtuple('Cell', ['row', 'col', 'num'])
    loc_cells = [Cell(c.split('.')[0], c.split('.')[1], c.split('.')[2]) for c in locations.split(delim_in)] #list comprehension
    
    # Lists of all the rows and cols matching to loc_cells, sorted in ascending order
    loc_cells_rows = sorted([c.row for c in loc_cells])
    loc_cells_cols = sorted([c.col for c in loc_cells], key=lambda col: col_order.index(col))
    
    # Initialize loc_short
    loc_short = ''
    
    for r in loc_cells_rows:
        for c in loc_cells_cols:
            # Get the cells corresponding to r and c
            loc_cells_select = [cell for cell in loc_cells if cell.row == r and cell.col == c]
            
            # Only trigger if there are cells to work with
            if len(loc_cells_select) > 0:
                
                # Remove selected cells from further iteration
                for s in loc_cells_select:
                    del loc_cells[loc_cells.index(s)]
                
                # Determine the current end character of loc_short
                if loc_cells_rows.index(r) == (len(loc_cells_rows)-1) or loc_cells_cols.index(c) == (len(loc_cells_cols)-1):
                    endchar = ''
                else:
                    endchar = delim_out
                
                # Get the nums and append to loc_short
                nums = [cell.num for cell in loc_cells_select]
                loc_short = loc_short + r + '.' + c + '.' + (','.join(map(str,nums))) + endchar
    
    # Remove a trailing delimiter if there is one and then return
    if loc_short[-len(delim_out):] == delim_out:
        loc_short = loc_short[:-len(delim_out)]
    return loc_short

# Col information
col_order = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII', 'XIII', 'XIV', 'XV',
        'XVI', 'XVII', 'XVIII', 'XIX', 'XX']

# Columns of interest in the data
cola = 1 #unique FeatureIDs
colb = 2 #lists of grid cell ids

# Import data
with open('FeatureTraceAndGrid5mIntersections_sortedshort.csv', newline='', encoding='utf-8-sig', mode='w') as outfile:
     with open('FeatureTraceAndGrid5mIntersections_cleaned.csv', newline='', encoding='utf-8-sig') as infile:
        csvwriter = csv.writer(outfile, delimiter=',')
        csvreader = csv.reader(infile, delimiter=',')
        header = next(csvreader, None)      #first line of csv is now removed from csvreader (https://stackoverflow.com/questions/42903157/how-to-use-csv-reader-object-multiple-times)
        
        # Write the header to outfile
        csvwriter.writerow(header)
        
        # Container for the rows from the CSV file
        rows = list(csvreader)
        rows = sorted(rows, key=lambda r: r[cola])
        
        # Do the sorting and write to outfile
        for row in rows:
            row[colb] = sort_and_shorten_locations(locations=row[colb], col_order=col_order, delim_in=', ', delim_out='; ')
            csvwriter.writerow(row)





