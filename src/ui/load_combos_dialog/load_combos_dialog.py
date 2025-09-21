"""
This module contains the logic for the Load Combinations dialog window.

This dialog allows users to create, edit, and delete load combinations for the project.
"""

from PySide6 import QtCore as Qtc, QtWidgets as Qtw, QtGui as Qtg
from src.ui.load_combos_dialog.load_combos_ui.load_combos_dialog import Ui_Dialog
from src.models.load_combination import LoadCombination, LoadCombinationItem
from src.models.loads import Load


class LoadCombosDialog(Qtw.QDialog, Ui_Dialog):
    """
    Manages the user interface for creating and editing load combinations.

    This dialog displays a list of all available load combinations. When a combination
    is selected, its details (name and constituent load cases with factors) are shown
    in a table view, allowing for editing.
    """
    def __init__(self, db_session):
        """
        Initializes the LoadCombosDialog.

        Args:
            db_session: The SQLAlchemy session for database interaction.
        """
        super().__init__()
        self.setupUi(self)
        self.db_session = db_session
        self.loads = self.db_session.query(Load).all()

        # --- Model Setup ---
        # The list view on the left uses a QStandardItemModel to display the names
        # of the load combinations.
        self.list_model = Qtg.QStandardItemModel()
        self.load_combinations_listView.setModel(self.list_model)

        # The table view on the right uses a custom model to handle the specific
        # data structure of load combination items.
        self.table_model = LoadCasesTableModel(self.db_session, self.loads)
        self.load_cases_tableView.setModel(self.table_model)
        self.load_cases_tableView.verticalHeader().hide()
        header = self.load_cases_tableView.horizontalHeader()
        header.setSectionResizeMode(Qtw.QHeaderView.ResizeMode.Stretch)

        # --- Delegate Setup ---
        # A custom delegate is required to place a QComboBox in the first column
        # of the table view for selecting the load case.
        delegate = LoadCaseDelegate(self.loads)
        self.load_cases_tableView.setItemDelegateForColumn(0, delegate)

        self.setup_connections()
        self.populate_load_combinations()

    def setup_connections(self):
        """Connects widget signals to their corresponding slots (methods)."""
        self.new_load_combination_pushButton.clicked.connect(self.new_load_combination)
        self.delete_load_combination_pushButton.clicked.connect(self.delete_load_combination)
        self.save_load_combiation_pushButton.clicked.connect(self.save_load_combination)
        
        # When the selection in the list view changes, update the details on the right.
        self.load_combinations_listView.selectionModel().selectionChanged.connect(self.on_load_combination_selected)

        # Connect buttons for adding/removing rows in the load case table.
        self.add_load_case_pushButton.clicked.connect(self.table_model.add_row)
        self.remove_load_case_pushButton.clicked.connect(self.remove_load_case_row)

        # Standard OK/Cancel button connections.
        self.ok_pushButton.clicked.connect(self.accept)
        self.cancel_pushButton.clicked.connect(self.reject)

    def populate_load_combinations(self):
        """Queries the database and populates the list view with load combinations."""
        self.list_model.clear()
        load_combos = self.db_session.query(LoadCombination).all()
        for combo in load_combos:
            item = Qtg.QStandardItem(combo.name)
            # Store the database ID in the item's UserRole. This is a standard Qt
            # practice for linking view items to underlying data objects without
            # displaying the ID to the user.
            item.setData(combo.id, Qtc.Qt.ItemDataRole.UserRole)
            self.list_model.appendRow(item)

    def on_load_combination_selected(self, selected, deselected):
        """
        Slot executed when a load combination is selected from the list.
        It populates the right-hand side of the dialog with the selected combo's details.
        """
        if not selected.indexes():
            self.load_combination_lineEdit.clear()
            self.table_model.set_load_combination(None)
            return

        # Retrieve the database ID from the selected item.
        item = self.list_model.itemFromIndex(selected.indexes()[0])
        combo_id = item.data(Qtc.Qt.ItemDataRole.UserRole)
        combo = self.db_session.query(LoadCombination).get(combo_id)

        if combo:
            self.load_combination_lineEdit.setText(combo.name)
            # Tell the table model to display the items for the selected combination.
            self.table_model.set_load_combination(combo)

    def new_load_combination(self):
        """Clears the input fields to allow for creation of a new load combination."""
        self.load_combinations_listView.clearSelection()
        self.load_combination_lineEdit.clear()
        self.table_model.set_load_combination(None)
        self.load_combination_lineEdit.setFocus()

    def delete_load_combination(self):
        """Deletes the currently selected load combination from the database."""
        selected = self.load_combinations_listView.selectedIndexes()
        if not selected:
            return

        item = self.list_model.itemFromIndex(selected[0])
        combo_id = item.data(Qtc.Qt.ItemDataRole.UserRole)
        combo = self.db_session.query(LoadCombination).get(combo_id)

        if combo:
            reply = Qtw.QMessageBox.question(self, "Delete Load Combination",
                                           f"Are you sure you want to delete '{combo.name}'?",
                                           Qtw.QMessageBox.StandardButton.Yes | Qtw.QMessageBox.StandardButton.No)
            if reply == Qtw.QMessageBox.StandardButton.Yes:
                self.db_session.delete(combo)
                self.db_session.commit()
                self.populate_load_combinations()
                self.new_load_combination()

    def save_load_combination(self):
        """
        Saves the current load combination (new or existing) to the database.
        """
        name = self.load_combination_lineEdit.text().strip()
        if not name:
            Qtw.QMessageBox.warning(self, "Input Error", "Load combination name cannot be empty.")
            return

        selected = self.load_combinations_listView.selectedIndexes()
        if selected:
            # If an item is selected, we are editing an existing combination.
            item = self.list_model.itemFromIndex(selected[0])
            combo_id = item.data(Qtc.Qt.ItemDataRole.UserRole)
            combo = self.db_session.query(LoadCombination).get(combo_id)
        else:
            # Otherwise, we are creating a new one.
            combo = LoadCombination()
            self.db_session.add(combo)

        combo.name = name
        # Delegate the saving of the table data to the table model.
        self.table_model.save_to_load_combination(combo)

        self.db_session.commit()
        self.populate_load_combinations()

        # Reselect the item that was just saved.
        for row in range(self.list_model.rowCount()):
            item = self.list_model.item(row)
            if item.data(Qtc.Qt.ItemDataRole.UserRole) == combo.id:
                self.load_combinations_listView.setCurrentIndex(self.list_model.indexFromItem(item))
                break

    def remove_load_case_row(self):
        """Removes the selected row from the load cases table."""
        selected_row = self.load_cases_tableView.currentIndex().row()
        if selected_row >= 0:
            self.table_model.removeRow(selected_row)


class LoadCasesTableModel(Qtc.QAbstractTableModel):
    """
    A custom table model for managing the load cases within a load combination.

    This model interfaces between the `QTableView` and the underlying data, which is
    a temporary list of dictionaries representing the load combination items.
    """
    def __init__(self, db_session, loads, parent=None):
        super().__init__(parent)
        self.db_session = db_session
        self.loads = loads # A list of all available Load objects
        self.load_combination = None # The currently displayed LoadCombination object
        self._data = [] # The internal data store for the table
        self._headers = ["Load Case", "Factor"]

    def rowCount(self, parent=Qtc.QModelIndex()):
        """Returns the number of rows in the model."""
        return len(self._data)

    def columnCount(self, parent=Qtc.QModelIndex()):
        """Returns the number of columns in the model."""
        return len(self._headers)

    def headerData(self, section, orientation, role):
        """Returns the header for the given section."""
        if role == Qtc.Qt.ItemDataRole.DisplayRole and orientation == Qtc.Qt.Orientation.Horizontal:
            return self._headers[section]

    def data(self, index, role):
        """
        Returns the data for a given index and role.
        This is the core method for providing data to the view.
        """
        if not index.isValid():
            return None

        row_data = self._data[index.row()]
        column = index.column()

        if role == Qtc.Qt.ItemDataRole.DisplayRole:
            if column == 0:
                return row_data['load'].name if row_data['load'] else ""
            elif column == 1:
                return str(row_data['factor'])

        elif role == Qtc.Qt.ItemDataRole.EditRole:
            # For editing, we provide the index for the combobox
            if column == 0:
                return self.loads.index(row_data['load']) if row_data['load'] in self.loads else -1
            elif column == 1:
                return str(row_data['factor'])

        return None

    def setData(self, index, value, role):
        """
        Sets the data for a given index. Called when the user edits a cell.
        """
        if role == Qtc.Qt.ItemDataRole.EditRole:
            row_data = self._data[index.row()]
            column = index.column()

            if column == 0: # The value from the delegate is the index of the selected load
                row_data['load'] = self.loads[value]
            elif column == 1:
                try:
                    row_data['factor'] = float(value)
                except (ValueError, TypeError):
                    return False

            self.dataChanged.emit(index, index)
            return True
        return False

    def flags(self, index):
        """Returns the flags for a given index, enabling editing."""
        return super().flags(index) | Qtc.Qt.ItemFlag.ItemIsEditable

    def set_load_combination(self, combo):
        """
        Updates the model's internal data to reflect the selected load combination.
        """
        self.beginResetModel() # Notifies views that the model is about to change drastically
        self.load_combination = combo
        self._data = []
        if combo:
            for item in combo.items:
                self._data.append({'load': item.load, 'factor': item.factor})
        self.endResetModel() # Notifies views that the model has changed

    def add_row(self):
        """Adds a new, empty row to the end of the model."""
        self.beginInsertRows(Qtc.QModelIndex(), self.rowCount(), self.rowCount())
        self._data.append({'load': None, 'factor': 1.0})
        self.endInsertRows()

    def removeRow(self, row, parent=Qtc.QModelIndex()):
        """Removes the specified row from the model."""
        self.beginRemoveRows(parent, row, row)
        del self._data[row]
        self.endRemoveRows()
        return True

    def save_to_load_combination(self, combo):
        """
        Saves the model's current data back to the SQLAlchemy LoadCombination object.
        """
        # Clear existing items to ensure a clean slate.
        combo.items.clear()

        # Add new items from the model's data.
        for row_data in self._data:
            if row_data['load']:
                combo.add_item(load=row_data['load'], factor=row_data['factor'])


class LoadCaseDelegate(Qtw.QStyledItemDelegate):
    """
    A custom delegate to render a QComboBox for editing load cases in the table view.
    """
    def __init__(self, loads, parent=None):
        super().__init__(parent)
        self.loads = loads

    def createEditor(self, parent, option, index):
        """Creates the QComboBox editor widget."""
        editor = Qtw.QComboBox(parent)
        for load in self.loads:
            editor.addItem(load.name)
        return editor

    def setEditorData(self, editor, index):
        """Sets the editor's current value from the model's data."""
        value = index.model().data(index, Qtc.Qt.ItemDataRole.EditRole)
        if value is not None:
            editor.setCurrentIndex(value)

    def setModelData(self, editor, model, index):
        """Saves the editor's current value back to the model."""
        model.setData(index, editor.currentIndex(), Qtc.Qt.ItemDataRole.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        """Ensures the editor widget is properly sized within the cell."""
        editor.setGeometry(option.rect)