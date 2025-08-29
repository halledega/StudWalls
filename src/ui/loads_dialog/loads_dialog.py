
from PySide6 import QtCore as Qtc, QtWidgets as Qtw
from src.ui.loads_dialog.loads_ui.loads_dialog import Ui_loads_Dialog
from src.models.loads import Load, LoadCase

class LoadsDialog(Qtw.QDialog, Ui_loads_Dialog):
    def __init__(self, db_session):
        super().__init__()
        self.setupUi(self)
        self.db_session = db_session

        self.setup_table()
        self.load_case_comboBox.addItems([case.name for case in LoadCase])

        self.add_load_pushButton.clicked.connect(self.add_load)
        self.edit_load_pushButton.clicked.connect(self.edit_load)
        self.delete_load_pushButton.clicked.connect(self.delete_load)
        self.ok_pushButton.clicked.connect(self.accept)
        self.cancel_pushButton.clicked.connect(self.reject)

    def setup_table(self):
        self.table_model = LoadTableModel(self.db_session)
        self.loads_tableView.setModel(self.table_model)

    def add_load(self):
        name = self.load_name_lineEdit.text()
        case = self.load_case_comboBox.currentText()
        try:
            value = float(self.load_value_lineEdit.text())
        except ValueError:
            Qtw.QMessageBox.warning(self, "Invalid Input", "Please enter a valid number for the load value.")
            return

        if name and case and value is not None:
            self.table_model.insertRow(self.table_model.rowCount(), name, case, value)
            self.load_name_lineEdit.clear()
            self.load_value_lineEdit.clear()

    def edit_load(self):
        selected_row = self.loads_tableView.currentIndex().row()
        if selected_row >= 0:
            name = self.load_name_lineEdit.text()
            case = self.load_case_comboBox.currentText()
            try:
                value = float(self.load_value_lineEdit.text())
            except ValueError:
                Qtw.QMessageBox.warning(self, "Invalid Input", "Please enter a valid number for the load value.")
                return

            if name and case and value is not None:
                self.table_model.setData(self.table_model.index(selected_row, 0), name, Qtc.Qt.ItemDataRole.EditRole)
                self.table_model.setData(self.table_model.index(selected_row, 1), case, Qtc.Qt.ItemDataRole.EditRole)
                self.table_model.setData(self.table_model.index(selected_row, 2), value, Qtc.Qt.ItemDataRole.EditRole)

    def delete_load(self):
        selected_row = self.loads_tableView.currentIndex().row()
        if selected_row >= 0:
            self.table_model.removeRow(selected_row)

class LoadTableModel(Qtc.QAbstractTableModel):
    def __init__(self, db_session):
        super().__init__()
        self.db_session = db_session
        self._loads = self.db_session.query(Load).all()
        self._headers = ["Name", "Case", "Value", "Type"]

    def rowCount(self, parent=Qtc.QModelIndex()):
        return len(self._loads)

    def columnCount(self, parent=Qtc.QModelIndex()):
        return len(self._headers)

    def headerData(self, section, orientation, role):
        if role == Qtc.Qt.ItemDataRole.DisplayRole and orientation == Qtc.Qt.Orientation.Horizontal:
            return self._headers[section]

    def data(self, index, role):
        if role == Qtc.Qt.ItemDataRole.DisplayRole or role == Qtc.Qt.ItemDataRole.EditRole:
            load = self._loads[index.row()]
            column = index.column()
            if column == 0: return load.name
            elif column == 1: return load.case
            elif column == 2: return load.value
            elif column == 3: return load.load_type

    def setData(self, index, value, role):
        if role == Qtc.Qt.ItemDataRole.EditRole:
            load = self._loads[index.row()]
            column = index.column()
            try:
                if column == 0: load.name = value
                elif column == 1: load.case = value
                elif column == 2: load.value = float(value)
                elif column == 3: load.load_type = value
                self.db_session.commit()
                self.dataChanged.emit(index, index)
                return True
            except ValueError:
                self.db_session.rollback()
                return False
        return False

    def flags(self, index):
        return super().flags(index) | Qtc.Qt.ItemFlag.ItemIsEditable

    def insertRow(self, row, name, case, value, parent=Qtc.QModelIndex()):
        self.beginInsertRows(parent, row, row)
        new_load = Load(name=name, case=case, value=value, load_type="Area")
        self.db_session.add(new_load)
        self.db_session.commit()
        self._loads.append(new_load)
        self.endInsertRows()
        return True

    def removeRow(self, row, parent=Qtc.QModelIndex()):
        self.beginRemoveRows(parent, row, row)
        load_to_delete = self._loads[row]
        self.db_session.delete(load_to_delete)
        self.db_session.commit()
        del self._loads[row]
        self.endRemoveRows()
        return True
