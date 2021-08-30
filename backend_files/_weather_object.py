
from datetime import datetime

class weather_object(object):
    
    _data_names = ["No",
                   "Time",
                   "MeasureInterval",
                   "HumidityInside",
                   "TemperatureInside",
                   "HumidityOutside",
                   "TemperatureOutside",
                   "PressureAbsolute",
                   "WindSpeed",
                   "WindGustSpeed",
                   "WindDirection",
                   "PressureRelative",
                   "DewPoint",
                   "WindChill",
                   "RainfallHourly",
                   "RainfallDaily",
                   "RainfallWeekly",
                   "RainfallMonthly",
                   "RainfallTotal",
                   "WindLevel",
                   "WindGustLevel"]
    
    def get_instance(self, value_name):
        datetime_value = ["Time"]
        string_value = ["WindDirection"]
        int_value = ["No"]
        # Otherwise, convert to float!
        
        if value_name in string_value:
            return str
        if value_name in int_value:
            return int
        if value_name in datetime_value:
            return lambda time_str: datetime.strptime(time_str, self._time_format)
        
        return float
            
            
    
    def __init__(self, data_string, separator=";", data_names=None, no_value_key="---", time_format=None):
        # structure:    No;Zeit;Intervall(mi);innen Luftfeuchtigkeit(%);innen Temperatur(°C);
        #               außen Luftfeuchtigkeit(%);außen Temperatur(°C);absolut Luftdruck(Hpa);
        #               Wind(m/s);Windbö"(m/s);Richtung;relative Luftdruck(Hpa);Taupunkt(°C);
        #               Windauskühlung(°C);Stunde Niederschlag(mm);24 Stunde Niederschlag(mm);
        #               Woche Niederschlag(mm);Monat Niederschlag(mm);Total Niederschlag(mm);
        #               Wind Level(bft);Windbö Level(bft)
        # sample: 1;11-03-2019 11:31;63;46;19.1;98;1.1;987.5;2.0;3.1;NW;1013.5;0.8;-0.5;0.0;0.0;0.0;0.0;0.0;2;2
        
        assert isinstance(data_string, str), "data_string must be of type string"
        
        if time_format==None:
            self._time_format = "%d-%m-%Y %H:%M"
        else:
            self._time_format = time_format
        if not data_names==None: self._data_names = data_names
        self._separator = separator
        self._no_value_key = no_value_key
        self._data_points = {} # Do NOT declare it outside of __init__ --> will be a "instance type"
        
        tmp_data_string = data_string.split(self._separator)
        
        ### Import Parameters... ###
        for index, value in enumerate(self._data_names):
            
            index_data = tmp_data_string[index]
            
            if index_data == self._no_value_key:
                self._data_points[value] = None
            else:
                convert_to_instance = self.get_instance(value)
                #print(index_data)
                #if index_data == None: print(data_names)
                #if index_data==None: print(tmp_data_string)
                
                self._data_points[value] = convert_to_instance(index_data)
        ### -------------------- ###
        
    
    def copy(self):
        data_str = self.__repr__()
        new_wo = weather_object(data_str, separator=self._separator,
                                data_names=self._data_names.copy(), no_value_key=self._no_value_key,
                                time_format=self._time_format)
        return new_wo
    
        
    def __getitem__(self, key):
        assert key in self._data_names, "keyword must be a valid data-name-entry"
        return self._data_points[key]
    
    def __str__(self):
        return str(self._data_points)
    
    def __repr__(self):
        return_string = ""
        
        for value in self._data_names:
            object_value = self._data_points[value]
            
            if isinstance(object_value, datetime):
                return_string += str(object_value.strftime(self._time_format)) + self._separator
                continue
            
            object_value = str(object_value)
            if object_value == "None": object_value = self._no_value_key
            return_string += object_value + self._separator
            
        return return_string[:-1]
    
    
    
    ### operator overwritings ###
    
    def _check_input(self, other):
        compare_time = other
        if isinstance(other, weather_object):
            compare_time = other._data_points["Time"]  
        assert isinstance(compare_time, datetime), "comparison must be instance of datetime or weather_object"
        return compare_time
    
    def __le__(self, other):
        return self._data_points["Time"] <= self._check_input(other)
    
    def __gt__(self, other):
        return self._data_points["Time"] > self._check_input(other)
    
    def __lt__(self, other):
        return self._data_points["Time"] < self._check_input(other)
        
    def __eq__(self, other):
        return self._data_points["Time"] == self._check_input(other)
    
    def __ne__(self, other):
        return self._data_points["Time"] != self._check_input(other)
    
    def __ge__(self, other):
        return self._data_points["Time"] >= self._check_input(other)
        
        
        
        
        
    
    
    