# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'loads_dialog.load_combos_ui'
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
    QHBoxLayout, QHeaderView, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QSpacerItem, QTableView,
    QVBoxLayout, QWidget)

class Ui_loads_Dialog(object):
    def setupUi(self, loads_Dialog):
        if not loads_Dialog.objectName():
            loads_Dialog.setObjectName(u"loads_Dialog")
        loads_Dialog.resize(601, 453)
        self.verticalLayout = QVBoxLayout(loads_Dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.frame = QFrame(loads_Dialog)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(self.frame)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.load_name_lineEdit = QLineEdit(self.frame)
        self.load_name_lineEdit.setObjectName(u"load_name_lineEdit")

        self.horizontalLayout.addWidget(self.load_name_lineEdit)

        self.label_2 = QLabel(self.frame)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout.addWidget(self.label_2)

        self.load_case_comboBox = QComboBox(self.frame)
        self.load_case_comboBox.setObjectName(u"load_case_comboBox")
        self.load_case_comboBox.setMinimumSize(QSize(150, 0))

        self.horizontalLayout.addWidget(self.load_case_comboBox)

        self.label_3 = QLabel(self.frame)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout.addWidget(self.label_3)

        self.load_value_lineEdit = QLineEdit(self.frame)
        self.load_value_lineEdit.setObjectName(u"load_value_lineEdit")
        self.load_value_lineEdit.setMaximumSize(QSize(75, 16777215))

        self.horizontalLayout.addWidget(self.load_value_lineEdit)


        self.verticalLayout.addWidget(self.frame)

        self.frame_3 = QFrame(loads_Dialog)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frame_3)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.add_load_pushButton = QPushButton(self.frame_3)
        self.add_load_pushButton.setObjectName(u"add_load_pushButton")

        self.horizontalLayout_3.addWidget(self.add_load_pushButton)

        self.edit_load_pushButton = QPushButton(self.frame_3)
        self.edit_load_pushButton.setObjectName(u"edit_load_pushButton")

        self.horizontalLayout_3.addWidget(self.edit_load_pushButton)

        self.delete_load_pushButton = QPushButton(self.frame_3)
        self.delete_load_pushButton.setObjectName(u"delete_load_pushButton")

        self.horizontalLayout_3.addWidget(self.delete_load_pushButton)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)


        self.verticalLayout.addWidget(self.frame_3)

        self.loads_tableView = QTableView(loads_Dialog)
        self.loads_tableView.setObjectName(u"loads_tableView")

        self.verticalLayout.addWidget(self.loads_tableView)

        self.frame_2 = QFrame(loads_Dialog)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frame_2)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.ok_pushButton = QPushButton(self.frame_2)
        self.ok_pushButton.setObjectName(u"ok_pushButton")

        self.horizontalLayout_2.addWidget(self.ok_pushButton)

        self.cancel_pushButton = QPushButton(self.frame_2)
        self.cancel_pushButton.setObjectName(u"cancel_pushButton")

        self.horizontalLayout_2.addWidget(self.cancel_pushButton)


        self.verticalLayout.addWidget(self.frame_2)


        self.retranslateUi(loads_Dialog)

        QMetaObject.connectSlotsByName(loads_Dialog)
    # setupUi

    def retranslateUi(self, loads_Dialog):
        loads_Dialog.setWindowTitle(QCoreApplication.translate("loads_Dialog", u"Edit Loads", None))
        self.label.setText(QCoreApplication.translate("loads_Dialog", u"Name:", None))
        self.label_2.setText(QCoreApplication.translate("loads_Dialog", u"Case:", None))
        self.label_3.setText(QCoreApplication.translate("loads_Dialog", u"Valuie:", None))
        self.add_load_pushButton.setText(QCoreApplication.translate("loads_Dialog", u"Add", None))
        self.edit_load_pushButton.setText(QCoreApplication.translate("loads_Dialog", u"Edit", None))
        self.delete_load_pushButton.setText(QCoreApplication.translate("loads_Dialog", u"Delete", None))
        self.ok_pushButton.setText(QCoreApplication.translate("loads_Dialog", u"OK", None))
        self.cancel_pushButton.setText(QCoreApplication.translate("loads_Dialog", u"Cancel", None))
    # retranslateUi

