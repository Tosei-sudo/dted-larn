# coding: utf-8
import struct
import numpy as np

def convet_60to10(value):
    direction_chr = value[-1]
    if direction_chr == "N" or direction_chr == "S":
        value10 = int(value[:2]) + int(value[2:4]) / 60.0 + int(value[4:6]) / 3600.0
    else:
        value10 = int(value[:3]) + int(value[3:5]) / 60.0 + int(value[5:7]) / 3600.0
    
    if direction_chr == "S" or direction_chr == "W":
        value10 = -value10
    return value10

class Point():
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y

    def read(self, file, accuracy = 15):
        if accuracy == 15:
            y_60 = file.read(7)
            x_60 = file.read(8)
        elif accuracy == 16:
            y_60 = file.read(8)
            x_60 = file.read(8)
        elif accuracy == 19:
            y_60 = file.read(9)
            x_60 = file.read(10)
        self.x = convet_60to10(x_60)
        self.y = convet_60to10(y_60)

class UHL():
    def read(self, file):
        self.header = file.read(3) # UHL
        file.read(1)
        
        self.position = Point()
        self.position.read(file, 16)
        
        self.longitude_interval = file.read(4)
        self.latitude_interval = file.read(4)
        self.absolute_vertical_accuracy = file.read(4)
        self.security_code = file.read(3).strip()
        self.unique_reference = file.read(12).strip()
        self.number_of_longitude_lines = file.read(4)
        self.number_of_latitude_points = int(file.read(4))
        self.multiple_accuracy = file.read(1)
        file.read(24)

class DSI():
    def read(self, file):
        self.header = file.read(3) # DSI
        self.security_code = file.read(1)
        self.security_marking = file.read(2)
        self.security_handring = file.read(27)
        file.read(26)
        self.NIMA = file.read(5)
        self.unique_reference = file.read(15)
        file.read(8)
        self.data_editon_number = file.read(2)
        self.match_merge_version = file.read(1)
        self.maintenance_date = file.read(4)
        self.match_merge_date = file.read(4)
        self.maintenance_description = file.read(4)
        self.producer_code = file.read(8)
        file.read(16)
        self.product_specification = file.read(9)
        self.versigon_digits = file.read(2)
        self.product_specification_date = file.read(4)
        self.vertival_datum = file.read(3)
        self.horizontal_datum = file.read(5)
        self.free_text = file.read(10)
        self.compilation_date = file.read(4)
        file.read(22)
        
        self.origin_data = Point()
        self.origin_data.read(file, 19)
        
        self.sw_corner = Point()
        self.sw_corner.read(file, 15)
        self.nw_corner = Point()
        self.nw_corner.read(file, 15)
        self.ne_corner = Point()
        self.ne_corner.read(file, 15)
        self.se_corner = Point()
        self.se_corner.read(file, 15)
        
        self.north_angle = file.read(9)
        
        self.latitude_interval = float(file.read(4))
        self.longitude_interval = float(file.read(4))
        
        self.latitude_lines_count = int(file.read(4))
        self.longitude_lines_count = int(file.read(4))
        
        self.partial_cell_indicator = file.read(2)
        file.read(357)

class ACC():
    def read(self, file):
        self.header = file.read(3) # DSI
        self.horizontal_accuracy_meters = file.read(4)
        self.vertical_accuracy_meters = file.read(4)
        self.relative_horizontal_accuracy_meters = file.read(4)
        self.relative_vertical_accuracy_meters = file.read(4)
        file.read(4)
        self.nima = file.read(1)
        file.read(31)
        self.accuracy_outline_flag = file.read(2)
        self.sub_region_horizontal_accuracy_meters = file.read(4)
        self.sub_region_vertical_accuracy_meters = file.read(4)
        self.sub_region_relative_horizontal_accuracy_meters = file.read(4)
        self.sub_region_relative_vertical_accuracy_meters = file.read(4)
        self.accuracy_sub_region_coordinates_count = file.read(2)

        # よくわかってない sub regionの座標かなんかそんな感じ
        for i in range(133):
            file.read(19)
        file.read(98)

class DataRecord():
    def read(self, file, uhl):
        self.header = file.read(1) # 252(8)

        self.data_block_count = struct.unpack(">i", "\x00" + file.read(3))[0]
        self.longitude_count = struct.unpack(">H", file.read(2))[0]
        self.latitude_count = struct.unpack(">H", file.read(2))[0]

        raw_elevetions = file.read(uhl.number_of_latitude_points * 2)
        dt = np.dtype(np.int16).newbyteorder('>')
        self.elevetions = np.frombuffer(raw_elevetions, dtype=dt)
        self.checksum = file.read(4)

class DTED2():
    def read(self, file):
        self.uhl = UHL()
        self.uhl.read(file)
        
        self.dsi = DSI()
        self.dsi.read(file)
        
        self.acc = ACC()
        self.acc.read(file)
        
        self.data_records = []
        while not file.eof:
            data_record = DataRecord()
            data_record.read(file, self.uhl)
            self.data_records.append(data_record)
        
        self.elevetion_map = np.zeros((self.dsi.latitude_lines_count, self.dsi.longitude_lines_count))
        for (j, data_record) in enumerate(self.data_records):
            self.elevetion_map[:, j] = data_record.elevetions
    
    def get_elevetion(self, longitude, latitude):
        x = abs(int((longitude - self.dsi.origin_data.x) * (self.dsi.longitude_lines_count)))
        y = abs(int((latitude - self.dsi.origin_data.y) * (self.dsi.latitude_lines_count)))
        
        return self.elevetion_map[y, x]