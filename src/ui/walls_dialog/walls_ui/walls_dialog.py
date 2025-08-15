# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'walls_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QFrame,
    QGridLayout, QGroupBox, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QListView, QPushButton,
    QSizePolicy, QSpacerItem, QTableView, QVBoxLayout,
    QWidget)

class Ui_walls_Dialog(object):
    def setupUi(self, walls_Dialog):
        if not walls_Dialog.objectName():
            walls_Dialog.setObjectName(u"walls_Dialog")
        walls_Dialog.resize(640, 480)
        walls_Dialog.setMinimumSize(QSize(640, 480))
        walls_Dialog.setMaximumSize(QSize(640, 640))
        self.gridLayout = QGridLayout(walls_Dialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.groupBox_3 = QGroupBox(walls_Dialog)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.horizontalLayout_2 = QHBoxLayout(self.groupBox_3)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.left_loads_listView = QListView(self.groupBox_3)
        self.left_loads_listView.setObjectName(u"left_loads_listView")

        self.horizontalLayout_2.addWidget(self.left_loads_listView)

        self.frame = QFrame(self.groupBox_3)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout = QVBoxLayout(self.frame)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.add_loads_left_pushButton = QPushButton(self.frame)
        self.add_loads_left_pushButton.setObjectName(u"add_loads_left_pushButton")
        self.add_loads_left_pushButton.setMaximumSize(QSize(20, 16777215))

        self.verticalLayout.addWidget(self.add_loads_left_pushButton)

        self.delete_loads_left_pushButton = QPushButton(self.frame)
        self.delete_loads_left_pushButton.setObjectName(u"delete_loads_left_pushButton")
        self.delete_loads_left_pushButton.setMaximumSize(QSize(20, 16777215))

        self.verticalLayout.addWidget(self.delete_loads_left_pushButton)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_2)


        self.horizontalLayout_2.addWidget(self.frame)

        self.loads_listView = QListView(self.groupBox_3)
        self.loads_listView.setObjectName(u"loads_listView")

        self.horizontalLayout_2.addWidget(self.loads_listView)

        self.frame_2 = QFrame(self.groupBox_3)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame_2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_3)

        self.add_loads_right_pushButton = QPushButton(self.frame_2)
        self.add_loads_right_pushButton.setObjectName(u"add_loads_right_pushButton")
        self.add_loads_right_pushButton.setMaximumSize(QSize(20, 16777215))

        self.verticalLayout_2.addWidget(self.add_loads_right_pushButton)

        self.delete_loads_right_pushButton = QPushButton(self.frame_2)
        self.delete_loads_right_pushButton.setObjectName(u"delete_loads_right_pushButton")
        self.delete_loads_right_pushButton.setMaximumSize(QSize(20, 16777215))

        self.verticalLayout_2.addWidget(self.delete_loads_right_pushButton)

        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_4)


        self.horizontalLayout_2.addWidget(self.frame_2)

        self.right_loads_listView = QListView(self.groupBox_3)
        self.right_loads_listView.setObjectName(u"right_loads_listView")

        self.horizontalLayout_2.addWidget(self.right_loads_listView)


        self.gridLayout.addWidget(self.groupBox_3, 4, 0, 1, 2)

        self.cancel_pushButton = QPushButton(walls_Dialog)
        self.cancel_pushButton.setObjectName(u"cancel_pushButton")

        self.gridLayout.addWidget(self.cancel_pushButton, 6, 1, 1, 1)

        self.groupBox = QGroupBox(walls_Dialog)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setMinimumSize(QSize(322, 0))
        self.gridLayout_2 = QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)

        self.bottom_story_comboBox = QComboBox(self.groupBox)
        self.bottom_story_comboBox.setObjectName(u"bottom_story_comboBox")
        self.bottom_story_comboBox.setMinimumSize(QSize(0, 0))

        self.gridLayout_2.addWidget(self.bottom_story_comboBox, 2, 1, 1, 4)

        self.top_story_comboBox = QComboBox(self.groupBox)
        self.top_story_comboBox.setObjectName(u"top_story_comboBox")
        self.top_story_comboBox.setMinimumSize(QSize(0, 0))

        self.gridLayout_2.addWidget(self.top_story_comboBox, 3, 1, 1, 4)

        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_2.addWidget(self.label_2, 2, 0, 1, 1)

        self.wall_name_lineEdit = QLineEdit(self.groupBox)
        self.wall_name_lineEdit.setObjectName(u"wall_name_lineEdit")
        self.wall_name_lineEdit.setMinimumSize(QSize(0, 0))
        self.wall_name_lineEdit.setMaximumSize(QSize(16777215, 16777215))

        self.gridLayout_2.addWidget(self.wall_name_lineEdit, 0, 1, 1, 4)

        self.n_stoiries_label = QLabel(self.groupBox)
        self.n_stoiries_label.setObjectName(u"n_stoiries_label")

        self.gridLayout_2.addWidget(self.n_stoiries_label, 4, 1, 1, 1)

        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_2.addWidget(self.label_3, 3, 0, 1, 1)

        self.wall_height_label = QLabel(self.groupBox)
        self.wall_height_label.setObjectName(u"wall_height_label")

        self.gridLayout_2.addWidget(self.wall_height_label, 5, 1, 1, 1)


        self.gridLayout.addWidget(self.groupBox, 1, 0, 1, 1)

        self.ok_pushButton = QPushButton(walls_Dialog)
        self.ok_pushButton.setObjectName(u"ok_pushButton")

        self.gridLayout.addWidget(self.ok_pushButton, 6, 0, 1, 1)

        self.frame_3 = QFrame(walls_Dialog)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_4 = QHBoxLayout(self.frame_3)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_4 = QLabel(self.frame_3)
        self.label_4.setObjectName(u"label_4")

        self.horizontalLayout_4.addWidget(self.label_4)

        self.select_story_comboBox = QComboBox(self.frame_3)
        self.select_story_comboBox.setObjectName(u"select_story_comboBox")

        self.horizontalLayout_4.addWidget(self.select_story_comboBox)


        self.gridLayout.addWidget(self.frame_3, 2, 0, 1, 1)

        self.groupBox_2 = QGroupBox(walls_Dialog)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setMaximumSize(QSize(16777215, 16777215))
        self.horizontalLayout = QHBoxLayout(self.groupBox_2)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.tribs_tableView = QTableView(self.groupBox_2)
        self.tribs_tableView.setObjectName(u"tribs_tableView")

        self.horizontalLayout.addWidget(self.tribs_tableView)


        self.gridLayout.addWidget(self.groupBox_2, 1, 1, 1, 1)


        self.retranslateUi(walls_Dialog)

        QMetaObject.connectSlotsByName(walls_Dialog)
    # setupUi

    def retranslateUi(self, walls_Dialog):
        walls_Dialog.setWindowTitle(QCoreApplication.translate("walls_Dialog", u"Add/Edit Wall", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("walls_Dialog", u"Loads", None))
        self.add_loads_left_pushButton.setText(QCoreApplication.translate("walls_Dialog", u"<", None))
        self.delete_loads_left_pushButton.setText(QCoreApplication.translate("walls_Dialog", u">", None))
        self.add_loads_right_pushButton.setText(QCoreApplication.translate("walls_Dialog", u">", None))
        self.delete_loads_right_pushButton.setText(QCoreApplication.translate("walls_Dialog", u"<", None))
        self.cancel_pushButton.setText(QCoreApplication.translate("walls_Dialog", u"Cancel", None))
        self.groupBox.setTitle(QCoreApplication.translate("walls_Dialog", u"Wall Info", None))
        self.label.setText(QCoreApplication.translate("walls_Dialog", u"Wall Name:", None))
        self.label_2.setText(QCoreApplication.translate("walls_Dialog", u"Bottom Story:", None))
        self.n_stoiries_label.setText(QCoreApplication.translate("walls_Dialog", u"TextLabel", None))
        self.label_3.setText(QCoreApplication.translate("walls_Dialog", u"Top Story:", None))
        self.wall_height_label.setText(QCoreApplication.translate("walls_Dialog", u"TextLabel", None))
        self.ok_pushButton.setText(QCoreApplication.translate("walls_Dialog", u"OK", None))
        self.label_4.setText(QCoreApplication.translate("walls_Dialog", u"Select Story To Edit Loads:", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("walls_Dialog", u"Tributary Widths", None))
    # retranslateUi

