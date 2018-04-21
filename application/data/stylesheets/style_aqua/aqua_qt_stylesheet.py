import os
import sys  # provides interaction with the Python interpreter

from PyQt4 import QtGui  # provides the graphic elements
from PyQt4.QtCore import Qt  # provides Qt identifiers

from aqua.qsshelper import QSSHelper


class Window(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)

        # pushbutton
        self.pushbutton = QtGui.QPushButton('PushButton')

        # checkable pushbutton
        self.pushbutton_checkable = QtGui.QPushButton('PushButton (checkable)')
        self.pushbutton_checkable.setCheckable(True)
        self.pushbutton_checkable.setChecked(True)

        # radiobutton
        self.radiobutton = QtGui.QRadioButton('RadioButton')
        self.radiobutton.setChecked(True)

        # checkboxes
        self.checkbox = QtGui.QCheckBox('CheckBox')
        self.checkbox.setChecked(True)

        # tristate checkbox
        self.checkbox_tristate = QtGui.QCheckBox('Checkbox (tristate)')
        self.checkbox_tristate.setTristate(True)

        # combobox
        self.combobox = QtGui.QComboBox()
        self.combobox.addItems(['Item 1', 'Item 2', 'Item 3'])

        # editable combobox
        self.combobox_editable = QtGui.QComboBox()
        self.combobox_editable.setEditable(True)
        self.combobox_editable.addItems(['Item 1', 'Item 2', 'Item 3'])

        # lineedit
        self.lineedit = QtGui.QLineEdit('LineEdit')

        # spinbox
        self.spinbox = QtGui.QSpinBox()

        # label
        self.label = QtGui.QLabel('Label')

        # horizontal scrollbar
        self.hscrollbar = QtGui.QScrollBar(Qt.Horizontal)

        # horizontal slider
        self.hslider = QtGui.QSlider(Qt.Horizontal)

        # LCD number
        self.lcdnumber = QtGui.QLCDNumber()
        self.lcdnumber.setNumDigits(10)
        self.lcdnumber.display(1234567890)

        # progressbar
        self.progressbar = QtGui.QProgressBar()
        self.progressbar.setValue(100)

        # scrollarea
        pixmap = QtGui.QPixmap(os.path.join('images', 'python_big_logo.png'))
        label = QtGui.QLabel()
        label.setPixmap(pixmap)
        self.scrollarea = QtGui.QScrollArea()
        self.scrollarea.setWidget(label)
        self.scrollarea.setAlignment(Qt.AlignCenter)

        # groupbox
        self.radiobutton1 = QtGui.QRadioButton('RadioButton 1')
        self.radiobutton2 = QtGui.QRadioButton('RadioButton 2')
        self.radiobutton3 = QtGui.QRadioButton('RadioButton 3')
        groupbox_layout = QtGui.QVBoxLayout()
        groupbox_layout.addWidget(self.radiobutton1)
        groupbox_layout.addWidget(self.radiobutton2)
        groupbox_layout.addWidget(self.radiobutton3)
        self.groupbox = QtGui.QGroupBox('GroupBox')
        self.groupbox.setLayout(groupbox_layout)

        # checkable groupbox
        self.checkbox1 = QtGui.QCheckBox('CheckBox 1')
        self.checkbox2 = QtGui.QCheckBox('CheckBox 2')
        self.checkbox3 = QtGui.QCheckBox('CheckBox 3')
        groupbox_checkable_layout = QtGui.QVBoxLayout()
        groupbox_checkable_layout.addWidget(self.checkbox1)
        groupbox_checkable_layout.addWidget(self.checkbox2)
        groupbox_checkable_layout.addWidget(self.checkbox3)
        self.groupbox_checkable = QtGui.QGroupBox('GroupBox (checkable)')
        self.groupbox_checkable.setLayout(groupbox_checkable_layout)
        self.groupbox_checkable.setCheckable(True)

        # toolbox
        textedit = QtGui.QTextEdit('TextEdit')
        plaintextedit = QtGui.QPlainTextEdit('PlainTextEdit')
        self.toolbox = QtGui.QToolBox()
        self.toolbox.addItem(textedit, 'Page 1')
        self.toolbox.addItem(plaintextedit, 'Page 2')

        # dial
        self.dial = QtGui.QDial()

        # vertical spacer on the left
        vspacer_left = QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.MinimumExpanding)

        # vertical spacer on the right
        vspacer_right = QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.MinimumExpanding)

        # vertical layout on the left
        vlayout_left = QtGui.QVBoxLayout()
        vlayout_left.addWidget(self.pushbutton)
        vlayout_left.addWidget(self.pushbutton_checkable)
        vlayout_left.addWidget(self.radiobutton)
        vlayout_left.addWidget(self.checkbox)
        vlayout_left.addWidget(self.checkbox_tristate)
        vlayout_left.addWidget(self.combobox)
        vlayout_left.addWidget(self.combobox_editable)
        vlayout_left.addWidget(self.lineedit)
        vlayout_left.addWidget(self.spinbox)
        vlayout_left.addWidget(self.label)
        vlayout_left.addWidget(self.hscrollbar)
        vlayout_left.addWidget(self.hslider)
        vlayout_left.addWidget(self.lcdnumber)
        vlayout_left.addWidget(self.progressbar)
        vlayout_left.addWidget(self.scrollarea)
        vlayout_left.addSpacerItem(vspacer_left)
        vlayout_left.setMargin(10)

        # vertical layout on the right
        vlayout_right = QtGui.QVBoxLayout()
        vlayout_right.addWidget(self.groupbox)
        vlayout_right.addWidget(self.groupbox_checkable)
        vlayout_right.addWidget(self.toolbox)
        vlayout_right.addWidget(self.dial)
        vlayout_right.addSpacerItem(vspacer_right)
        vlayout_right.setMargin(10)

        # horizontal layout
        hlayout = QtGui.QHBoxLayout()
        hlayout.addLayout(vlayout_left)
        hlayout.addLayout(vlayout_right)

        # central widget
        central = QtGui.QWidget()
        central.setLayout(hlayout)
        self.setCentralWidget(central)

        # sets focus on QLineEdit widget and selects all the text
        self.lineedit.setFocus()
        self.lineedit.selectAll()


def main():
    # creates the application and takes arguments from the command line
    application = QtGui.QApplication(sys.argv)

    # creates the window and sets its properties
    window = Window()
    window.setWindowTitle('Aqua (Qt stylesheet)')  # title
    window.resize(800, 700)  # size

    # loads and sets the Qt stylesheet
    qss = QSSHelper.open_qss(os.path.join('aqua', 'aqua.qss'))
    window.setStyleSheet(qss)

    window.show()  # shows the window

    # runs the application and waits for its return value at the end
    sys.exit(application.exec_())


if __name__ == '__main__':
    main()
