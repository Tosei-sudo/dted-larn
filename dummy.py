class File:
    def __init__(self, data):
        self.data = data
        self.pos = 0
        self.eof = False
    
    def read(self, size):
        self.pos += size
        self.eof = self.pos >= len(self.data)
        return self.data[self.pos-size:self.pos]
    
    def next(self, size = 1, offset = 0):
        tmp_pos = self.pos + size + offset
        return self.data[tmp_pos-size:tmp_pos]