from os import path
# from app import configfile
from datetime import datetime

racks = {'Cartridge':0, 'Tube':1, 'Trough':2}
fileformats = {0:'%s %14s  %s    %8s %-8s %15s %13s         %-15s %-15s %-15s %-15s %-15s %-15s %-15s %-15s %-15s %-15s %-15s %-15s %-15s %-15s %-15s %-15s %-15s %-15s %-15s',
        1:'%s %s %s %15s %s %-15s %-15s %-15s %-15s %-15s %-15s %-15s %-15s %-15s %-15s %-15s %-15s %-15s %-15s %-15s %-15s %-15s %-15s %-15s %-15s %-15s %-15s %-15s %-15s',
        2:'%s %s %s %15s %s %-15s %-15s %-15s %-15s'}
    
class Log_file:

    def __init__ ():
        pass
    
    def write_file(filename, data, racktype):
        if path.exists(filename):
            f = open (filename, 'a')
            f.write('\n')
        else:
            f = open (filename, 'w') # new file

        newdata = (datetime.now().strftime('%Y%m%d_%H%M%S'), ) + data
        print (fileformats[racktype])
        print (newdata)
        f.write(fileformats[racktype] % newdata)
        f.close()