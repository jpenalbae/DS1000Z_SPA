#!/usr/bin/env python3

import os
import sys
import ds1000z
from PyQt6 import QtCore, QtWidgets, uic
from PyQt6.QtWidgets import QPushButton, QFileDialog
import pyqtgraph as pg

basedir = os.path.dirname(__file__)

chans = {}
markers = []
scopeAddr = None

class chanData():
    """
    A class to represent channel data.

    Attributes:
    -----------
    gw : pyqtgraph.GraphicsWindow
        The graphics window to plot the data.
    btn : QPushButton
        The button to toggle the data.
    color : str
        The color of the plotted data.
    line : pyqtgraph.PlotDataItem
        The plotted data.
    enabled : bool
        Whether the plotted data is enabled or not.
    toggled : bool
        Whether the button is toggled or not.
    button : QPushButton
        The button to toggle the plotted data.
    """

    def __init__(self, gw, btn, color):
        """
        Constructs all the necessary attributes for the chanData object.

        Parameters:
        -----------
        gw : pyqtgraph.GraphicsWindow
            The graphics window to plot the data.
        btn : QPushButton
            The button to toggle the data.
        color : str
            The color of the plotted data.
        """
        pen = pen1 = pg.mkPen(color=color)

        self.gw = gw
        self.line = gw.plot([], pen=color)
        self.gw.removeItem(self.line)
        self.enabled = False
        self.button = btn
        self.toggled = False
        self.button.clicked.connect(self.toggle)

        test = QPushButton()

    def setData(self, data):
        """
        Sets the data to be plotted.

        Parameters:
        -----------
        data : list
            The data to be plotted.
        """
        self.line.setData(data)

    def toggle(self, checked):
        """
        Toggles the plotted data.

        Parameters:
        -----------
        checked : bool
            Whether the button is checked or not.
        """
        if checked:
            self.gw.addItem(self.line)
            self.toggled = True
        else:
            self.gw.removeItem(self.line)
            self.toggled = False


class MainWindow(QtWidgets.QMainWindow):
    """
    The main window of the application.

    Attributes:
        scopeRaw (dict): A dictionary containing the raw data from the oscilloscope.
        graph (pyqtgraph.PlotWidget): The plot widget used to display the data.
        table (QtWidgets.QTableWidget): The table widget used to display the markers.
        range (pyqtgraph.LinearRegionItem): The linear region item used to select a range of data.
        markPen (pyqtgraph.mkPen): The pen used to draw the markers.
    """

    def download_scope_data(self):
        """
        Downloads the scope data from the oscilloscope and updates the graph.
        """
        if scopeAddr is None:
            print("No scope address set")
            return

        scope = ds1000z.Scope(scopeAddr)
        self.scopeRaw = scope.get_all_chans()
        del scope

        self.update_graph()

    def loadFile(self):
        """
        Loads a CSV file and updates the scopeRaw attribute with the data.
        """
        fileName, _ = QFileDialog.getOpenFileName(self,
                                                  "Open File", 
                                                  "", 
                                                  "CSV Files (*.csv)")

        if fileName:
            self.scopeRaw = {}
            for i in ["CHAN1", "CHAN2", "CHAN3", "CHAN4"]:
                self.scopeRaw[i] = []

            with open(fileName, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        line = line.split(',')

                        # skip if data is not valid (possibly header)
                        try:
                            int(float(line[0]))
                        except:
                            continue

                        try:
                            if line[1]:
                                self.scopeRaw["CHAN1"].append(int(float(line[1])))
                            if line[3]:
                                self.scopeRaw["CHAN2"].append(int(float(line[3])))
                            if line[5]:
                                self.scopeRaw["CHAN3"].append(int(float(line[5])))
                            if line[7]:
                                self.scopeRaw["CHAN4"].append(int(float(line[7])))
                        except:
                            continue

            # delete empty channels
            for i in ["CHAN1", "CHAN2", "CHAN3", "CHAN4"]:
                if len(self.scopeRaw[i]) < 1:
                    del self.scopeRaw[i]

            self.update_graph()

    def update_graph(self, start=0, end=0):
        """
        Updates the graph with the data in scopeRaw.

        Args:
            start (int): The starting index of the data to display.
            end (int): The ending index of the data to display.
        """
        for i in chans:
            chans[i].button.setEnabled(False)
            if chans[i].toggled:
                chans[i].button.toggle()

        for i in self.scopeRaw:
            if start and end:
                self.scopeRaw[i] = self.scopeRaw[i][start:end]
                chans[i].setData(self.scopeRaw[i])
            else:
                chans[i].setData(self.scopeRaw[i])
            chans[i].button.setEnabled(True)
            chans[i].button.toggle()
            chans[i].toggle(True)

        self.graph.getViewBox().enableAutoRange()
        self.graph.getViewBox().setMouseEnabled(y=False)

        self.clearMarkers()

    def rangeToggle(self, checked):
        """
        Toggles the linear region item used to select a range of data.

        Args:
            checked (bool): Whether the action is checked or not.
        """
        if checked:
            self.range = pg.LinearRegionItem()
            self.range.setRegion([0, 100])
            self.graph.addItem(self.range)
        else:
            self.graph.removeItem(self.range)
            del self.range

    def cutRange(self):
        """
        Cuts the data in scopeRaw to the selected range.
        """
        if not hasattr(self, 'range'):
            return

        if not hasattr(self, 'scopeRaw'):
            return

        region = self.range.getRegion()
        self.update_graph(int(region[0]), int(region[1]))
        self.rangeToggle(False)
        self.actionRange.setChecked(False)

    def moveMarker(self, marker):
        """
        Moves a marker to a new position.

        Args:
            marker (pyqtgraph.InfiniteLine): The marker to move.
        """
        marker.setPos(int(round(marker.getPos()[0])))

        for i in range(len(markers)):
            if markers[i]["marker"] == marker:
                # update the pos
                markers[i]["pos"] = int(round(marker.getPos()[0]))
                break

        self.update_markers()

    def removeMaker(self, marker, event):
        """
        Removes a marker from the graph.

        Args:
            marker (pyqtgraph.InfiniteLine): The marker to remove.
            event (QtCore.QEvent): The event that triggered the removal.
        """
        if not event.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier:
            event.ignore()
            return

        # find the marker
        for i in range(len(markers)):
            if markers[i]["marker"] == marker:
                # remove the marker
                del markers[i]
                break

        self.graph.removeItem(marker)
        self.update_markers()

        event.accept()

    def mouse_clicked(self, event):
        """
        Handles mouse clicks on the graph.

        Args:
            event (QtCore.QEvent): The event that triggered the click.
        """
        # Ignore if control is pressed
        if event.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier:
            event.ignore()
            return

        # ignore if not left click
        if event.button() != QtCore.Qt.MouseButton.LeftButton:
            event.ignore()
            return

        vb = self.graph.getViewBox()
        mousePoint = vb.mapSceneToView(event._scenePos)

        # Add a new marker
        marker = pg.InfiniteLine(angle=90, movable=True, pen=self.markPen)
        marker.setPos(round(mousePoint.x()))
        marker.sigPositionChangeFinished.connect(self.moveMarker)
        marker.sigClicked.connect(self.removeMaker)

        label = pg.InfLineLabel(marker, "0", fill="#FF0000", color="#000000")
        label.setMovable(True)
        label.setPosition(0.97)

        markers.append({
            "marker": marker,
            "label": label,
            "pos": round(mousePoint.x()),
            "width": 0,
            "note": ""
        })

        self.graph.addItem(marker)
        self.update_markers()

        event.accept()

    def cellChanged(self, x, y):
        """
        Handles changes to the markers table.

        Args:
            x (int): The row index of the changed cell.
            y (int): The column index of the changed cell.
        """
        if y == 1:
            markers[x]["note"] = self.table.item(x, y).text()

    def update_markers(self):
        """
        Updates the markers on the graph and in the table.
        """
        # order markers by position
        markers.sort(key=lambda x: x["pos"])

        # Update markers width with the different between the next marker
        for i in range(len(markers)):
            if i == len(markers) - 1:
                markers[i]["width"] = 0
            else:
                markers[i]["width"] = markers[i+1]["pos"] - markers[i]["pos"]

            markers[i]["label"].setText(str(i+1))

        # Update the table
        self.table.clearContents()
        self.table.setRowCount(len(markers))
        for i in range(len(markers)):
            self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(str(markers[i]["width"])))
            self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(markers[i]["note"]))

    def cellClicked(self, x, y):
        """
        Moves the graph view to the position of a marker.

        Args:
            x (int): The row index of the clicked cell.
            y (int): The column index of the clicked cell.
        """
        # move the graph view to the marker pos
        self.graph.getViewBox().setXRange(markers[x]["pos"] - 100, markers[x]["pos"] + 100, padding=0)

    def clearMarkers(self):
        """
        Clears all markers from the graph and table.
        """
        for i in range(len(markers)):
            self.graph.removeItem(markers[i]["marker"])
            self.graph.removeItem(markers[i]["label"])

        markers.clear()
        self.table.clearContents()
        self.table.setRowCount(0)

    def exportMarkers(self):
        """
        Exports the markers to a CSV file.
        """
        fileName, _ = QFileDialog.getSaveFileName(self,
                                                  "Save File", 
                                                  "", 
                                                  "CSV Files (*.csv)")

        if fileName:
            with open(fileName, 'w') as f:
                f.write("pos,width,note\n")
                for i in range(len(markers)):
                    f.write("%d,%d,%s\n" % (markers[i]["pos"],
                                            markers[i]["width"],
                                            markers[i]["note"]))


    def __init__(self, *args, **kwargs):
        """
        Initializes the main window.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)
        uic.loadUi(os.path.join(basedir, "main.ui"), self)

        # Do not allow to remove the toolbar
        self.toolBar.toggleViewAction().setEnabled(False)

        # Enable downsampling for performance (can be disabled later)
        self.graph.setDownsampling(True, True, 'peak')
        self.graph.showGrid(x=True, y=True)

        # Create the pen for markings
        self.markPen = pg.mkPen('r', width=3)

        # Intialize the channels
        chans["CHAN1"] = chanData(self.graph, self.buttonChan1, "#f8fc00")
        chans["CHAN2"] = chanData(self.graph, self.buttonChan2, "#00fcf8")
        chans["CHAN3"] = chanData(self.graph, self.buttonChan3, "#f800f8")
        chans["CHAN4"] = chanData(self.graph, self.buttonChan4, "#003870")

        self.graph.scene().sigMouseClicked.connect(self.mouse_clicked)

        # Add toolbar actions
        self.actionDownload.triggered.connect(self.download_scope_data)
        self.actionRange.triggered.connect(self.rangeToggle)
        self.actionCut.triggered.connect(self.cutRange)
        self.actionOpen.triggered.connect(self.loadFile)
        self.actionClearMarkers.triggered.connect(self.clearMarkers)
        self.actionExportMarkers.triggered.connect(self.exportMarkers)

        # Prepare table
        self.table.setRowCount(0)
        self.table.cellChanged.connect(self.cellChanged)
        self.table.cellDoubleClicked.connect(self.cellClicked)


# get first arg check for valid ipv4 address and set scopeAddr
if len(sys.argv) > 1:
    if sys.argv[1] == "-h" or len(sys.argv) > 2:
        print("Usage: python3 ds1000z_spa.py <scope address>")
        sys.exit()
    scopeAddr = sys.argv[1]

app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
