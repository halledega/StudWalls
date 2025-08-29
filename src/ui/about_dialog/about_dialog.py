from PySide6 import QtWidgets as Qtw
from .about_ui.about_dialog import Ui_AboutDialog

class AboutDialog(Qtw.QDialog, Ui_AboutDialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.setWindowTitle("About StudWalls")
        self.labelTitle.setText("StudWalls")
        self.labelVersion.setText("Version 0.1.0")
        self.buttonBox.accepted.connect(self.accept)
