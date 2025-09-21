"""
This module contains the logic for the Loads dialog window, allowing users
to manage the basic loads available in the project.
"""

from PySide6 import QtCore as Qtc, QtWidgets as Qtw
from src.ui.loads_dialog.loads_ui.loads_dialog import Ui_loads_Dialog
from src.models.loads import Load, LoadCase

class LoadsDialog(Qtw.QDialog, Ui_loads_Dialog):
    """
    Manages the user interface for creating, editing, and deleting loads.

    This dialog uses a QTableView with a custom model to display and manage
    all the Load objects in the current project's database.
    """
    def __init__(self, db_session):
        """
        Initializes the LoadsDialog.

        Args:
            db_session: The SQLAlchemy session for database interaction.
        """
        super().__init__()
        self.setupUi(self)
        self.db_session = db_session

        self.setup_table()
        # Populate the combo box with all available load cases from the Enum.
        self.load_case_comboBox.addItems([case.name for case in LoadCase])

        # Connect button signals to their respective slots.
        self.add_load_pushButton.clicked.connect(self.add_load)
        self.edit_load_pushButton.clicked.connect(self.edit_load)
        self.delete_load_pushButton.clicked.connect(self.delete_load)
        self.ok_pushButton.clicked.connect(self.accept)
        self.cancel_pushButton.clicked.connect(self.reject)

        # When the table selection changes, populate the input fields on the right.
        self.loads_tableView.selectionModel().selectionChanged.connect(self.populate_fields)

    def setup_table(self):
        """Initializes and sets the custom table model for the loads view."""
        self.table_model = LoadTableModel(self.db_session)
        self.loads_tableView.setModel(self.table_model)
        self.loads_tableView.verticalHeader().hide()
        header = self.loads_tableView.horizontalHeader()
        header.setSectionResizeMode(Qtw.QHeaderView.ResizeMode.Stretch)

    def populate_fields(self, selected):
        """
        Populates the input fields with data from the selected table row.

        Args:
            selected: The QItemSelection object from the selection model's signal.
        """
        if not selected.indexes():
            self.load_name_lineEdit.clear()
            self.load_value_lineEdit.clear()
            return
        
        row = selected.indexes()[0].row()
        self.load_name_lineEdit.setText(self.table_model.index(row, 0).data())
        self.load_case_comboBox.setCurrentText(self.table_model.index(row, 1).data())
        self.load_value_lineEdit.setText(str(self.table_model.index(row, 2).data()))

    def add_load(self):
        """Adds a new load to the database using the data from the input fields."""
        name = self.load_name_lineEdit.text()
        case = self.load_case_comboBox.currentText()
        try:
            value = float(self.load_value_lineEdit.text())
        except ValueError:
            Qtw.QMessageBox.warning(self, "Invalid Input", "Please enter a valid number for the load value.")
            return

        if name and case and value is not None:
            # The insertRow method on the model handles both adding the data to the
            # internal list and committing it to the database.
            self.table_model.insertRow(self.table_model.rowCount(), name, case, value)
            self.load_name_lineEdit.clear()
            self.load_value_lineEdit.clear()
            self.loads_tableView.clearSelection()

    def edit_load(self):
        """Edits the selected load in the database with the new data."""
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
                # The setData method on the model handles both updating the internal
                # data and committing the change to the database.
                self.table_model.setData(self.table_model.index(selected_row, 0), name, Qtc.Qt.ItemDataRole.EditRole)
                self.table_model.setData(self.table_model.index(selected_row, 1), case, Qtc.Qt.ItemDataRole.EditRole)
                self.table_model.setData(self.table_model.index(selected_row, 2), value, Qtc.Qt.ItemDataRole.EditRole)
                self.load_name_lineEdit.clear()
                self.load_value_lineEdit.clear()
                self.loads_tableView.clearSelection()

    def delete_load(self):
        """Deletes the selected load from the database."""
        selected_row = self.loads_tableView.currentIndex().row()
        if selected_row >= 0:
            self.table_model.removeRow(selected_row)

class LoadTableModel(Qtc.QAbstractTableModel):
    """
    A custom table model for managing Load objects.

    This model provides the interface between the QTableView and the list of
    SQLAlchemy Load objects. It handles fetching data, updating the database,
    inserting new rows, and deleting rows.
    """
    def __init__(self, db_session):
        super().__init__()
        self.db_session = db_session
        self._loads = self.db_session.query(Load).all()
        self._headers = ["Name", "Case", "Value", "Type"]

    def rowCount(self, parent=Qtc.QModelIndex()):
        """Returns the number of rows in the model."""
        return len(self._loads)

    def columnCount(self, parent=Qtc.QModelIndex()):
        """Returns the number of columns."""
        return len(self._headers)

    def headerData(self, section, orientation, role):
        """Returns the data for the headers."""
        if role == Qtc.Qt.ItemDataRole.DisplayRole and orientation == Qtc.Qt.Orientation.Horizontal:
            return self._headers[section]

    def data(self, index, role):
        """
        Returns the data to be displayed in a cell.
        SQLAlchemy objects are accessed here to provide the data.
        """
        if role == Qtc.Qt.ItemDataRole.DisplayRole or role == Qtc.Qt.ItemDataRole.EditRole:
            load = self._loads[index.row()]
            column = index.column()
            if column == 0: return load.name
            elif column == 1: return load.case
            elif column == 2: return load.value
            elif column == 3: return load.load_type

    def setData(self, index, value, role):
        """
        Called when a cell is edited by the user. This method updates the
        SQLAlchemy object and commits the change to the database.
        """
        if role == Qtc.Qt.ItemDataRole.EditRole:
            load = self._loads[index.row()]
            column = index.column()
            try:
                if column == 0: load.name = value
                elif column == 1: load.case = value
                elif column == 2: load.value = float(value)
                elif column == 3: load.load_type = value
                self.db_session.commit()
                self.dataChanged.emit(index, index) # Notify views of the change
                return True
            except ValueError:
                self.db_session.rollback() # Rollback on error
                return False
        return False

    def flags(self, index):
        """Enables editing for all cells."""
        return super().flags(index) | Qtc.Qt.ItemFlag.ItemIsEditable

    def insertRow(self, row, name, case, value, parent=Qtc.QModelIndex()):
        """
        Inserts a new row into the model and a new record into the database.
        """
        self.beginInsertRows(parent, row, row) # Notify views of the upcoming insertion
        new_load = Load(name=name, case=case, value=value, load_type="Area")
        self.db_session.add(new_load)
        self.db_session.commit()
        self._loads.append(new_load)
        self.endInsertRows() # Finalize the insertion
        return True

    def removeRow(self, row, parent=Qtc.QModelIndex()):
        """
        Removes a row from the model and the corresponding record from the database.
        """
        self.beginRemoveRows(parent, row, row) # Notify views
        load_to_delete = self._loads[row]
        self.db_session.delete(load_to_delete)
        self.db_session.commit()
        del self._loads[row]
        self.endRemoveRows() # Finalize removal
        return True