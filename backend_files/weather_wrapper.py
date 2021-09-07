from backend_files._weather_object import weather_object as wo
from os import walk
from datetime import datetime

from numpy import array, sort, unique
from numpy import polyval, polyfit, isfinite, flip # für "Sonstiges"


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
                one_file_data = []
                
                for i, line in enumerate(lines):
                    if i == 0:
                        first_line = line
                        continue
                    if line in ["", "\x00", " "]: # line is empty...
                        continue
                    
                    tmp_object = wo(line, separator, data_names, time_format=time_format)
                    one_file_data.append(tmp_object)
                
                one_file_data = convert_to_std_units(one_file_data, first_line, separator=separator) # ex: km/h should be converted to m/s
                tmp_data += one_file_data
                    
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
    
    def subscript_data(self, index_strings, start_date=datetime(2000, 1, 1), end_date=datetime(3000, 12, 31),
                       include_labeling=True, for_interpolation=False):
        
        start_index, stop_index = self._get_indizes(start_date, end_date)
        
        return_array = []
        for i in range(start_index, stop_index):
            tmp_data_entries = [self._data[i][key] for key in index_strings]
            return_array.append(tmp_data_entries)
            
        if include_labeling:
            return array(return_array), self._get_labels(index_strings, for_interpolation=for_interpolation)
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
            #if for_interp:
                #ret_keys.append("Ausgleichspolynom: " + key_from_value(self._default_names, label))
            #else:
            ret_keys.append(key_from_value(self._default_names, label))
        
        return ret_keys
                
        
        

    
    
    ### ---- Helper Methods ----- ###
    
    def _get_labels(self, index_strings, for_interpolation=False):
        
        interpolation_suffix = ""
        if for_interpolation:
            interpolation_suffix = "Ausgleichspolynom: "
        
        return_labels = []
        for label in index_strings:
            if label in self._default_names:
                return_labels.append(interpolation_suffix + self._default_names[label])
            else:
                return_labels.append(interpolation_suffix + label)
                
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

def remove_indizes_from_list(value_list: list, rm_list):
    
    value_list = array(value_list).tolist()
    
    reversed_sorted_indizes = flip(sort(rm_list))
    for index in reversed_sorted_indizes:
        value_list.pop(index)
        
    return array(value_list)
    
def clear_nan_values(x_data, y_data):
    # clears nan values in y_data
    
    nan_indizes = []
    tmp_ar = array(y_data.copy(), dtype=float)
    
    for i in range(tmp_ar.shape[0]):
        if not isfinite([tmp_ar[i]]):
            nan_indizes.append(i)
            
    return remove_indizes_from_list(x_data, nan_indizes), remove_indizes_from_list(y_data, nan_indizes)
    

def do_polyval(times: list, data: list, degree=1): # übergebe auf erster Achse die Zeitobjekte, auf der zweiten die zu fittenden Daten

    starting_time = times[0]
    seconds_per_day = 86400
    
    times, data = clear_nan_values(times, data)
    
    time_as_timestamp = array([(times[i]-starting_time).total_seconds() / seconds_per_day for i in range(times.shape[0])], dtype="float")
    data = array(data, dtype="float")
    
    fit_constants = polyfit(time_as_timestamp, data, degree)
    ret_eval = polyval(fit_constants, time_as_timestamp)
    
    return times, ret_eval
    
    
    
    
### more helper methods ###
def get_conversion_function(current_unit: str, desired_unit: str):
    if current_unit == desired_unit:
        print("Warning: returning \"no conversion\" (should not happen normally)!")
        return lambda x: x # nothing happens (this case should not occur)
    
    if current_unit=="km/h":
        if desired_unit=="m/s":
            return lambda x: x / 3.6
    if current_unit=="m/s":
        if desired_unit=="km/h":
            return lambda x: x * 3.6
    if current_unit=="mm":
        if desired_unit=="m":
            return lambda x: x / 1000.0
    if current_unit=="m":
        if desired_unit=="mm":
            return lambda x: x * 1000.0
        
    if current_unit=="Hpa":
        if desired_unit=="hpa": # to ensure compatibility for older versions
            return lambda x: x
    
    print(f"Error: desired conversion ({current_unit}->{desired_unit}) not available, returning identity function!")
    return lambda x: x
        
def apply_function_to_all_values(values: list, value_key: str, function: callable):
    for i in range(len(values)):
        values[i]._apply_func_to_value(value_key, function)
    return values

def convert_to_std_units(values: list, first_line: str, separator=";"):
    standard_units = {"No": "No",
                      "Time": "Zeit",
                      "MeasureInterval": "mi",
                      "HumidityInside": "%",
                      "TemperatureInside": "°C",
                      "HumidityOutside": "%",
                      "TemperatureOutside": "°C",
                      "PressureAbsolute": "hpa",
                      "WindSpeed": "m/s",
                      "WindGustSpeed": "m/s",
                      "WindDirection": "Richtung",
                      "PressureRelative": "hpa",
                      "DewPoint": "°C",
                      "WindChill": "°C",
                      "RainfallHourly": "mm",
                      "RainfallDaily": "mm",
                      "RainfallWeekly": "mm",
                      "RainfallMonthly": "mm",
                      "RainfallTotal": "mm",
                      "WindLevel": "bft",
                      "WindGustLevel": "bft"}
    
    used_units = first_line.split(separator)
    for i, title in enumerate(used_units):
        if not "(" in title:
            continue
        from_index = title.rindex("(") + 1
        used_units[i] = title[from_index:-1]
    
    tmp_data_names = values[0]._data_names # to iterate through data names and find the right key
    
    for _used, value_key in zip(used_units, tmp_data_names):
        _desired = standard_units[value_key]
        if _used == _desired:
            continue
        
        conversion_function = get_conversion_function(_used, _desired)
        values = apply_function_to_all_values(values, value_key, conversion_function) # lieber doppelt gemoppelt zugewiesen...
    
    return values
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    