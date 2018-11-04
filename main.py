from __future__ import unicode_literals
import sys
import os
import random
import matplotlib
# Make sure that we are using QT5
matplotlib.use('Qt5Agg')
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import Qt

from numpy import arange, sin, pi, linspace
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

progname = os.path.basename("Lissajous")
progversion = "0.1"

class LabeledInputLine(QtWidgets.QWidget):
    def __init__(self, label_name, parent = None):
        QtWidgets.QWidget.__init__(self)
        layout = QtWidgets.QHBoxLayout(self)
        self.label = QtWidgets.QLabel(self)
        self.label.setText(label_name)
        self.edit = QtWidgets.QLineEdit(self)
        layout.addWidget(self.label)
        layout.addWidget(self.edit)


class InputWidget(QtWidgets.QWidget):
    valueChanged = QtCore.Signal(int)
    def __init__(self, label_name, slider_minimum, slider_maximum, default_value = 0, parent = None):
        QtWidgets.QWidget.__init__(self)
        layout = QtWidgets.QVBoxLayout(self)

        self.input_line = LabeledInputLine(label_name, self)
        layout.addWidget(self.input_line)

        self.slider = QtWidgets.QSlider(Qt.Horizontal)
        self.slider.setTickInterval(1)
        self.slider.setSingleStep(1)
        self.slider.setMinimum(slider_minimum)
        self.slider.setMaximum(slider_maximum)
        self.input_line.edit.textChanged.connect(self.line_edit_changed)
        self.slider.valueChanged.connect(self.slider_changed)
        layout.addWidget(self.slider)

        self.slider.setValue(default_value)
        self.input_line.edit.setText(str(default_value))

    def slider_changed(self, new_value):
        self.input_line.edit.setText(str(new_value))
        self.valueChanged.emit(new_value)

    def line_edit_changed(self, new_value):
        if new_value is None or new_value is '':
            new_value = 0
        new_value = float(new_value)
        self.slider.setValue(new_value)
        self.valueChanged.emit(new_value)

class Options(QtWidgets.QWidget):
    def __init__(self, parent = None):
        QtWidgets.QWidget.__init__(self)
        l = QtWidgets.QVBoxLayout(self)
        self.delta_widget = InputWidget("Delta", 0, 360, 0, self)
        l.addWidget(self.delta_widget)
        self.a_widget = InputWidget("a", -10, 10, 1, self)
        l.addWidget(self.a_widget)
        self.b_widget = InputWidget("b", -10, 10, 1, self)
        l.addWidget(self.b_widget)
        self.A_widget = InputWidget("A", -10, 10, 1, self)
        l.addWidget(self.A_widget)
        self.B_widget = InputWidget("B", -10, 10, 1, self)
        l.addWidget(self.B_widget)

    def add_new_delta_handler(self, new_delta_handler):
        self.delta_widget.valueChanged.connect(new_delta_handler)

    def add_new_a_handler(self, new_a_handler):
        self.a_widget.valueChanged.connect(new_a_handler)

    def add_new_b_handler(self, new_b_handler):
        self.b_widget.valueChanged.connect(new_b_handler)

    def add_new_A_handler(self, new_A_handler):
        self.A_widget.valueChanged.connect(new_A_handler)

    def add_new_B_handler(self, new_B_handler):
        self.B_widget.valueChanged.connect(new_B_handler)

class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)

        self.compute_initial_figure()

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass


class MyDynamicMplCanvas(MyMplCanvas):
    """A canvas that updates itself every second with a new plot."""

    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
        self.a = 1 # plotting the curves for
        self.b = 1 # different values of a/b
        self.A = 1
        self.B = 1
        self.delta = pi / 2;
        self.t = linspace(-pi, pi, 360)

    def compute_initial_figure(self):
        x = sin(linspace(-pi, pi, 360))
        y = sin(linspace(-pi, pi, 360))
        self.axes.plot(x, y, 'g')

    def update_figure(self):
        x = self.A * sin(self.a * self.t + self.delta)
        y = self.B * sin(self.b * self.t)
        self.axes.cla()
        self.axes.plot(x, y, 'g')
        self.draw()

    def update_delta(self, new_delta):
        self.delta = new_delta
        self.update_figure()

    def update_a(self, new_a):
        self.a = new_a
        self.update_figure()

    def update_b(self, new_b):
        self.b = new_b
        self.update_figure()

    def update_A(self, new_A):
        self.A = new_A
        self.update_figure()

    def update_B(self, new_B):
        self.B = new_B
        self.update_figure()

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("application main window")

        self.file_menu = QtWidgets.QMenu('&File', self)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        self.help_menu = QtWidgets.QMenu('&Help', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)

        self.help_menu.addAction('&About', self.about)

        self.main_widget = QtWidgets.QWidget(self)

        l = QtWidgets.QHBoxLayout(self.main_widget)
        dc = MyDynamicMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        options = Options(dc)
        options.add_new_delta_handler(dc.update_delta)
        options.add_new_a_handler(dc.update_a)
        options.add_new_b_handler(dc.update_b)
        options.add_new_A_handler(dc.update_A)
        options.add_new_B_handler(dc.update_B)
        l.addWidget(dc)
        l.addWidget(options)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        self.statusBar().showMessage("Lissajous curves visualization", 2000)

    def delta_slider_changed(self, delta):
        self.update_text_delta(delta)
        self.update_display_delta(delta)

    def delta_line_edit_changed(self, delta):
        if delta is None or delta is '':
            delta = 0
        delta = float(delta)
        while (delta > 360):
            delta -= 360
        while (delta < 0):
            delta += 360
        self.update_slider_delta(delta)
        self.update_display_delta(delta)

    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()

    def about(self):
        QtWidgets.QMessageBox.about(self, "About",
                                    """Lissajous figures visualization
Based on an example on how to embed matplotlib into a Python Qt Application \
embedding_in_qt5.py by Florent Rougon, Darren Dale and Jenes H Nielsen""")


qApp = QtWidgets.QApplication(sys.argv)

aw = ApplicationWindow()
aw.setWindowTitle("%s" % progname)
aw.show()
sys.exit(qApp.exec_())
#qApp.exec_()
