"""
Created on Sep 22, 2011
Modified Apr 13, 2022 for python 3
@author: theo
"""
import re


def readline(f):
    """ read a line from binary file and convert to string """
    return f.readline().decode()


class Adoreblock:
    """
    Stores parameter blocks in standard Triwaco format:
    Integer, Floating point or Text 
    """

    name = "UNTITLED,TIME: 0.0000"
    format = "13E6.4"
    filename = "file.ado"
    pos = 0
    data = []
    count = 0
    time = 0
    constant = True

    def __repr__(self):
        return '%s[%d]' % (self.name, self.count)

    def parse_format(self):
        """ 
        parse format string in rep, type, width and optional precision
        Examples: 13E6.3, 10A8
        returns dict with format components
        """
        match = re.match(r"(?P<rep>\d+)(?P<type>\w)(?P<width>\d+)(?:\.(?P<prec>\d+))?", self.format.upper())
        d = match.groupdict()
        if 'prec' not in d:
            d['prec'] = 0
        return d

    def set_default_time(self):
        """ Set the time to value from name of adoreblock """
        i = self.name.find(",TIME")
        if i > 0:
            tail = self.name[i + 6:]
            self.time = float(tail)

    def set_time(self, time):
        """ sets the time and updates the name of the adoreblock """
        self.time = time
        self.name = '%s,TIME:%10.4f' % (self.rootname, time)

    def get_rootname(self):
        """returns the root name: everything before first comma"""
        index = self.name.find(",")
        if index < 1:
            return self.name
        return self.name[0:index]

    def set_rootname(self, rootname):
        """sets the root name"""
        index = self.name.find(",")
        if index < 0:
            self.name = rootname
        else:
            self.name = rootname + self.name[index:]

    rootname = property(get_rootname, set_rootname)

    def get_value(self, index):
        if self.constant:
            index = 0
        return self.data[index]

    def set_value(self, index, value):
        self.data[index] = value

    def get_values(self):
        if not self.data:
            self.read_data()
        return self.data

    def read_data(self):
        fmt = self.parse_format()
        rep = int(fmt['rep'])
        width = int(fmt['width'])
        typ = fmt['type']
        with open(self.filename, 'rb') as f:
            f.seek(self.pos, 0)
            self.data = []
            while len(self.data) < self.count:
                line = readline(f)
                if line == '':
                    break
                for j in range(rep):
                    if len(self.data) >= self.count:
                        break
                    k = j * width
                    value = line[k:k + width]
                    if typ == 'A':
                        self.data.append(value)
                    elif typ == 'I':
                        self.data.append(int(value))
                    else:
                        self.data.append(float(value))

    def write(self, f):
        if not self.data:
            return
        fmt = self.parse_format()
        rep = int(fmt.get('rep', 1))
        width = int(fmt.get('width', 10))
        typ = fmt.get('type', 'F')
        prec = int(fmt.get('prec', 0))
        if typ == 'A':
            f.write('*TEXT*%s\n' % self.name)
        else:
            f.write('*SET*%s\n' % self.name)
        if self.constant:
            f.write('1\n')
            if typ == 'I':
                f.write('%d\n' % int(self.data[0]))
            elif typ == 'A':
                f.write('%s\n' % self.data[0])
            else:
                f.write('%#g\n' % self.data[0])
        else:
            f.write('2\n')
            if typ == 'I':
                fmt = '%%%d%%d' % width
            elif typ == 'A':
                fmt = '%%%d%%s' % width
            else:  # typ in ('F','E')
                fmt = '%%%d.%d%s' % (width, prec, typ.lower())
            f.write('%5d     (%s)\n' % (self.count, self.format))
            for i in range(self.count):
                val = fmt % self.data[i]
                f.write(val)
                if (i + 1) < self.count and (i + 1) % rep == 0:
                    f.write('\n')
            if typ == 'A':
                f.write('\nENDTEXT\n')
            else:
                f.write('\nENDSET\n')
            f.write('-' * 72)
            f.write('\n')


class AdoreCollection(dict):
    """ Collection (dict) of adoreblocks with setname as key """

    def __init__(self, filename=None):
        self.filename = None
        if filename is not None:
            self.scan(filename)

    def scan(self, filename):
        """ scan file for adoreblocks and build dictionary """
        with open(filename, 'rb') as f:
            self.filename = filename
            line = readline(f)
            while line != '':
                if line.startswith('*SET*'):
                    name = line[5:]
                elif line.startswith('*TEXT*'):
                    name = line[6:]
                else:
                    line = readline(f)
                    continue

                block = Adoreblock()
                block.filename = filename
                block.name = name.strip()
                block.set_default_time()
                line = readline(f)
                block.constant = int(line) == 1
                if not block.constant:
                    line = readline(f)
                    block.count = int(line[:10])
                    block.format = line[10:].strip('() \r\n')
                block.pos = f.tell()
                self[block.name] = block

                # move file pointer near next block
                d = block.parse_format()
                rep = int(d['rep'])
                width = int(d['width'])
                nlines = block.count / rep + 1
                # add additional byte(s) for line terminator
                extra = 2 if line.endswith('\r\n') else 1
                linesize = rep * width + extra
                offset = int(nlines * linesize)
                f.seek(offset, 1)

                line = readline(f)

    def find_first(self, name):
        """ find first adoreblock in collection using case insensitive, partial search """
        caps = name.upper()
        for key in self.keys():
            if key.upper().startswith(caps):
                return self.get(key)
        return None

    def __getitem__(self, item):
        """ supports case insensitive, partial match """
        return self.find_first(item)


class AdoreValues(dict):
    """ collection of adoreblocks with transient data """

    def __init__(self, name, collection=None):
        self.name = name
        if collection is None:
            return
        for b in collection.values():
            if b.rootname.upper() == name.upper():
                self[b.time] = b

    @property
    def times(self):
        """ return sorted array of timesteps """
        return sorted(self.keys())

    def get_values(self, time=0):
        """ get values for a single timestep """
        a = self[time]
        if len(a.data) == 0:
            a.read_data()
        return a.data

    def set_values(self, values, time=0):
        """ set values for single timestep """
        self[time].data = values

    def get_value(self, index, time=0):
        """ get value at specified index for a single timestep """
        values = self.get_values(time)
        return values[index]

    def set_value(self, index, value, time=0):
        """ set value at specified index for a single timestep """
        values = self.get_values(time)
        values[index] = value

    def get_timeseries(self, index):
        """ get timeseries data at specified index """
        return [[time, self.get_value(index, time)] for time in self.times]

    def set_timeseries(self, index, series):
        """
        set timeseries data at specified index
        series = array with same length as number of timesteps
        """
        for time in self.times:
            self.set_value(index, series[index], time)
