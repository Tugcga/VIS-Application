import sys
from PyQt4 import QtGui, QtCore

from main_window import MainWindow
from helpers.read_data import get_image_path

if __name__ == '__main__':
    appQt = QtGui.QApplication(sys.argv)
    use_splash = True
    if use_splash:
        splash_pix = QtGui.QPixmap(get_image_path("splash.png"))
        splash = QtGui.QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
        splash.show()
        appQt.processEvents()
    win = MainWindow()
    app_icon = QtGui.QIcon()
    app_icon.addFile(get_image_path("icon_16.png"), QtCore.QSize(16, 16))
    app_icon.addFile(get_image_path("icon_24.png"), QtCore.QSize(24, 24))
    app_icon.addFile(get_image_path("icon_32.png"), QtCore.QSize(32, 32))
    app_icon.addFile(get_image_path("icon_48.png"), QtCore.QSize(48, 48))
    app_icon.addFile(get_image_path("icon_256.png"), QtCore.QSize(256, 256))
    win.setWindowIcon(app_icon)
    win.show()
    if use_splash:
        pass
        # splash.finish(win)
    appQt.exec_()
