# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'load_combos_dialog.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QFormLayout, QFrame,
    QGridLayout, QGroupBox, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QListView, QPushButton,
    QSizePolicy, QSpacerItem, QTableView, QVBoxLayout,
    QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(605, 501)
        self.gridLayout = QGridLayout(Dialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.groupBox = QGroupBox(Dialog)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout = QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.load_combinations_listView = QListView(self.groupBox)
        self.load_combinations_listView.setObjectName(u"load_combinations_listView")

        self.verticalLayout.addWidget(self.load_combinations_listView)

        self.frame_2 = QFrame(self.groupBox)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frame_2)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.new_load_combination_pushButton = QPushButton(self.frame_2)
        self.new_load_combination_pushButton.setObjectName(u"new_load_combination_pushButton")

        self.horizontalLayout_2.addWidget(self.new_load_combination_pushButton)

        self.delete_load_combination_pushButton = QPushButton(self.frame_2)
        self.delete_load_combination_pushButton.setObjectName(u"delete_load_combination_pushButton")

        self.horizontalLayout_2.addWidget(self.delete_load_combination_pushButton)


        self.verticalLayout.addWidget(self.frame_2)


        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 1)

        self.groupBox_2 = QGroupBox(Dialog)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.formLayout = QFormLayout(self.groupBox_2)
        self.formLayout.setObjectName(u"formLayout")
        self.label = QLabel(self.groupBox_2)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label)

        self.load_combination_lineEdit = QLineEdit(self.groupBox_2)
        self.load_combination_lineEdit.setObjectName(u"load_combination_lineEdit")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.load_combination_lineEdit)

        self.load_cases_tableView = QTableView(self.groupBox_2)
        self.load_cases_tableView.setObjectName(u"load_cases_tableView")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.SpanningRole, self.load_cases_tableView)

        self.frame_4 = QFrame(self.groupBox_2)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_4.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frame_4)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.add_load_case_pushButton = QPushButton(self.frame_4)
        self.add_load_case_pushButton.setObjectName(u"add_load_case_pushButton")

        self.horizontalLayout_3.addWidget(self.add_load_case_pushButton)

        self.remove_load_case_pushButton = QPushButton(self.frame_4)
        self.remove_load_case_pushButton.setObjectName(u"remove_load_case_pushButton")

        self.horizontalLayout_3.addWidget(self.remove_load_case_pushButton)

        self.save_load_combiation_pushButton = QPushButton(self.frame_4)
        self.save_load_combiation_pushButton.setObjectName(u"save_load_combiation_pushButton")

        self.horizontalLayout_3.addWidget(self.save_load_combiation_pushButton)


        self.formLayout.setWidget(2, QFormLayout.ItemRole.SpanningRole, self.frame_4)


        self.gridLayout.addWidget(self.groupBox_2, 0, 2, 1, 1)

        self.frame_3 = QFrame(Dialog)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame_3)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.ok_pushButton = QPushButton(self.frame_3)
        self.ok_pushButton.setObjectName(u"ok_pushButton")

        self.horizontalLayout.addWidget(self.ok_pushButton)

        self.cancel_pushButton = QPushButton(self.frame_3)
        self.cancel_pushButton.setObjectName(u"cancel_pushButton")

        self.horizontalLayout.addWidget(self.cancel_pushButton)


        self.gridLayout.addWidget(self.frame_3, 1, 0, 1, 3)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Create/Edit Stud Sections", None))
        self.groupBox.setTitle(QCoreApplication.translate("Dialog", u"Load Combinations", None))
        self.new_load_combination_pushButton.setText(QCoreApplication.translate("Dialog", u"New", None))
        self.delete_load_combination_pushButton.setText(QCoreApplication.translate("Dialog", u"Delete", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("Dialog", u"Stud Properties", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"Name:", None))
        self.add_load_case_pushButton.setText(QCoreApplication.translate("Dialog", u"Add", None))
        self.remove_load_case_pushButton.setText(QCoreApplication.translate("Dialog", u"Delete", None))
        self.save_load_combiation_pushButton.setText(QCoreApplication.translate("Dialog", u"Save", None))
        self.ok_pushButton.setText(QCoreApplication.translate("Dialog", u"OK", None))
        self.cancel_pushButton.setText(QCoreApplication.translate("Dialog", u"Cencel", None))
    # retranslateUi

