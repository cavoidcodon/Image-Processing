from PyQt5 import QtGui, QtCore, QtWidgets


class ResultViewer(QtWidgets.QDialog):
    def __init__(self):
        super(ResultViewer, self).__init__()

        self.answer_box = QtWidgets.QGroupBox("Answer")
        self.id_box = QtWidgets.QGroupBox("ID")

        self.title = 'Result'
        self.left = 50
        self.top = 50
        self.width = 300
        self.height = 500

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

    def show_result(self):
        window_layout = QtWidgets.QVBoxLayout()
        window_layout.addWidget(self.id_box)
        window_layout.addWidget(self.answer_box)
        self.setLayout(window_layout)
        self.show()

    def create_grid_layout(self, student_id, test_id, answer):
        id_layout = QtWidgets.QGridLayout()
        id_layout.setColumnStretch(0, 1)
        id_layout.setColumnStretch(1, 3)
        answer_layout = QtWidgets.QGridLayout()

        id_layout.addWidget(QtWidgets.QLabel('Student ID'), 0, 0)
        id_layout.addWidget(QtWidgets.QLabel('Test ID'), 1, 0)
        id_layout.addWidget(QtWidgets.QLabel(str(student_id)), 0, 1)
        id_layout.addWidget(QtWidgets.QLabel(str(test_id)), 1, 1)

        count = 0
        for i in range(0, 6, 2):
            for j in range(0, 20):
                if count >= 50:
                    break
                answer_layout.addWidget(QtWidgets.QLabel(str(count + 1)), j, i)
                answer_layout.addWidget(QtWidgets.QLabel(str(answer[count])), j, i + 1)
                count += 1

        self.answer_box.setLayout(answer_layout)
        self.id_box.setLayout(id_layout)
