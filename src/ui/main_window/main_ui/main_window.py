# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QAbstractSpinBox, QApplication, QComboBox, QDateEdit,
    QDockWidget, QFrame, QGraphicsView, QGridLayout,
    QHBoxLayout, QLabel, QLineEdit, QMainWindow,
    QMenu, QMenuBar, QPushButton, QSizePolicy,
    QSpacerItem, QStatusBar, QTabWidget, QTextEdit,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(919, 675)
        self.actionNew = QAction(MainWindow)
        self.actionNew.setObjectName(u"actionNew")
        self.actionOpen = QAction(MainWindow)
        self.actionOpen.setObjectName(u"actionOpen")
        self.actionSave = QAction(MainWindow)
        self.actionSave.setObjectName(u"actionSave")
        self.actionSave_As = QAction(MainWindow)
        self.actionSave_As.setObjectName(u"actionSave_As")
        self.actionPreferences = QAction(MainWindow)
        self.actionPreferences.setObjectName(u"actionPreferences")
        self.actionClose = QAction(MainWindow)
        self.actionClose.setObjectName(u"actionClose")
        self.actionMaterials = QAction(MainWindow)
        self.actionMaterials.setObjectName(u"actionMaterials")
        self.actionStuds = QAction(MainWindow)
        self.actionStuds.setObjectName(u"actionStuds")
        self.actionLoads = QAction(MainWindow)
        self.actionLoads.setObjectName(u"actionLoads")
        self.actionLoad_Combinations = QAction(MainWindow)
        self.actionLoad_Combinations.setObjectName(u"actionLoad_Combinations")
        self.actionLevels = QAction(MainWindow)
        self.actionLevels.setObjectName(u"actionLevels")
        self.actionAnalze_and_Code_Check = QAction(MainWindow)
        self.actionAnalze_and_Code_Check.setObjectName(u"actionAnalze_and_Code_Check")
        self.actionWalls = QAction(MainWindow)
        self.actionWalls.setObjectName(u"actionWalls")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout_3 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.main_graphicsView = QGraphicsView(self.centralwidget)
        self.main_graphicsView.setObjectName(u"main_graphicsView")

        self.horizontalLayout_3.addWidget(self.main_graphicsView)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 919, 23))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuEdit = QMenu(self.menubar)
        self.menuEdit.setObjectName(u"menuEdit")
        self.menuDefine = QMenu(self.menubar)
        self.menuDefine.setObjectName(u"menuDefine")
        self.menuRun = QMenu(self.menubar)
        self.menuRun.setObjectName(u"menuRun")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.dockWidget = QDockWidget(MainWindow)
        self.dockWidget.setObjectName(u"dockWidget")
        self.dockWidget.setMinimumSize(QSize(344, 514))
        self.dockWidget.setDockLocation(Qt.DockWidgetArea.LeftDockWidgetArea)
        self.dockWidgetContents = QWidget()
        self.dockWidgetContents.setObjectName(u"dockWidgetContents")
        self.horizontalLayout = QHBoxLayout(self.dockWidgetContents)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.main_tabWidget = QTabWidget(self.dockWidgetContents)
        self.main_tabWidget.setObjectName(u"main_tabWidget")
        self.main_tabWidget.setMinimumSize(QSize(0, 0))
        self.main_tabWidget.setMaximumSize(QSize(16777215, 16777215))
        self.main_tabWidget.setSizeIncrement(QSize(0, 0))
        self.project_info_tabWidgetPage = QWidget()
        self.project_info_tabWidgetPage.setObjectName(u"project_info_tabWidgetPage")
        self.gridLayout = QGridLayout(self.project_info_tabWidgetPage)
        self.gridLayout.setObjectName(u"gridLayout")
        self.line_2 = QFrame(self.project_info_tabWidgetPage)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout.addWidget(self.line_2, 12, 0, 1, 3)

        self.label_3 = QLabel(self.project_info_tabWidgetPage)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 5, 0, 1, 1)

        self.copy_wall_pushButton = QPushButton(self.project_info_tabWidgetPage)
        self.copy_wall_pushButton.setObjectName(u"copy_wall_pushButton")

        self.gridLayout.addWidget(self.copy_wall_pushButton, 14, 2, 1, 1)

        self.label_9 = QLabel(self.project_info_tabWidgetPage)
        self.label_9.setObjectName(u"label_9")

        self.gridLayout.addWidget(self.label_9, 11, 0, 1, 1)

        self.units_comboBox = QComboBox(self.project_info_tabWidgetPage)
        self.units_comboBox.setObjectName(u"units_comboBox")

        self.gridLayout.addWidget(self.units_comboBox, 11, 2, 1, 1)

        self.project_address_2_lineEdit = QLineEdit(self.project_info_tabWidgetPage)
        self.project_address_2_lineEdit.setObjectName(u"project_address_2_lineEdit")

        self.gridLayout.addWidget(self.project_address_2_lineEdit, 6, 2, 1, 1)

        self.label_8 = QLabel(self.project_info_tabWidgetPage)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout.addWidget(self.label_8, 3, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 18, 0, 1, 3)

        self.label = QLabel(self.project_info_tabWidgetPage)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 2, 0, 1, 1)

        self.line = QFrame(self.project_info_tabWidgetPage)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout.addWidget(self.line, 8, 0, 1, 3)

        self.wall_comboBox = QComboBox(self.project_info_tabWidgetPage)
        self.wall_comboBox.setObjectName(u"wall_comboBox")

        self.gridLayout.addWidget(self.wall_comboBox, 13, 2, 1, 1)

        self.new_wall_pushButton = QPushButton(self.project_info_tabWidgetPage)
        self.new_wall_pushButton.setObjectName(u"new_wall_pushButton")

        self.gridLayout.addWidget(self.new_wall_pushButton, 14, 0, 1, 1)

        self.label_2 = QLabel(self.project_info_tabWidgetPage)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 4, 0, 1, 1)

        self.label_10 = QLabel(self.project_info_tabWidgetPage)
        self.label_10.setObjectName(u"label_10")

        self.gridLayout.addWidget(self.label_10, 13, 0, 1, 1)

        self.project_number_lineEdit = QLineEdit(self.project_info_tabWidgetPage)
        self.project_number_lineEdit.setObjectName(u"project_number_lineEdit")

        self.gridLayout.addWidget(self.project_number_lineEdit, 2, 2, 1, 1)

        self.delete_wall_pushButton = QPushButton(self.project_info_tabWidgetPage)
        self.delete_wall_pushButton.setObjectName(u"delete_wall_pushButton")

        self.gridLayout.addWidget(self.delete_wall_pushButton, 14, 1, 1, 1)

        self.engineer_lineEdit = QLineEdit(self.project_info_tabWidgetPage)
        self.engineer_lineEdit.setObjectName(u"engineer_lineEdit")

        self.gridLayout.addWidget(self.engineer_lineEdit, 7, 2, 1, 1)

        self.label_4 = QLabel(self.project_info_tabWidgetPage)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 7, 0, 1, 1)

        self.project_name_lineEdit = QLineEdit(self.project_info_tabWidgetPage)
        self.project_name_lineEdit.setObjectName(u"project_name_lineEdit")

        self.gridLayout.addWidget(self.project_name_lineEdit, 4, 2, 1, 1)

        self.project_address_1_lineEdit = QLineEdit(self.project_info_tabWidgetPage)
        self.project_address_1_lineEdit.setObjectName(u"project_address_1_lineEdit")

        self.gridLayout.addWidget(self.project_address_1_lineEdit, 5, 2, 1, 1)

        self.line_3 = QFrame(self.project_info_tabWidgetPage)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShape(QFrame.Shape.HLine)
        self.line_3.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout.addWidget(self.line_3, 15, 0, 1, 3)

        self.run_pushButton = QPushButton(self.project_info_tabWidgetPage)
        self.run_pushButton.setObjectName(u"run_pushButton")

        self.gridLayout.addWidget(self.run_pushButton, 16, 0, 1, 1)

        self.result_summary_textEdit = QTextEdit(self.project_info_tabWidgetPage)
        self.result_summary_textEdit.setObjectName(u"result_summary_textEdit")
        self.result_summary_textEdit.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self.result_summary_textEdit.setReadOnly(True)

        self.gridLayout.addWidget(self.result_summary_textEdit, 17, 0, 1, 3)

        self.project_date_dateEdit = QDateEdit(self.project_info_tabWidgetPage)
        self.project_date_dateEdit.setObjectName(u"project_date_dateEdit")
        self.project_date_dateEdit.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.project_date_dateEdit.setCalendarPopup(True)

        self.gridLayout.addWidget(self.project_date_dateEdit, 3, 2, 1, 1)

        self.main_tabWidget.addTab(self.project_info_tabWidgetPage, "")
        self.results_tabWidgetPage = QWidget()
        self.results_tabWidgetPage.setObjectName(u"results_tabWidgetPage")
        self.horizontalLayout_2 = QHBoxLayout(self.results_tabWidgetPage)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.main_tabWidget.addTab(self.results_tabWidgetPage, "")

        self.horizontalLayout.addWidget(self.main_tabWidget)

        self.dockWidget.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dockWidget)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuDefine.menuAction())
        self.menubar.addAction(self.menuRun.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.actionNew)
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSave_As)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionPreferences)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionClose)
        self.menuDefine.addAction(self.actionLevels)
        self.menuDefine.addAction(self.actionLoads)
        self.menuDefine.addAction(self.actionLoad_Combinations)
        self.menuDefine.addAction(self.actionMaterials)
        self.menuDefine.addAction(self.actionStuds)
        self.menuDefine.addAction(self.actionWalls)
        self.menuRun.addAction(self.actionAnalze_and_Code_Check)

        self.retranslateUi(MainWindow)

        self.main_tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"StudWalls", None))
        self.actionNew.setText(QCoreApplication.translate("MainWindow", u"New", None))
        self.actionOpen.setText(QCoreApplication.translate("MainWindow", u"Open", None))
        self.actionSave.setText(QCoreApplication.translate("MainWindow", u"Save", None))
        self.actionSave_As.setText(QCoreApplication.translate("MainWindow", u"Save As", None))
        self.actionPreferences.setText(QCoreApplication.translate("MainWindow", u"Preferences", None))
        self.actionClose.setText(QCoreApplication.translate("MainWindow", u"Close", None))
        self.actionMaterials.setText(QCoreApplication.translate("MainWindow", u"Materials", None))
        self.actionStuds.setText(QCoreApplication.translate("MainWindow", u"Studs", None))
        self.actionLoads.setText(QCoreApplication.translate("MainWindow", u"Loads", None))
        self.actionLoad_Combinations.setText(QCoreApplication.translate("MainWindow", u"Load Combinations", None))
        self.actionLevels.setText(QCoreApplication.translate("MainWindow", u"Levels", None))
        self.actionAnalze_and_Code_Check.setText(QCoreApplication.translate("MainWindow", u"Analze and Code Check", None))
        self.actionWalls.setText(QCoreApplication.translate("MainWindow", u"Walls", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuEdit.setTitle(QCoreApplication.translate("MainWindow", u"Edit", None))
        self.menuDefine.setTitle(QCoreApplication.translate("MainWindow", u"Define", None))
        self.menuRun.setTitle(QCoreApplication.translate("MainWindow", u"Run", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"Help", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Poject Address:", None))
        self.copy_wall_pushButton.setText(QCoreApplication.translate("MainWindow", u"Copy Wall", None))
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"Units:", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"Date:", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Project Number:", None))
        self.new_wall_pushButton.setText(QCoreApplication.translate("MainWindow", u"New Wall", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Project Name:", None))
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"Wall:", None))
        self.delete_wall_pushButton.setText(QCoreApplication.translate("MainWindow", u"Delete Wall", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Engineer:", None))
        self.run_pushButton.setText(QCoreApplication.translate("MainWindow", u"Run", None))
        self.project_date_dateEdit.setDisplayFormat(QCoreApplication.translate("MainWindow", u"yyyy|mm|dd", None))
        self.main_tabWidget.setTabText(self.main_tabWidget.indexOf(self.project_info_tabWidgetPage), QCoreApplication.translate("MainWindow", u"Project", None))
        self.main_tabWidget.setTabText(self.main_tabWidget.indexOf(self.results_tabWidgetPage), QCoreApplication.translate("MainWindow", u"Results", None))
    # retranslateUi

