import sys
from gui_output_file import Ui_MainWindow
from datetime import datetime
import os, subprocess # correct link-opening


### Just for reference in Ui_MainWindow (redundant import) ###
from PyQt5 import QtCore, QtGui, QtWidgets

### files for usage ###
from backend_files.weather_wrapper import weather_wrapper as ww
from backend_files.weather_plot_main import plot_oneAxis, plot_twinAxis




def conv_to_datetime(time: QtCore.QDateTime):
    return time.toPyDateTime()
def conv_to_qttime(time: datetime):
    secs_since_epoch = int(time.timestamp())
    return QtCore.QDateTime.fromSecsSinceEpoch(secs_since_epoch)


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
        
        ### context-menus ###
        self.ui.labelFolder.customContextMenuRequested.connect(self.labelFolder_contextMenu)
        
        ### other status-settings ###
        self.ui.labelPlotSecAxis.setVisible(False)
        self.ui.listWidgetSecYAxis.setVisible(False)
 
        
        
        
    ### --- buttons and stuff --- ###    
    def buttonLoadFolder(self):
        self.ui.listWidgetYAxis.clear() # clear to prevent double-saves
        self.ui.listWidgetSecYAxis.clear()
        
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
        for label in possible_labels:
            self.ui.listWidgetYAxis.addItem(label)
            self.ui.listWidgetSecYAxis.addItem(label)
        
        self.message_box("Daten wurden erfolgreich eingelesen!\nEin weiteres Einlesen überschreibt intern die alten Daten.", "Information")

    def checkBoxSecAxis(self):        
        if self.ui.checkBoxSecAxis.isChecked():
            self.ui.labelPlotSecAxis.setVisible(True)
            self.ui.listWidgetSecYAxis.setVisible(True)
        else:
            self.ui.labelPlotSecAxis.setVisible(False)
            self.ui.listWidgetSecYAxis.setVisible(False)
            

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
        
        YAxis_labels = [item.text() for item in self.ui.listWidgetYAxis.selectedItems()]
        YAxis_keys = self.data_object.get_keys_from_labels(YAxis_labels)
        secYAxis_labels = [item.text() for item in self.ui.listWidgetSecYAxis.selectedItems()]
        secYAxis_keys = self.data_object.get_keys_from_labels(secYAxis_labels)
        
        sec_axis = self.ui.checkBoxSecAxis.isChecked()
        
        if sec_axis:
            if len(YAxis_keys) == 0 or len(secYAxis_keys) == 0:
                self.message_box("Auf beiden Achsen muss mindestens ein Wert ausgewählt werden!", "Achtung")
                return
            print("Plotting on two axis...")
            plot_twinAxis(self.data_object, plotting_time_format, [plot_start_datetime, plot_end_datetime], YAxis_keys, secYAxis_keys)
        else:
            if len(YAxis_keys) == 0:
                self.message_box("Es muss mindestens ein Wert ausgewählt werden!", "Achtung")
                return
            print("Plotting on one axis...")
            plot_oneAxis(self.data_object, plotting_time_format, [plot_start_datetime, plot_end_datetime], YAxis_keys)
            
        print("Plot erfolgreich durchgeführt...")
    
    
    
    ### --- menubar --- ###
    def closeEvent(self, event):
        print ("User has clicked the close on the main window")        
        self.close() # Close opened window
        app.quit() # End loaded "python instance..."
    
    def linkZuGithub(self, event):
        link_zu_github = "https://github.com/aliemen/WeatherDataVisualization"
        if sys.platform=='win32':
            os.startfile(link_zu_github)
        elif sys.platform=='darwin':
            subprocess.Popen(['open', link_zu_github])
            
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
            
            self.ui.listWidgetYAxis.clear()
            self.ui.listWidgetSecYAxis.clear()
            
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
    
    
    
    
    
    
    
    
    
    
    