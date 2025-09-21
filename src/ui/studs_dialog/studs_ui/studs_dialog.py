# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'studs_dialog.load_combos_ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog,
    QFormLayout, QFrame, QGridLayout, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QListView,
    QPushButton, QSizePolicy, QSpacerItem, QSpinBox,
    QVBoxLayout, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(523, 501)
        self.gridLayout = QGridLayout(Dialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.groupBox = QGroupBox(Dialog)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout = QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.frame = QFrame(self.groupBox)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.formLayout = QFormLayout(self.frame)
        self.formLayout.setObjectName(u"formLayout")
        self.material_filter_checkBox = QCheckBox(self.frame)
        self.material_filter_checkBox.setObjectName(u"material_filter_checkBox")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.material_filter_checkBox)

        self.material_filter_comboBox = QComboBox(self.frame)
        self.material_filter_comboBox.setObjectName(u"material_filter_comboBox")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.material_filter_comboBox)


        self.verticalLayout.addWidget(self.frame)

        self.stud_sections_listView = QListView(self.groupBox)
        self.stud_sections_listView.setObjectName(u"stud_sections_listView")

        self.verticalLayout.addWidget(self.stud_sections_listView)

        self.frame_2 = QFrame(self.groupBox)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frame_2)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.new_stud_pushButton = QPushButton(self.frame_2)
        self.new_stud_pushButton.setObjectName(u"new_stud_pushButton")

        self.horizontalLayout_2.addWidget(self.new_stud_pushButton)

        self.delete_stud_pushButton = QPushButton(self.frame_2)
        self.delete_stud_pushButton.setObjectName(u"delete_stud_pushButton")

        self.horizontalLayout_2.addWidget(self.delete_stud_pushButton)


        self.verticalLayout.addWidget(self.frame_2)


        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 1)

        self.groupBox_2 = QGroupBox(Dialog)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.formLayout_2 = QFormLayout(self.groupBox_2)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.label = QLabel(self.groupBox_2)
        self.label.setObjectName(u"label")

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label)

        self.stud_name_lineEdit = QLineEdit(self.groupBox_2)
        self.stud_name_lineEdit.setObjectName(u"stud_name_lineEdit")

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.FieldRole, self.stud_name_lineEdit)

        self.label_2 = QLabel(self.groupBox_2)
        self.label_2.setObjectName(u"label_2")

        self.formLayout_2.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_2)

        self.stud_width_lineEdit = QLineEdit(self.groupBox_2)
        self.stud_width_lineEdit.setObjectName(u"stud_width_lineEdit")

        self.formLayout_2.setWidget(2, QFormLayout.ItemRole.FieldRole, self.stud_width_lineEdit)

        self.label_3 = QLabel(self.groupBox_2)
        self.label_3.setObjectName(u"label_3")

        self.formLayout_2.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_3)

        self.stud_deoth_lineEdit = QLineEdit(self.groupBox_2)
        self.stud_deoth_lineEdit.setObjectName(u"stud_deoth_lineEdit")

        self.formLayout_2.setWidget(3, QFormLayout.ItemRole.FieldRole, self.stud_deoth_lineEdit)

        self.label_7 = QLabel(self.groupBox_2)
        self.label_7.setObjectName(u"label_7")

        self.formLayout_2.setWidget(4, QFormLayout.ItemRole.LabelRole, self.label_7)

        self.number_of_ply_spinBox = QSpinBox(self.groupBox_2)
        self.number_of_ply_spinBox.setObjectName(u"number_of_ply_spinBox")
        self.number_of_ply_spinBox.setMinimum(1)
        self.number_of_ply_spinBox.setMaximum(5)

        self.formLayout_2.setWidget(4, QFormLayout.ItemRole.FieldRole, self.number_of_ply_spinBox)

        self.label_8 = QLabel(self.groupBox_2)
        self.label_8.setObjectName(u"label_8")

        self.formLayout_2.setWidget(5, QFormLayout.ItemRole.LabelRole, self.label_8)

        self.stud_area_label = QLabel(self.groupBox_2)
        self.stud_area_label.setObjectName(u"stud_area_label")

        self.formLayout_2.setWidget(5, QFormLayout.ItemRole.FieldRole, self.stud_area_label)

        self.label_10 = QLabel(self.groupBox_2)
        self.label_10.setObjectName(u"label_10")

        self.formLayout_2.setWidget(6, QFormLayout.ItemRole.LabelRole, self.label_10)

        self.stud_ix_label = QLabel(self.groupBox_2)
        self.stud_ix_label.setObjectName(u"stud_ix_label")

        self.formLayout_2.setWidget(6, QFormLayout.ItemRole.FieldRole, self.stud_ix_label)

        self.label_12 = QLabel(self.groupBox_2)
        self.label_12.setObjectName(u"label_12")

        self.formLayout_2.setWidget(7, QFormLayout.ItemRole.LabelRole, self.label_12)

        self.stud_iy_label = QLabel(self.groupBox_2)
        self.stud_iy_label.setObjectName(u"stud_iy_label")

        self.formLayout_2.setWidget(7, QFormLayout.ItemRole.FieldRole, self.stud_iy_label)

        self.label_14 = QLabel(self.groupBox_2)
        self.label_14.setObjectName(u"label_14")

        self.formLayout_2.setWidget(8, QFormLayout.ItemRole.LabelRole, self.label_14)

        self.stud_sx_label = QLabel(self.groupBox_2)
        self.stud_sx_label.setObjectName(u"stud_sx_label")

        self.formLayout_2.setWidget(8, QFormLayout.ItemRole.FieldRole, self.stud_sx_label)

        self.label_16 = QLabel(self.groupBox_2)
        self.label_16.setObjectName(u"label_16")

        self.formLayout_2.setWidget(9, QFormLayout.ItemRole.LabelRole, self.label_16)

        self.stud_sy_label = QLabel(self.groupBox_2)
        self.stud_sy_label.setObjectName(u"stud_sy_label")

        self.formLayout_2.setWidget(9, QFormLayout.ItemRole.FieldRole, self.stud_sy_label)

        self.frame_4 = QFrame(self.groupBox_2)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_4.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frame_4)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_3)

        self.save_stud_pushButton = QPushButton(self.frame_4)
        self.save_stud_pushButton.setObjectName(u"save_stud_pushButton")

        self.horizontalLayout_3.addWidget(self.save_stud_pushButton)


        self.formLayout_2.setWidget(11, QFormLayout.ItemRole.SpanningRole, self.frame_4)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.formLayout_2.setItem(10, QFormLayout.ItemRole.SpanningRole, self.verticalSpacer)

        self.label_18 = QLabel(self.groupBox_2)
        self.label_18.setObjectName(u"label_18")

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_18)

        self.stud_material_comboBox = QComboBox(self.groupBox_2)
        self.stud_material_comboBox.setObjectName(u"stud_material_comboBox")

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.FieldRole, self.stud_material_comboBox)


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
        self.groupBox.setTitle(QCoreApplication.translate("Dialog", u"Stud Sections", None))
        self.material_filter_checkBox.setText(QCoreApplication.translate("Dialog", u"Filter By Material:", None))
        self.new_stud_pushButton.setText(QCoreApplication.translate("Dialog", u"New", None))
        self.delete_stud_pushButton.setText(QCoreApplication.translate("Dialog", u"Delete", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("Dialog", u"Stud Properties", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"Name:", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"Width:", None))
        self.label_3.setText(QCoreApplication.translate("Dialog", u"Depth:", None))
        self.label_7.setText(QCoreApplication.translate("Dialog", u"Plys", None))
        self.label_8.setText(QCoreApplication.translate("Dialog", u"Ag:", None))
        self.stud_area_label.setText(QCoreApplication.translate("Dialog", u"TextLabel", None))
        self.label_10.setText(QCoreApplication.translate("Dialog", u"Ix:", None))
        self.stud_ix_label.setText(QCoreApplication.translate("Dialog", u"TextLabel", None))
        self.label_12.setText(QCoreApplication.translate("Dialog", u"Iy:", None))
        self.stud_iy_label.setText(QCoreApplication.translate("Dialog", u"TextLabel", None))
        self.label_14.setText(QCoreApplication.translate("Dialog", u"Sx:", None))
        self.stud_sx_label.setText(QCoreApplication.translate("Dialog", u"TextLabel", None))
        self.label_16.setText(QCoreApplication.translate("Dialog", u"Sy:", None))
        self.stud_sy_label.setText(QCoreApplication.translate("Dialog", u"TextLabel", None))
        self.save_stud_pushButton.setText(QCoreApplication.translate("Dialog", u"Save", None))
        self.label_18.setText(QCoreApplication.translate("Dialog", u"Material:", None))
        self.ok_pushButton.setText(QCoreApplication.translate("Dialog", u"OK", None))
        self.cancel_pushButton.setText(QCoreApplication.translate("Dialog", u"Cencel", None))
    # retranslateUi

