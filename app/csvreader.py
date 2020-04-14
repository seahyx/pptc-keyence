import csv

class CSVReader:
    _data = []
    _open = False

    def __init__(self, fn):
        try:
            print (fn)
            with open(fn) as csvfile:
                _reader = csv.reader(csvfile)
                self._open = True
                for row in _reader:
                    print (row)
                    self._data.append(row)
        except Exception as ex: # File not found
            print ("File not found" + str(ex))
            self._open = False
    
    def isOpen (self):
        return self._open
        
    def search (self, value):
        print (value)
        if self._open:
            for row in self._data:
                print (row[0])
                if (row[0] == value):
                    print(row[0])
                    return row[2], row[3]   # mask, rack type
            
        return None, None