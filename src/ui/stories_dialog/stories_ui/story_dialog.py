# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'story_dialog.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QGraphicsView, QGridLayout,
    QGroupBox, QHeaderView, QPushButton, QSizePolicy,
    QSpacerItem, QTableView, QVBoxLayout, QWidget)

class Ui_stories_Dialog(object):
    def setupUi(self, stories_Dialog):
        if not stories_Dialog.objectName():
            stories_Dialog.setObjectName(u"stories_Dialog")
        stories_Dialog.resize(800, 480)
        self.gridLayout_2 = QGridLayout(stories_Dialog)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.groupBox = QGroupBox(stories_Dialog)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setMinimumSize(QSize(400, 0))
        self.groupBox.setMaximumSize(QSize(400, 16777215))
        self.gridLayout = QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.levels_tableView = QTableView(self.groupBox)
        self.levels_tableView.setObjectName(u"levels_tableView")

        self.gridLayout.addWidget(self.levels_tableView, 0, 0, 1, 3)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 2, 1, 1, 1)

        self.delete_level_pushButton = QPushButton(self.groupBox)
        self.delete_level_pushButton.setObjectName(u"delete_level_pushButton")

        self.gridLayout.addWidget(self.delete_level_pushButton, 1, 2, 1, 1)

        self.add_level_pushButton = QPushButton(self.groupBox)
        self.add_level_pushButton.setObjectName(u"add_level_pushButton")

        self.gridLayout.addWidget(self.add_level_pushButton, 1, 1, 1, 1)


        self.gridLayout_2.addWidget(self.groupBox, 0, 1, 1, 1)

        self.pushButton = QPushButton(stories_Dialog)
        self.pushButton.setObjectName(u"pushButton")

        self.gridLayout_2.addWidget(self.pushButton, 1, 3, 1, 1)

        self.pushButton_2 = QPushButton(stories_Dialog)
        self.pushButton_2.setObjectName(u"pushButton_2")

        self.gridLayout_2.addWidget(self.pushButton_2, 1, 4, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer, 1, 2, 1, 1)

        self.groupBox_2 = QGroupBox(stories_Dialog)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.verticalLayout = QVBoxLayout(self.groupBox_2)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.graphicsView = QGraphicsView(self.groupBox_2)
        self.graphicsView.setObjectName(u"graphicsView")

        self.verticalLayout.addWidget(self.graphicsView)


        self.gridLayout_2.addWidget(self.groupBox_2, 0, 2, 1, 3)


        self.retranslateUi(stories_Dialog)

        QMetaObject.connectSlotsByName(stories_Dialog)
    # setupUi

    def retranslateUi(self, stories_Dialog):
        stories_Dialog.setWindowTitle(QCoreApplication.translate("stories_Dialog", u"Add/Edit Levels", None))
        self.groupBox.setTitle(QCoreApplication.translate("stories_Dialog", u"Add/Edit Levels", None))
        self.delete_level_pushButton.setText(QCoreApplication.translate("stories_Dialog", u"Delete Level", None))
        self.add_level_pushButton.setText(QCoreApplication.translate("stories_Dialog", u"Add Level", None))
        self.pushButton.setText(QCoreApplication.translate("stories_Dialog", u"OK", None))
        self.pushButton_2.setText(QCoreApplication.translate("stories_Dialog", u"Cancel", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("stories_Dialog", u"Legend", None))
    # retranslateUi

