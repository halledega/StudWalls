# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'materials_dialog.load_combos_ui'
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
    QPushButton, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)

class Ui_materials_Dialog(object):
    def setupUi(self, materials_Dialog):
        if not materials_Dialog.objectName():
            materials_Dialog.setObjectName(u"materials_Dialog")
        materials_Dialog.resize(511, 493)
        self.gridLayout = QGridLayout(materials_Dialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.groupBox = QGroupBox(materials_Dialog)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout = QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.frame_2 = QFrame(self.groupBox)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)
        self.formLayout_3 = QFormLayout(self.frame_2)
        self.formLayout_3.setObjectName(u"formLayout_3")
        self.category_filter_checkBox = QCheckBox(self.frame_2)
        self.category_filter_checkBox.setObjectName(u"category_filter_checkBox")

        self.formLayout_3.setWidget(0, QFormLayout.ItemRole.LabelRole, self.category_filter_checkBox)

        self.category_filter_comboBox = QComboBox(self.frame_2)
        self.category_filter_comboBox.setObjectName(u"category_filter_comboBox")

        self.formLayout_3.setWidget(0, QFormLayout.ItemRole.FieldRole, self.category_filter_comboBox)

        self.species_filter_comboBox = QComboBox(self.frame_2)
        self.species_filter_comboBox.setObjectName(u"species_filter_comboBox")

        self.formLayout_3.setWidget(1, QFormLayout.ItemRole.FieldRole, self.species_filter_comboBox)

        self.species_filter_checkBox = QCheckBox(self.frame_2)
        self.species_filter_checkBox.setObjectName(u"species_filter_checkBox")

        self.formLayout_3.setWidget(1, QFormLayout.ItemRole.LabelRole, self.species_filter_checkBox)


        self.verticalLayout.addWidget(self.frame_2)

        self.materials_listView = QListView(self.groupBox)
        self.materials_listView.setObjectName(u"materials_listView")

        self.verticalLayout.addWidget(self.materials_listView)

        self.frame_3 = QFrame(self.groupBox)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frame_3)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.new_material_pushButton = QPushButton(self.frame_3)
        self.new_material_pushButton.setObjectName(u"new_material_pushButton")

        self.horizontalLayout_2.addWidget(self.new_material_pushButton)

        self.delete_material_pushButton = QPushButton(self.frame_3)
        self.delete_material_pushButton.setObjectName(u"delete_material_pushButton")

        self.horizontalLayout_2.addWidget(self.delete_material_pushButton)


        self.verticalLayout.addWidget(self.frame_3)


        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 1)

        self.groupBox_2 = QGroupBox(materials_Dialog)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.formLayout = QFormLayout(self.groupBox_2)
        self.formLayout.setObjectName(u"formLayout")
        self.label_7 = QLabel(self.groupBox_2)
        self.label_7.setObjectName(u"label_7")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_7)

        self.material_name_lineEdit = QLineEdit(self.groupBox_2)
        self.material_name_lineEdit.setObjectName(u"material_name_lineEdit")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.material_name_lineEdit)

        self.label_8 = QLabel(self.groupBox_2)
        self.label_8.setObjectName(u"label_8")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_8)

        self.material_category_comboBox = QComboBox(self.groupBox_2)
        self.material_category_comboBox.setObjectName(u"material_category_comboBox")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.material_category_comboBox)

        self.label_9 = QLabel(self.groupBox_2)
        self.label_9.setObjectName(u"label_9")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_9)

        self.material_species_comboBox = QComboBox(self.groupBox_2)
        self.material_species_comboBox.setObjectName(u"material_species_comboBox")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.material_species_comboBox)

        self.label_10 = QLabel(self.groupBox_2)
        self.label_10.setObjectName(u"label_10")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_10)

        self.material_type_comboBox = QComboBox(self.groupBox_2)
        self.material_type_comboBox.setObjectName(u"material_type_comboBox")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.material_type_comboBox)

        self.label_11 = QLabel(self.groupBox_2)
        self.label_11.setObjectName(u"label_11")

        self.formLayout.setWidget(4, QFormLayout.ItemRole.LabelRole, self.label_11)

        self.material_grade_comboBox = QComboBox(self.groupBox_2)
        self.material_grade_comboBox.setObjectName(u"material_grade_comboBox")

        self.formLayout.setWidget(4, QFormLayout.ItemRole.FieldRole, self.material_grade_comboBox)

        self.label = QLabel(self.groupBox_2)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(5, QFormLayout.ItemRole.LabelRole, self.label)

        self.material_fb_lineEdit = QLineEdit(self.groupBox_2)
        self.material_fb_lineEdit.setObjectName(u"material_fb_lineEdit")

        self.formLayout.setWidget(5, QFormLayout.ItemRole.FieldRole, self.material_fb_lineEdit)

        self.label_2 = QLabel(self.groupBox_2)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(6, QFormLayout.ItemRole.LabelRole, self.label_2)

        self.material_fv_lineEdit = QLineEdit(self.groupBox_2)
        self.material_fv_lineEdit.setObjectName(u"material_fv_lineEdit")

        self.formLayout.setWidget(6, QFormLayout.ItemRole.FieldRole, self.material_fv_lineEdit)

        self.label_3 = QLabel(self.groupBox_2)
        self.label_3.setObjectName(u"label_3")

        self.formLayout.setWidget(7, QFormLayout.ItemRole.LabelRole, self.label_3)

        self.material_fc_lineEdit = QLineEdit(self.groupBox_2)
        self.material_fc_lineEdit.setObjectName(u"material_fc_lineEdit")

        self.formLayout.setWidget(7, QFormLayout.ItemRole.FieldRole, self.material_fc_lineEdit)

        self.label_4 = QLabel(self.groupBox_2)
        self.label_4.setObjectName(u"label_4")

        self.formLayout.setWidget(8, QFormLayout.ItemRole.LabelRole, self.label_4)

        self.meterial_fcp_lineEdit = QLineEdit(self.groupBox_2)
        self.meterial_fcp_lineEdit.setObjectName(u"meterial_fcp_lineEdit")

        self.formLayout.setWidget(8, QFormLayout.ItemRole.FieldRole, self.meterial_fcp_lineEdit)

        self.label_5 = QLabel(self.groupBox_2)
        self.label_5.setObjectName(u"label_5")

        self.formLayout.setWidget(9, QFormLayout.ItemRole.LabelRole, self.label_5)

        self.material_ft_lineEdit = QLineEdit(self.groupBox_2)
        self.material_ft_lineEdit.setObjectName(u"material_ft_lineEdit")

        self.formLayout.setWidget(9, QFormLayout.ItemRole.FieldRole, self.material_ft_lineEdit)

        self.label_6 = QLabel(self.groupBox_2)
        self.label_6.setObjectName(u"label_6")

        self.formLayout.setWidget(10, QFormLayout.ItemRole.LabelRole, self.label_6)

        self.meterial_e_lineEdit = QLineEdit(self.groupBox_2)
        self.meterial_e_lineEdit.setObjectName(u"meterial_e_lineEdit")

        self.formLayout.setWidget(10, QFormLayout.ItemRole.FieldRole, self.meterial_e_lineEdit)

        self.frame_4 = QFrame(self.groupBox_2)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_4.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frame_4)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_3)

        self.save_material_pushButton = QPushButton(self.frame_4)
        self.save_material_pushButton.setObjectName(u"save_material_pushButton")

        self.horizontalLayout_3.addWidget(self.save_material_pushButton)


        self.formLayout.setWidget(16, QFormLayout.ItemRole.SpanningRole, self.frame_4)


        self.gridLayout.addWidget(self.groupBox_2, 0, 1, 1, 1)

        self.frame = QFrame(materials_Dialog)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.ok_pushButton = QPushButton(self.frame)
        self.ok_pushButton.setObjectName(u"ok_pushButton")

        self.horizontalLayout.addWidget(self.ok_pushButton)

        self.cancel_pushButton = QPushButton(self.frame)
        self.cancel_pushButton.setObjectName(u"cancel_pushButton")

        self.horizontalLayout.addWidget(self.cancel_pushButton)


        self.gridLayout.addWidget(self.frame, 1, 0, 1, 2)


        self.retranslateUi(materials_Dialog)

        QMetaObject.connectSlotsByName(materials_Dialog)
    # setupUi

    def retranslateUi(self, materials_Dialog):
        materials_Dialog.setWindowTitle(QCoreApplication.translate("materials_Dialog", u"Materials", None))
        self.groupBox.setTitle(QCoreApplication.translate("materials_Dialog", u"Available Materials", None))
        self.category_filter_checkBox.setText(QCoreApplication.translate("materials_Dialog", u"Filter By Category:", None))
        self.species_filter_checkBox.setText(QCoreApplication.translate("materials_Dialog", u"Filter by Species:", None))
        self.new_material_pushButton.setText(QCoreApplication.translate("materials_Dialog", u"New", None))
        self.delete_material_pushButton.setText(QCoreApplication.translate("materials_Dialog", u"Delete", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("materials_Dialog", u"Material Properties", None))
        self.label_7.setText(QCoreApplication.translate("materials_Dialog", u"Name:", None))
        self.label_8.setText(QCoreApplication.translate("materials_Dialog", u"Category:", None))
        self.label_9.setText(QCoreApplication.translate("materials_Dialog", u"Species:", None))
        self.label_10.setText(QCoreApplication.translate("materials_Dialog", u"Type:", None))
        self.label_11.setText(QCoreApplication.translate("materials_Dialog", u"Grade:", None))
        self.label.setText(QCoreApplication.translate("materials_Dialog", u"fb:", None))
        self.label_2.setText(QCoreApplication.translate("materials_Dialog", u"fv:", None))
        self.label_3.setText(QCoreApplication.translate("materials_Dialog", u"fc:", None))
        self.label_4.setText(QCoreApplication.translate("materials_Dialog", u"fcp:", None))
        self.label_5.setText(QCoreApplication.translate("materials_Dialog", u"Ft", None))
        self.label_6.setText(QCoreApplication.translate("materials_Dialog", u"E05:", None))
        self.save_material_pushButton.setText(QCoreApplication.translate("materials_Dialog", u"Save", None))
        self.ok_pushButton.setText(QCoreApplication.translate("materials_Dialog", u"OK", None))
        self.cancel_pushButton.setText(QCoreApplication.translate("materials_Dialog", u"Cancel", None))
    # retranslateUi

