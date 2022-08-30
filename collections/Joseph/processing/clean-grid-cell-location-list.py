# -*- coding: utf-8 -*-
"""
Created on Wed Aug 18 10:33:47 2021

@author: Joseph

This script takes a csv file of intersections between two layers from QGIS and condenses
the labels in one column into a list based on duplicate values in another column. It also
sorts the lists by ascending FeatureID

Note that this uses namedtuple. If you want to use this with a different csv file, you will
need to change the attribute names directly in the code. (Sorry! I had too little time
to be elegant about this...)
"""
import csv

# Parameters
cola = 1 #index of column containing duplicate values that will be used to condense values in rb into a list
colb = 2 #index of row containing values that will be condensed into a list based on duplicate values in ra

# Open the input csv file and extract each row as a named tuple
with open('FeatureTraceAndGrid5mIntersections_cleaned.csv', newline='', encoding='utf-8-sig', mode='w') as outfile:
     with open('FeatureTraceAndGrid5mIntersections.csv', newline='', encoding='utf-8-sig') as infile:
        csvwriter = csv.writer(outfile, delimiter=',')
        csvreader = csv.reader(infile, delimiter=',')
        header = next(csvreader, None)      #first line of the csv is now removed from csvreader (https://stackoverflow.com/questions/42903157/how-to-use-csv-reader-object-multiple-times)
        
        # Container for the rows from the CSV file
        rows = list(csvreader)
        rows = sorted(rows, key=lambda r: r[cola])
        
        for row in rows:
            # Only trigger if there are FeatureID duplicates below the current row
            rownum = rows.index(row) 
            if ((len(rows)-1) - rownum) > 2: #skip the last two rows for this check
                remaining_cola = [r[cola] for r in rows[(rownum+1):]]
                if row[cola] in remaining_cola: 
                    
                    # Get all rows with current FeatureID and add their GridIDs to this one, filter out the current row to avoid duplicate GridID values
                    rows_select = [r for r in rows if r[cola] == row[cola] and r[colb] != row[colb]]   #could be more efficient by only searching rows from the current rownum down
                    row[colb] = row[colb] + ', ' + (', '.join([r[colb] for r in rows_select]))
                    
                    # Remove the duplicate rows
                    for r in rows_select:
                        del rows[rows.index(r)]
                        print('deleted ' +str(r))
            
            if ((len(rows)-1) - rownum) == 2: #check for the last value (note that I could make code more concise with a function)
                if row[cola] == rows[rownum+1][cola]: #note the multidimensional indexing inside a list of tuples - this is very inelegant
                    
                    # Get all rows with current FeatureID and add their GridIDs to this one, filter out the current row to avoid duplicate GridID values
                    rows_select = [r for r in rows if r[cola] == row[cola] and r[colb] != row[colb]] 
                    row[colb] = row[colb] + ', ' + (', '.join([r[colb] for r in rows_select]))
                    
                    # Remove the duplicate rows
                    for r in rows_select:
                        del rows[rows.index(r)]
                        print('deleted ' +str(r))
                    
        # Write the row to outfile
        csvwriter.writerow(header)
        csvwriter.writerows(rows)
        