'''
Created on Aug 14, 2015

@author: theo
'''
import os, sys, re
from adore import AdoreCollection

if __name__ == '__main__':
    
    if len(sys.argv) != 4:
        print 'Syntax: stitch.py folder setname dest.flo'
        exit
    
    folder = sys.argv[1]
    setname = sys.argv[2].upper()
    dest = sys.argv[3]
    
    # get all flo files from folder
    flo = []
    for root, dirs, files in os.walk(folder):
        for name in files:
            # get starting time for this flo file
            # time is extracted from filename, e.g. flairs_1234.flo
            if name.lower().endswith('.flo'):
                match = re.search('_(\d+)\.', name)
                if match is not None:
                    time = float(match.groups(1)[0])
                    flo.append((time,os.path.join(root,name)))

    # reverse sort flo files on starting time
    flo.sort(key=lambda f: -f[0])
    
    result = {}
    for flotime,flofile in flo:
        
        # select adoreblocks with matching rootname from flofile
        blocks = [a for a in AdoreCollection(flofile).values() if a.rootname.upper() == setname]
        
        # sort blocks on ascending time
        blocks.sort(key=lambda a: a.time)

        # modify the time (add offset from flo filename)
        t0 = blocks[0].time
        for a in blocks:
            a.set_time(flotime + (a.time - t0))
            # add to result dict. If timestep already exists the data will be replaced by data from flo file with lower starting time
            result[a.time] = a

    # write (sorted) result to destination file 
    with open(dest,'w') as f:
        for a in sorted(result.values(),key=lambda a:a.time):
            print a.name
            a.read_data()
            a.write(f)
            del a.data

