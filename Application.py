import sys
from PyQt5 import QtGui, QtCore, QtWidgets
from ImageViewer import ImageViewer
from ResultViewer import ResultViewer
import cv2
import ntpath
from utilities import *
import numpy as np
import math


class Application(QtWidgets.QMainWindow):
    def __init__(self):
        super(Application, self).__init__()

        self.RESIZED_WIDTH = 1500
        self.RESIZED_HEIGHT = 2100
        self.AREA_SIZE = 250
        self.THRESHOLD_VALUE = 230

        self.global_dir = r"D:\Developments\Projects\XLA\output\global"
        self.local_dir = r"D:\Developments\Projects\XLA\output\local"
        self.rotate_dir = r"D:\Developments\Projects\XLA\output\rotate"
        self.morphology_dir = r"D:\Developments\Projects\XLA\output\morphology"

        self.mark_x = 0
        self.mark_y = 0

        self.choice_image_path = ''
        self.rotated_image_path = ''
        self.global_threshold_path = ''
        self.morphology_image_path = ''

        self.global_threshold_image = None
        self.local_threshold_image = None
        self.morphology_image = None
        self.rotated_image = None

        self.original_image_viewer = ImageViewer()
        self.global_image_viewer = ImageViewer()
        self.local_image_viewer = ImageViewer()
        self.rotate_image_viewer = ImageViewer()
        self.morphology_image_viewer = ImageViewer()
        self.result_viewer = None

        self.setGeometry(100, 100, 300, 400)
        self.setWindowTitle("Image Processing")
        self.init_ui()

    def init_ui(self):
        open_btn = QtWidgets.QPushButton("Open", self)
        open_btn.clicked.connect(self.open)
        open_btn.move(30, 50)

        threshold_global_btn = QtWidgets.QPushButton("Global Threshold", self)
        threshold_global_btn.clicked.connect(self.global_threshold)
        threshold_global_btn.move(30, 100)

        threshold_local_btn = QtWidgets.QPushButton("Local Threshold", self)
        threshold_local_btn.clicked.connect(self.local_threshold)
        threshold_local_btn.move(30, 150)

        rotate_btn = QtWidgets.QPushButton("Rotate", self)
        rotate_btn.clicked.connect(self.rotate)
        rotate_btn.move(170, 50)

        morphology_btn = QtWidgets.QPushButton("Morphology", self)
        morphology_btn.clicked.connect(self.morphology)
        morphology_btn.move(170, 100)

        get_result_btn = QtWidgets.QPushButton("Get Result", self)
        get_result_btn.clicked.connect(self.get_result)
        get_result_btn.move(170, 150)

    def get_result(self):
        self.result_viewer = ResultViewer()

        if len(self.rotated_image_path) == 0:
            QtWidgets.QMessageBox.question(self, "Warning",
                                           "Please rotate image before get result", QtWidgets.QMessageBox.Ok)
            return

        rotated = self.rotated_image
        ret, image = cv2.threshold(rotated, self.THRESHOLD_VALUE, 255, cv2.THRESH_BINARY)

        coor = (self.mark_x, self.mark_y)
        marks, id_marks, answer_marks = find_coordinate(image, coor)

        # read image, get id, answers then save to a matrix
        sbd = get_id(image, marks, id_marks)
        answer = get_answer(image, marks, answer_marks)

        # read answer, id from a id matrix, answer matrix
        student_id = read_student_id(sbd)
        test_id = read_test_id(sbd)
        ans = read_answer(answer)

        self.result_viewer.create_grid_layout(student_id, test_id, ans)
        self.result_viewer.show_result()

    def open(self):
        file_name = QtWidgets.QFileDialog.getOpenFileName(self, 'QFileDialog.getOpenFileName()', '',
                                                          'Images (*.png *.jpeg *.jpg *.bmp *.gif)')
        self.choice_image_path = file_name[0]
        self.original_image_viewer.set_image(self.choice_image_path)
        self.original_image_viewer.show()

    def global_threshold(self):
        if len(self.choice_image_path) == 0:
            QtWidgets.QMessageBox.question(self, "Warning",
                                           "Please press \"Open\" button to choose a image", QtWidgets.QMessageBox.Ok)
            return

        directory, name = ntpath.split(self.choice_image_path)
        img = cv2.imread(self.choice_image_path)
        if len(img.shape) > 2:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # threshold image with the fix value
        ret, thresh = cv2.threshold(img, self.THRESHOLD_VALUE, 255, cv2.THRESH_BINARY)
        self.global_threshold_image = thresh

        # save image for showing
        saved_path = self.global_dir + '\\' + name
        self.global_threshold_path = saved_path
        cv2.imwrite(saved_path, thresh)
        # show global threshold image
        self.global_image_viewer.set_image(saved_path)
        self.global_image_viewer.setWindowTitle("Global Threshold")
        self.global_image_viewer.show()

    def rotate(self):
        if len(self.morphology_image_path) == 0:
            QtWidgets.QMessageBox.question(self, "Warning",
                                           "Please morphology image before", QtWidgets.QMessageBox.Ok)
            return
        # get the image for rotation
        img = self.morphology_image

        # resize image to standard size
        dim = (self.RESIZED_WIDTH, self.RESIZED_HEIGHT)
        img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)

        # find marked point in top left and right of the image
        # get top left area
        left = img[0:self.AREA_SIZE, 0:self.AREA_SIZE]
        # get top right area
        right = img[0:self.AREA_SIZE, self.RESIZED_WIDTH - self.AREA_SIZE:self.RESIZED_WIDTH]
        # find mark point in area
        left_x, left_y, min_left = find_interested_point(left)
        right_x, right_y, min_right = find_interested_point(right)
        right_x = self.RESIZED_WIDTH - self.AREA_SIZE + right_x

        # calculate angle for rotation
        # left's mark point is center for rotation
        dis_y = right_y - left_y
        dis_x = right_x - left_x
        tan_alpha = dis_y / dis_x
        alpha_rad = np.arctan(tan_alpha)
        alpha_deg = np.rad2deg(alpha_rad)

        # calculate top right mark point after rotation
        self.mark_x = int(math.cos(alpha_rad) * (right_x - left_x) -
                          math.sin(alpha_rad) * (right_y - left_y) + left_x)
        self.mark_y = int(-math.sin(alpha_rad) * (right_x - left_x) +
                          math.cos(alpha_rad) * (right_y - left_y) + left_y)

        # rotate image
        m = cv2.getRotationMatrix2D((left_x, left_y), alpha_deg, 1)
        rotated = cv2.warpAffine(img, m, dim)

        # save rotation image
        self.rotated_image = rotated

        # get the directory path and file name
        # file name used for save processed image
        directory, name = ntpath.split(self.morphology_image_path)

        # save rotated image and show it to the window
        saved_path = self.rotate_dir + '\\' + name
        self.rotated_image_path = saved_path
        cv2.imwrite(saved_path, rotated)

        self.rotate_image_viewer.set_image(saved_path)
        self.rotate_image_viewer.setWindowTitle("Rotated Image")
        self.rotate_image_viewer.show()

    def local_threshold(self):
        if len(self.choice_image_path) == 0:
            QtWidgets.QMessageBox.question(self, "Warning",
                                           "Please press \"Open\" button to choose a image", QtWidgets.QMessageBox.Ok)
            return

        image = cv2.imread(self.choice_image_path)
        if len(image.shape) > 2:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        id_part = image[200:700, 1100:self.RESIZED_WIDTH]
        answer_part = image[1000:self.RESIZED_HEIGHT, 0:self.RESIZED_WIDTH]

        id_thresh_val, id_threshold = cv2.threshold(id_part, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        answer_thresh_val, answer_threshold = cv2.threshold(answer_part, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        threshold_val = max(id_thresh_val, answer_thresh_val)
        ret, thresh = cv2.threshold(image, threshold_val, 255, cv2.THRESH_BINARY)
        self.local_threshold_image = thresh

        directory, name = ntpath.split(self.choice_image_path)
        saved_path = self.local_dir + '\\' + name
        cv2.imwrite(saved_path, thresh)

        self.local_image_viewer.set_image(saved_path)
        self.local_image_viewer.setWindowTitle("Local Threshold")
        self.local_image_viewer.show()

    def morphology(self):
        if len(self.global_threshold_path) == 0:
            QtWidgets.QMessageBox.question(self, "Warning",
                                           "Please global threshold before", QtWidgets.QMessageBox.Ok)
            return

        binary_image = self.global_threshold_image

        invert_img = cv2.bitwise_not(binary_image)
        opening_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
        opening = cv2.morphologyEx(invert_img, cv2.MORPH_OPEN, opening_kernel)
        closing_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
        closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, closing_kernel)
        dilation_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        morphology_image = cv2.dilate(closing, dilation_kernel, iterations=1)
        morphology_image = cv2.bitwise_not(morphology_image)
        self.morphology_image = morphology_image

        directory, name = ntpath.split(self.global_threshold_path)
        saved_path = self.morphology_dir + '\\' + name
        self.morphology_image_path = saved_path
        cv2.imwrite(saved_path, morphology_image)

        self.morphology_image_viewer.set_image(saved_path)
        self.morphology_image_viewer.setWindowTitle("Morphology Image")
        self.morphology_image_viewer.show()

    def closeEvent(self, event):
        widget_list = QtWidgets.QApplication.topLevelWidgets()
        num_windows = len(widget_list)
        if num_windows > 1:
            event.accept()
        else:
            event.ignore()


def run():
    app = QtWidgets.QApplication(sys.argv)
    gui = Application()
    gui.show()
    sys.exit(app.exec_())


run()
