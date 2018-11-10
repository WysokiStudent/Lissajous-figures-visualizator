"""
A simple GUI application where the user can edit a displayed Lissajous courve
"""

from __future__ import unicode_literals
import sys
import os
import matplotlib
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt

from numpy import sin, pi, linspace
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

PROGRAM_NAME = os.path.basename("Lissajous")
# Make sure that we are using QT5
matplotlib.use('Qt5Agg')

class LabeledInputLine(QtWidgets.QWidget):
    """
    Takes in user input inside a textbox. Consists of a label and textbox.
    """
    def __init__(self, label_name, parent=None):
        QtWidgets.QWidget.__init__(self)
        layout = QtWidgets.QHBoxLayout(self)
        self.label = QtWidgets.QLabel(self)
        self.label.setText(label_name)
        self.edit = QtWidgets.QLineEdit(self)
        layout.addWidget(self.label)
        layout.addWidget(self.edit)


class InputWidget(QtWidgets.QWidget):
    """
    Allows the user to input values in a textbox or a select them via a  slider.
    Both the textbox and slider are synchronised to display the same value when
    it is changed.
    """
    valueChanged = QtCore.Signal(int)
    def __init__(self, label_name, slider_minimum, slider_maximum, default_value=0, parent=None):
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
        """
        Updates textbox to display new_value and emits valueChanged(new_value)
        """
        self.input_line.edit.setText(str(new_value))
        self.valueChanged.emit(new_value)

    def line_edit_changed(self, new_value):
        """
        Updates slider to display new_value if possible and emits
        valueChanged(new_value).
        """
        try:
            new_value = float(new_value)
            if new_value <= self.slider.maximum():
                self.slider.setValue(new_value)
            self.valueChanged.emit(new_value)
        except ValueError:
            pass

class Options(QtWidgets.QWidget):
    """
    A QtWidget that allows the user to set multiple values with sliders
    and textboxes. The modifiable values represent the coefficients of
    a Lissajous equation.
    """
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self)
        layout = QtWidgets.QVBoxLayout(self)
        self.lissajous_equation = QtWidgets.QLabel("x=Asin(at + delta) y=Bsin(bt)")
        layout.addWidget(self.lissajous_equation)
        self.delta_widget = InputWidget("Delta", 0, 360, 0, self)
        layout.addWidget(self.delta_widget)
        self.a_widget = InputWidget("a", -10, 10, 1, self)
        layout.addWidget(self.a_widget)
        self.b_widget = InputWidget("b", -10, 10, 1, self)
        layout.addWidget(self.b_widget)
        self.A_widget = InputWidget("A", 0, 10, 1, self)
        layout.addWidget(self.A_widget)
        self.B_widget = InputWidget("B", 0, 10, 1, self)
        layout.addWidget(self.B_widget)

    def add_new_delta_handler(self, new_delta_handler):
        """
        Connects new_delta_handler to an event wich is fired when delta changes.
        """
        self.delta_widget.valueChanged.connect(new_delta_handler)

    def add_new_a_handler(self, new_a_handler):
        """
        Connects new_a_handler to an event wich is fired when a changes.
        """
        self.a_widget.valueChanged.connect(new_a_handler)

    def add_new_b_handler(self, new_b_handler):
        """
        Connects new_b_handler to an event wich is fired when b changes.
        """
        self.b_widget.valueChanged.connect(new_b_handler)

    def add_new_A_handler(self, new_A_handler):
        """
        Connects new_A_handler to an event wich is fired when A changes.
        """
        self.A_widget.valueChanged.connect(new_A_handler)

    def add_new_B_handler(self, new_B_handler):
        """
        Connects new_B_handler to an event wich is fired when B changes.
        """
        self.B_widget.valueChanged.connect(new_B_handler)

class MatplotlibCanvas(FigureCanvas):
    """
    Abstract class for simplifing the usage of Matplotlib's canvas from Qt.
    """

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
        """
        This method should compute the initial parameters required for
        visualising a figure.
        """
        pass


class DynamicCanvas(MatplotlibCanvas):
    """
    A canvas that updates itself with a new plot when the curves parameters
    change.
    """

    def __init__(self, *args, **kwargs):
        MatplotlibCanvas.__init__(self, *args, **kwargs)
        self.a = 1
        self.b = 1
        self.A = 1
        self.B = 1
        self.delta = pi / 2
        self.t = linspace(-pi, pi, 360)

    def compute_initial_figure(self):
        """
        Computes initial Lissajous curve with delta=0, A=1, B=1, a=1 and b=1.
        """
        x = sin(linspace(-pi, pi, 360))
        y = sin(linspace(-pi, pi, 360))
        self.axes.plot(x, y, 'g')

    def update_figure(self):
        """
        Recomputes the Lissajous figure and redraws it.
        """
        x = self.A * sin(self.a * self.t + self.delta)
        y = self.B * sin(self.b * self.t)
        self.axes.cla()
        self.axes.plot(x, y, 'g')
        self.draw()

    def update_delta(self, new_delta):
        """
        Sets delta = new_delta and redraws the canvas.
        """
        self.delta = new_delta
        self.update_figure()

    def update_a(self, new_a):
        """
        Sets a = new_a and redraws the canvas.
        """
        self.a = new_a
        self.update_figure()

    def update_b(self, new_b):
        """
        Sets b = new_b and redraws the canvas.
        """
        self.b = new_b
        self.update_figure()

    def update_A(self, new_A):
        """
        Sets A = new_A and redraws the canvas.
        """
        self.A = new_A
        self.update_figure()

    def update_B(self, new_B):
        """
        Sets B = new_B and redraws the canvas.
        """
        self.B = new_B
        self.update_figure()

class ApplicationWindow(QtWidgets.QMainWindow):
    """
    The main display, inside it there is a Lissajous visualization and options
    to control it.
    """
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("application main window")

        self.file_menu = QtWidgets.QMenu('&File', self)
        self.file_menu.addAction('&Quit', self.quit_program,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        self.help_menu = QtWidgets.QMenu('&Help', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)

        self.help_menu.addAction('&About', self.about)

        self.main_widget = QtWidgets.QWidget(self)

        layout = QtWidgets.QHBoxLayout(self.main_widget)
        lissajous_canvas = DynamicCanvas(self.main_widget, width=5, height=4, dpi=100)
        options = Options(lissajous_canvas)
        options.add_new_delta_handler(lissajous_canvas.update_delta)
        options.add_new_a_handler(lissajous_canvas.update_a)
        options.add_new_b_handler(lissajous_canvas.update_b)
        options.add_new_A_handler(lissajous_canvas.update_A)
        options.add_new_B_handler(lissajous_canvas.update_B)
        layout.addWidget(lissajous_canvas)
        layout.addWidget(options)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        self.statusBar().showMessage("Lissajous curves visualization", 2000)

    def quit_program(self):
        """
        Exits program
        """
        self.close()

    def about(self):
        """
        Displays a messagebox explaining the purpose and origin of the program.
        """
        QtWidgets.QMessageBox.about(self, "About",
                                    """Lissajous figures visualization
Based on an example on how to embed matplotlib into a Python Qt Application \
embedding_in_qt5.py by Florent Rougon, Darren Dale and Jenes H Nielsen""")

def main():
    """
    Creates a windows inside which there is a grapth and a set of options to
    control the displayed Lissajous figure.
    """
    app = QtWidgets.QApplication(sys.argv)

    application_window = ApplicationWindow()
    application_window.setWindowTitle("%s" % PROGRAM_NAME)
    application_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
