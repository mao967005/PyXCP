import sys
from PyQt4 import QtGui, QtCore
import HelpGUI
import XcpCom
import qdarkstyle


class Window(QtGui.QMainWindow):

    def __init__(self):
        super(Window, self).__init__()
        self.setGeometry(50, 50, 500, 300)
        self.setWindowTitle('PyXCP')
        #self.setWindowIcon(QtGui.QIcon('optim.jpg'))

        self.helper = HelpGUI.AssistGUI()
        self.xcp_com = XcpCom.XcpCommunicator(0)

        # create menu item quit
        quit_action = QtGui.QAction('&Quit', self)
        quit_action.setShortcut('Ctrl+Q')
        quit_action.setStatusTip('Leave the app')
        quit_action.triggered.connect(self.close_application)

        # create menu item open file
        open_file = QtGui.QAction('&Load A2L', self)
        open_file.setShortcut('Ctrl+O')
        open_file.setStatusTip('Open file')
        open_file.triggered.connect(self.file_open)

        open_help = QtGui.QAction('&Open Help', self)
        open_help.setShortcut('Ctrl+H')
        open_help.setStatusTip('Open the pdf help documentation')
        open_help.triggered.connect(lambda: self.helper.open_documentation())

        self.statusBar()

        main_menu = self.menuBar()

        file_menu = main_menu.addMenu('&File')
        file_menu.addAction(quit_action)
        file_menu.addAction(open_file)
        file_menu.addAction(open_help)

        self.home()

    def home(self):
        # btn = QtGui.QPushButton('Quit', self)
        # btn.clicked.connect(self.close_application)
        # btn.resize(btn.sizeHint())
        # btn.move(100, 100)

        btn = QtGui.QPushButton('Start Stream', self)
        btn.clicked.connect(self.get_address)
        btn.resize(btn.sizeHint())
        btn.move(10, 70)

        btn = QtGui.QPushButton('Stop Stream', self)
        btn.clicked.connect(self.stop_stream)
        btn.resize(btn.sizeHint())
        btn.move(10, 110)

        # create tool bar
        # extract_action = QtGui.QAction(QtGui.QIcon('optim.jpg'),
        #                                'Hover Text', self)
        # extract_action.triggered.connect(self.close_application)
        #
        # self.toolBar = self.addToolBar('Extraction')
        # self.toolBar.addAction(extract_action)

        # PTO message controls
        # self.checkBox = QtGui.QCheckBox('Transmission', self)
        # self.checkBox.pressed.connect(lambda: self.pto_transmission(self.checkBox))
        # self.checkBox.move(0, 50)

        # checkBox = QtGui.QCheckBox('Enable', self)
        # checkBox.stateChanged.connect(self.enlarge_window)
        # checkBox.move(0, 70)

        # self.progress = QtGui.QProgressBar(self)
        # self.progress.setGeometry(200, 80, 250, 20)
        #
        # self.btn = QtGui.QPushButton('download', self)
        # self.btn.move(200, 120)
        # self.btn.clicked.connect(self.download)

        self.model = QtGui.QStringListModel(self)
        self.model.setStringList(['test'])

        completer = QtGui.QCompleter(self)
        completer.setModel(self.model)

        self.le = QtGui.QLineEdit(self)
        self.le.setCompleter(completer)
        self.le.setGeometry(10, 30, 400, 30)


        # textbox = QtGui.QLineEdit(self)

        self.show()

    def pto_transmission(self, b):
        if b.isChecked() == True:
            print('Checked')
        else:
            print('Not checked')

    def get_address(self):
        label = self.le.text()
        name, data_type, address = self.helper.find_address_from_name(label)
        self.xcp_com.setup_daq(int(address, 16))
        self.xcp_com.graph_response(10)

    def stop_stream(self):
        self.xcp_com.xcp_stop()


    def file_open(self):
        name = QtGui.QFileDialog.getOpenFileName(self, 'Please select an .a2l file')
        measurement_list = self.helper.parse_a2l(name)
        self.model.setStringList(measurement_list)



    def download(self):
        self.completed = 0

        while self.completed < 100:
            self.completed += 0.0001
            self.progress.setValue(self.completed)

    def close_application(self):
        choice =QtGui.QMessageBox.question(self, 'Extract!',
                                           'Do you want to quit?',
                                           QtGui.QMessageBox.Yes |
                                           QtGui.QMessageBox.No)
        if choice == QtGui.QMessageBox.Yes:
            print('Alright, see you later!')
            self.xcp_com.xcp_stop()
            sys.exit()
        else:
            pass

    def enlarge_window(self, state):
        if state == QtCore.Qt.Checked:
            self.setGeometry(50, 50, 1000, 600)
        else:
            self.setGeometry(50, 50, 500, 300)


def main():
    app = QtGui.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt())
    gui = Window()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
