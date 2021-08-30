import numpy as np
from datetime import datetime
import random

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.dates import DateFormatter

### imports for usage ###
from backend_files.weather_wrapper import weather_wrapper as ww
from backend_files.weather_wrapper import do_polyval



def _get_yString(labels: list):
    assert len(labels) > 0, "Plotted values must be more than zero!"
    if len(labels) == 1: return labels[0]
    
    ret_string = ""
    for label in labels:
        ret_string += label + "/"
    
    return ret_string[:-1]

def _get_usable_colors():
    base_color_keys = list(mcolors.BASE_COLORS.keys())
    tableau_color_keys = list(mcolors.TABLEAU_COLORS.keys())
    css_color_keys = list(mcolors.CSS4_COLORS.keys())
    
    random.shuffle(css_color_keys) # to ensure not to close lying colors
    
    return base_color_keys + tableau_color_keys + css_color_keys
    

def plot_oneAxis(data_object: ww, plotting_time_format: str, time_range: list, plotting_values: list):
    '''
    Parameters
    ----------
    data_object : ww
        Contains all data from loaded weather-files.
    plotting_time_format : str
        String-Format for x-axis time-plot.
    time_range : list
        Contains two elements with from type "datetime" [plot_start, plot_end].
    plotting_values : list
        A list with every key-word that needs to be plotted on the y-axis.
        
    '''
    
    subs_data, labels = data_object.subscript_data(["Time"] + plotting_values,
                                                   start_date=time_range[0], end_date=time_range[1])
    
    fig, ax = plt.subplots()
    ax.set_title("Zusammenstellung Wetterdaten")
    
    ax.set_xlabel(labels[0]) # Standard: contains "Time" at labels[0] / subs_data[0]
    ax.set_ylabel(_get_yString(labels[1:]))
    
    for i in range(1, subs_data.shape[1]):
        ax.plot(subs_data[:,0], subs_data[:,i], label=labels[i])
    
    ax.legend(loc="best")
    
    ### Format x-axis as "time"
    myFmt = DateFormatter(plotting_time_format)
    ax.xaxis.set_major_formatter(myFmt)
    fig.autofmt_xdate() ## Rotate date labels automatically
    
    ax.grid(True)
    plt.show()
    
    

def plot_twinAxis(data_object: ww, plotting_time_format: str, time_range: list, plotting_YValues: list, plotting_secYValues: list):
    subs_dataY, labelsY = data_object.subscript_data(["Time"] + plotting_YValues,
                                                     start_date=time_range[0], end_date=time_range[1])
    subs_dataSecY, labelsSecY = data_object.subscript_data(["Time"] + plotting_secYValues,
                                                           start_date=time_range[0], end_date=time_range[1])
    
    usable_color = _get_usable_colors() # to ensure different colors for every line
    color_iterator = 0
    
    fig, ax = plt.subplots()
    ax.set_title("Zusammenstellung Wetterdaten")
    
    ax.set_xlabel(labelsY[0]) # Standard: contains "Time" at labels[0] / subs_data[0]
    ax.set_ylabel(_get_yString(labelsY[1:]))
    
    plot_objects_Y = []
    for i in range(1, subs_dataY.shape[1]):
        plot_objects_Y.append(ax.plot(subs_dataY[:,0], subs_dataY[:,i], label=labelsY[i], c=usable_color[color_iterator])[0])
        color_iterator += 1
    
    
    ### secondary axis ###
    ax2 = ax.twinx()
    
    ax2.set_ylabel(_get_yString(labelsSecY[1:]))
    plot_objects_SecY = []
    for i in range(1, subs_dataSecY.shape[1]):
        plot_objects_SecY.append(ax2.plot(subs_dataSecY[:,0], subs_dataSecY[:,i], label=labelsSecY[i], c=usable_color[color_iterator])[0])
        color_iterator += 1
    

    ### Get Labels     
    lns = plot_objects_Y + plot_objects_SecY # added every line together
    labs = [l.get_label() for l in lns]
    ax.legend(lns, labs, loc="best")
    
    ### Format x-axis as "time"
    myFmt = DateFormatter(plotting_time_format)
    ax.xaxis.set_major_formatter(myFmt)
    fig.autofmt_xdate() ## Rotate date labels automatically
    
    ax.grid(True)
    plt.show()


    





'''

### own testing... ###

def plot_test():
    plotting_time_format = "%d.%m.%Y"
    as_date = lambda time_str: datetime.strptime(time_str, plotting_time_format)
    time_range = ["09.05.2000",
                  "09.06.2030"]
    #time_range = ["20.07.2019",
    #              "29.07.2019"]
    
    data_object = ww(directory="weather_files/")
    test, labels = data_object.subscript_data(["Time", "TemperatureOutside", "TemperatureInside"], include_labeling=True,
                                              start_date=as_date(time_range[0]), end_date=as_date(time_range[1]))
    
    
    fig, ax = plt.subplots()
    ax.set_title("Zusammenstellung Wetterdaten")
    ax.set_xlabel("Zeit")
    
    ax.set_ylabel(labels[1])
    plot1 = ax.plot(test[:,0], test[:,1], label=labels[1], c="blue")
    
    #plot1_fit = do_polyval(test[:,0], test[:,1], degree=3) # Uebergebe die ersten beiden Indizes (Zeit, Temperatur draussen)
    #ax.plot(test[:,0], plot1_fit, c="red", zorder=12)
    
    ax2 = ax.twinx()
    #ax2 = ax
    
    ax2.set_ylabel(labels[2])
    plot2 = ax2.plot(test[:,0], test[:,2], label=labels[2], c="orange")
    
    ### Get Labels     
    lns = plot1+plot2 # added these three lines
    labs = [l.get_label() for l in lns]
    ax.legend(lns, labs, loc="best")
    
    ### Format xaxis as "time"
    myFmt = DateFormatter("%d.%m.%y")
    ax.xaxis.set_major_formatter(myFmt)
    fig.autofmt_xdate() ## Rotate date labels automatically
    
    ax.grid(True)
    plt.show()


    
    
    
def main():
    #global data_object
    data_object = ww(directory="weather_files/")
    
    #print(data_object._data[-1])
    
    #print(data_object._data[-1])
    
    test, labels = data_object.subscript_data(["Time", "TemperatureOutside"], include_labeling=True)
    
    
    plt.figure()
    #plt.plot(test[:,0], label=labels[0])
    plt.plot(test[:,1], label=labels[1])
    #plt.plot(test[:,1], label=labels[1])
    
    plt.grid(True)
    plt.legend(loc="best")
    plt.title("Test")
    plt.show()
    
    #file_names = get_file_names()
    #data = import_data(file_names)
    
    #print(data)
    pass
    
if __name__=="__main__":
    #main()
    plot_test()
    
'''