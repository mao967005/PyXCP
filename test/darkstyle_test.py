import qdarkstyle

import sys
import qdarkstyle
from PyQt4 import QtGui

# create the application and the main window
app = QtGui.QApplication(sys.argv)
window = QtGui.QMainWindow()

# setup stylesheet
app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt())

# run
window.show()
app.exec_()
