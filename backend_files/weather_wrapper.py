#from _weather_object import weather_object as wo
from backend_files._weather_object import weather_object as wo
from os import walk
from numpy import array, sort, unique
from datetime import datetime


class weather_wrapper(object):
    
    _default_names = {"No": "Nummer",
                     "Time": "Zeit",
                     "MeasureInterval": "Messintervall",
                     "HumidityInside": "Luftfeuchtigkeit innen",
                     "TemperatureInside": "Temperatur innen",
                     "HumidityOutside": "Luftfeuchtigkeit aussen",
                     "TemperatureOutside": "Temperatur aussen",
                     "PressureAbsolute": "Absoluter Luftdruck",
                     "WindSpeed": "Windgeschwindigkeit",
                     "WindGustSpeed": "Windböengeschwindigkeit",
                     "WindDirection": "Windrichtung",
                     "PressureRelative": "Relativer Luftdruck",
                     "DewPoint": "Taupunkt",
                     "WindChill": "Windauskühlung",
                     "RainfallHourly": "Stündlicher Regenfall",
                     "RainfallDaily": "Täglicher Regenfall",
                     "RainfallWeekly": "Wöchentlicher Regenfall",
                     "RainfallMonthly": "Monatlicher Regenfall",
                     "RainfallTotal": "Gesamter Regenfall",
                     "WindLevel": "Windlevel",
                     "WindGustLevel": "Windböenlevel"}
    
    def _get_data(self, file_endings, separator, directory, data_names, time_format):
        file_names = self._get_file_names(file_endings, directory)
        
        tmp_data = []
        
        for filename in file_names:
            with open(directory + filename) as file:
                lines = [line.rstrip() for line in file]
                for i, line in enumerate(lines):
                    if i == 0:
                        continue
                    
                    tmp_object = wo(line, separator, data_names, time_format=time_format)
                    tmp_data.append(tmp_object)
                    
        return array(tmp_data)
    
    
    
    def __init__(self, file_endings=[".txt", ".csv"], separator=";", directory="weather_files/", data_names=None,
                 time_format=None, sort_elements=True, remove_duplicates=True):
        
        if not directory.endswith("/"): directory += "/"
        
        self._data = self._get_data(file_endings, separator, directory, data_names, time_format)
        if remove_duplicates: 
            assert sort_elements, "if duplicates should get removed, array must be sorted"
            self._data = unique(self._data)
        else:
            if sort_elements: self._data = sort(self._data) # sorts through implemented-overwritten comparison methods
    
    ### ---- Public Methods ----- ###
    
    def size(self):
        return len(self._data)
    
    def subscript_data(self, index_strings, start_date=datetime(2000, 1, 1), end_date=datetime(3000, 12, 31), include_labeling=True):
        
        start_index, stop_index = self._get_indizes(start_date, end_date)
        
        return_array = []
        for i in range(start_index, stop_index):
            tmp_data_entries = [self._data[i][key] for key in index_strings]
            return_array.append(tmp_data_entries)
            
        if include_labeling:
            return array(return_array), self._get_labels(index_strings)
        else:
            return array(return_array)
        
    def get_possible_labels(self, time_key="Time"):
        indizes = self._data[0]._data_names.copy() # choose one shared representative "label-array"
        if time_key in indizes: indizes.remove(time_key)
        
        return self._get_labels(indizes)
    
    def get_keys_from_labels(self, labels):
        def key_from_value(tmp_dict, value):
            keys = tmp_dict.keys()
            for key in keys:
                if tmp_dict[key] == value:
                    return key
            return value
        
        ret_keys = []
        for label in labels:
            ret_keys.append(key_from_value(self._default_names, label))
        
        return ret_keys
                
        
        

    
    
    ### ---- Helper Methods ----- ###
    
    def _get_labels(self, index_strings):
        
        return_labels = []
        for label in index_strings:
            if label in self._default_names:
                return_labels.append(self._default_names[label])
            else:
                return_labels.append(label)
                
        return return_labels
    
    def _get_indizes(self, start_date, end_date):
        assert start_date < end_date, "starting date must be before ending date"
        
        ret_start = 0
        ret_stop = self._data.size
        
        for i in range(ret_stop):
            if self._data[i] > start_date:
                ret_start = i
                break
        for i in range(ret_start, ret_stop):
            if self._data[i] > end_date:
                ret_stop = i
                break
            
        return ret_start, ret_stop
    
    def _ends_with(self, name_str, name_array):
        for name in name_array:
            if name_str.endswith(name):
                return True
        return False
    
    def _get_file_names(self, file_endings, directory):
        directory_structure = next(walk(directory), (None, None, []))[2]  # [] if no file
        file_names = []
        for tmp_filename in directory_structure:
            if self._ends_with(tmp_filename, file_endings): file_names.append(str(tmp_filename))
        return file_names
    
    def __getitem__(self, key):
        #assert isinstance(key, ), "keyword must be a valid data-name-entry"
        return self._data[key]
    
    
    

### Sonstige Methoden zur Datenverarbeitung ###
from numpy import polyval, polyfit

def do_polyval(times, data, degree=1): # übergebe auf erster Achse die Zeitobjekte, auf der zweiten die zu fittenden Daten

    starting_time = times[0]
    seconds_per_day = 86400
    
    time_as_timestamp = array([(times[i]-starting_time).total_seconds() / seconds_per_day for i in range(times.shape[0])], dtype="float")
    data = array(data, dtype="float")
    
    fit_constants = polyfit(time_as_timestamp, data, degree)
    ret_eval = polyval(fit_constants, time_as_timestamp)
    
    return ret_eval
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    