from PyQt5 import QtGui, QtCore, QtWidgets


class ImageViewer(QtWidgets.QMainWindow):
    def __init__(self):
        super(ImageViewer, self).__init__()
        self.STANDARD_WIDTH = 800
        self.STANDARD_HEIGHT = 1200

        self.imageLabel = QtWidgets.QLabel()
        self.imageLabel.setBackgroundRole(QtGui.QPalette.Base)
        self.imageLabel.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)

        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollArea.setBackgroundRole(QtGui.QPalette.Dark)

        self.setCentralWidget(self.scrollArea)

        self.setWindowTitle("Image Viewer")
        self.image = ''

    def set_image(self, file_path):
        self.image = file_path
        pixmap = QtGui.QPixmap(file_path).scaled(self.STANDARD_WIDTH, self.STANDARD_HEIGHT)
        self.imageLabel.setPixmap(pixmap)
        self.scrollArea.setWidget(self.imageLabel)
        self.resize(pixmap.width(), pixmap.height())
