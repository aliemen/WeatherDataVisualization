import sys
from gui_output_file import Ui_MainWindow
from datetime import datetime
import os, subprocess # correct link-opening


### Just for reference in Ui_MainWindow (redundant import) ###
from PyQt5 import QtCore, QtGui, QtWidgets

### files for usage ###
from backend_files.weather_wrapper import weather_wrapper as ww
from backend_files.weather_plot_main import plot_oneAxis, plot_twinAxis



def open_link(link: str):
    if sys.platform=='win32':
        os.startfile(link)
    elif sys.platform=='darwin':
        subprocess.Popen(['open', link])

def conv_to_datetime(time: QtCore.QDateTime):
    return time.toPyDateTime()

def conv_to_qttime(time: datetime):
    secs_since_epoch = int(time.timestamp())
    return QtCore.QDateTime.fromSecsSinceEpoch(secs_since_epoch)

def clear_view(list_view_object: QtWidgets.QListView):
    used_model = list_view_object.model()
    if used_model is None: return # Liste ist leer/noch nicht initialisiert
    used_model.clear()

def get_std_item(label_text: str):
    tmp_item = QtGui.QStandardItem(label_text)
    tmp_item.setCheckState(QtCore.Qt.Unchecked) # Damit man es zusätzlich ankreuzen kann!
    tmp_item.setCheckable(True)
    tmp_item.setEditable(False)
    return tmp_item

def get_view_selection_strings(list_view: QtWidgets.QListView):
    model = list_view.model()
    
    selected_interp = []
    for index in range(model.rowCount()):
        tmp_model_index = model.index(index, 0) # column no 0
        tmp_item = model.itemFromIndex(tmp_model_index)
        
        # soll interpoliert werden...
        if tmp_item.checkState() == QtCore.Qt.Checked: 
            selected_interp.append(tmp_item.text())
            
    # soll geplottet werden ...
    selected_plot = [model.itemFromIndex(model_index).text() for model_index in list_view.selectedIndexes()]
        
    return selected_plot, selected_interp # zu plotten, Ausgleichsgerade zu erstellen




class gui_class(QtWidgets.QMainWindow):
    def __init__(self):
        ### initial setup ###
        super(gui_class, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        ### own setup ###
        self.setup_actions()
        self.folder_path = "" # No folder yet selected        
        
    def setup_actions(self):
        ### buttons and stuff ###
        self.ui.buttonLoadFolder.clicked.connect(self.buttonLoadFolder) # connect button clicked with action
        self.ui.buttonCreatePlot.clicked.connect(self.buttonCreatePlot) 
        self.ui.checkBoxSecAxis.clicked.connect(self.checkBoxSecAxis)
        
        ### menubar ###
        self.ui.actionBeenden.triggered.connect(self.closeEvent)
        self.ui.actionLink_zu_GitHub.triggered.connect(self.linkZuGithub)
        self.ui.action_ber.triggered.connect(self.action_ueber)
        self.ui.actionZeitachsen_Beschriftung.triggered.connect(self.actionZeitachsen_Beschriftung)
        
        ### context-menus ###
        self.ui.labelFolder.customContextMenuRequested.connect(self.labelFolder_contextMenu)
        
        ### other status-settings ###
        self.ui.labelPlotSecAxis.setVisible(False)
        self.ui.listViewSecYAxis.setVisible(False)
 
        
        
        
    ### --- buttons and stuff --- ###    
    def buttonLoadFolder(self):
        clear_view(self.ui.listViewYAxis) # clear to prevent double-saves
        clear_view(self.ui.listViewSecYAxis)
        
        self.folder_path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Wähle Ordner der Wetterdateien') # Select weather-files folder
        
        self.ui.labelFolder.setText(self.folder_path)
        self.ui.labelFolder.setToolTip("Ausgewählter Ordner: " + str(self.folder_path))
        
        self.data_object = ww(directory=self.folder_path)
        
        # automatically set "time boundaries" of loaded files
        earliest_time = self.data_object[0]["Time"]
        latest_time = self.data_object[-1]["Time"]
        self.ui.dateTimeStart.setDateTime(earliest_time)
        self.ui.dateTimeEnd.setDateTime(latest_time)
        
        possible_labels = self.data_object.get_possible_labels()
        
        item_model = QtGui.QStandardItemModel() # Model that gets added to listviews (both share the same model...)
        item_model_secAxis = QtGui.QStandardItemModel() # Model that gets added to listviews (both share the same model...)
        for label in possible_labels:
            item_model.appendRow(get_std_item(label))
            item_model_secAxis.appendRow(get_std_item(label))
            
        self.ui.listViewYAxis.setModel(item_model)
        self.ui.listViewSecYAxis.setModel(item_model_secAxis)
        
        self.message_box("Daten wurden erfolgreich eingelesen!\nEin weiteres Einlesen überschreibt intern die alten Daten.", "Information")

    def checkBoxSecAxis(self):        
        if self.ui.checkBoxSecAxis.isChecked():
            self.ui.labelPlotSecAxis.setVisible(True)
            self.ui.listViewSecYAxis.setVisible(True)
        else:
            self.ui.labelPlotSecAxis.setVisible(False)
            self.ui.listViewSecYAxis.setVisible(False)
            

    def buttonCreatePlot(self):
        if self.folder_path == "":
            self.message_box("Es wurden noch keine Wetterdaten eingelesen!", "Achtung", icon=QtWidgets.QMessageBox.Warning)
            return
        
        plot_start_datetime = conv_to_datetime(self.ui.dateTimeStart.dateTime())
        plot_end_datetime = conv_to_datetime(self.ui.dateTimeEnd.dateTime())
        
        if plot_start_datetime > plot_end_datetime:
            self.message_box("Die Startzeit muss vor der Endzeit liegen!", "Achtung", icon=QtWidgets.QMessageBox.Warning)
            return
        
        plotting_time_format = str(self.ui.lineEditTimeFormat.text())
        
        YAxis_labels_plot, YAxis_labels_interp = get_view_selection_strings(self.ui.listViewYAxis)
        secYAxis_labels_plot, secYAxis_labels_interp = get_view_selection_strings(self.ui.listViewSecYAxis)
        
        YAxis_keys_plot = self.data_object.get_keys_from_labels(YAxis_labels_plot)
        YAxis_keys_interp = self.data_object.get_keys_from_labels(YAxis_labels_interp)
        
        secYAxis_keys_plot = self.data_object.get_keys_from_labels(secYAxis_labels_plot)
        secYAxis_keys_interp = self.data_object.get_keys_from_labels(secYAxis_labels_interp)
        
        sec_axis = self.ui.checkBoxSecAxis.isChecked()
        interpolation_degree = self.ui.spinBoxInterpDegree.value()
        
        if sec_axis:
            if len(YAxis_keys_plot)+len(YAxis_keys_interp) == 0 or len(secYAxis_keys_plot)+len(secYAxis_keys_interp) == 0:
                self.message_box("Auf beiden Achsen muss mindestens ein Wert ausgewählt werden!", "Achtung")
                return
            print("Plotting on two axis...")
            plot_twinAxis(self.data_object, plotting_time_format, [plot_start_datetime, plot_end_datetime],
                          YAxis_keys_plot, secYAxis_keys_plot, YAxis_keys_interp, secYAxis_keys_interp, interpolation_degree=interpolation_degree)
        else:
            if len(YAxis_keys_plot)+len(YAxis_keys_interp) == 0:
                self.message_box("Es muss mindestens ein Wert ausgewählt werden!", "Achtung")
                return
            print("Plotting on one axis...")
            plot_oneAxis(self.data_object, plotting_time_format, [plot_start_datetime, plot_end_datetime], YAxis_keys_plot,
                         YAxis_keys_interp, interpolation_degree=interpolation_degree)
            
        print("Plot erfolgreich durchgeführt...")
    
    
    
    ### --- menubar --- ###
    def closeEvent(self, event):
        print ("User has clicked the close on the main window")        
        self.close() # Close opened window
        app.quit() # End loaded "python instance..."
    
    def linkZuGithub(self, event):
        link_zu_github = "https://github.com/aliemen/WeatherDataVisualization"
        open_link(link_zu_github)
            
    def action_ueber(self, event):
        ueber_string = "<html><body>" \
                + "<h3>Contact</h3>" \
                + "<p>Name: Alexander Liemen<br />E-Mail: <a href=\"mailto:alexander@a-liemen.de\">alexander@a-liemen.de</a><br />Code on GitHub: <a href=\"https://github.com/aliemen/WeatherDataVisualization\">https://github.com/aliemen/WeatherDataVisualization</a></p>" \
                + "<h3>Informations</h3>" \
                + "<p>\"Weather Data Visualization\" is a Python program for convenient loading and visualization of \"EasyWeather\" exports. Visualization is done using the <em>matplotlib.pyplot</em> library, the GUI is written in <em>PyQt5</em> with QtDesigner. " \
                    + "For any questions please contact the given email address or visit the GitHub page of the project.<br /><strong>Note</strong>: This is just a small project to simplify the handling and backup of my weather station. An active support or further " \
                    + "development of the program is therefore not guaranteed.<br />Nevertheless, I am of course grateful for any feedback/suggestions via the GitHub page.</p>" \
                + "</body></html>"
        self.message_box(ueber_string, "Über das Programm...")
        
    def actionZeitachsen_Beschriftung(self, event):
        link_strftime_cheatsheet = "https://strftime.org/"
        open_link(link_strftime_cheatsheet)
    
    
    ### --- context-menus --- ###
    def labelFolder_contextMenu(self, event_position):
        child = self.childAt(self.sender().mapTo(self, event_position))
        context_menu = QtWidgets.QMenu(self)
        reset_action = context_menu.addAction("Reset data")
        action = context_menu.exec_(child.mapToGlobal(event_position))
        
        if action == reset_action:
            self.folder_path = ""
            self.ui.labelFolder.setText("--- noch kein Ordner ausgewählt ---")
            self.ui.labelFolder.setToolTip("Ordner mit allen einzulesenden Dateien der Wetterdaten")
            del self.data_object # should be fine...
            
            self.ui.dateTimeStart.setDateTime(standard_time)
            self.ui.dateTimeEnd.setDateTime(standard_time)
            
            clear_view(self.ui.listViewYAxis)
            clear_view(self.ui.listViewSecYAxis)
            
            print("Geladene Wetterdateien wurden entfernt!")
            
  
    
  
    
    ### --- helper-functions --- ###
    def message_box(self, message: str, title: str, icon=QtWidgets.QMessageBox.Information):
        msgBox = QtWidgets.QMessageBox(icon, title, message)
        msgBox.exec()
    
    
    
    

if __name__ == "__main__":
    standard_time = datetime(2000, 1, 1)
    
    app = QtWidgets.QApplication(sys.argv)

    myapp = gui_class()
    myapp.show()
    
    sys.exit(app.exec_())
    
    
    
    
    
    
    
    
    
    
    