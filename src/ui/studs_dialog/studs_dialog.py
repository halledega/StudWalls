"""
This module contains the logic for the Studs dialog window.
"""

from PySide6 import QtCore as Qtc, QtWidgets as Qtw, QtGui as Qtg
from src.ui.studs_dialog.studs_ui.studs_dialog import Ui_Dialog
from src.models.stud import Stud
from src.models.section import Section
from src.models.wood import Wood

class StudsDialog(Qtw.QDialog, Ui_Dialog):
    """
    Manages the user interface for creating, editing, and deleting stud types.
    """
    def __init__(self, db_session):
        """
        Initializes the StudsDialog.

        Args:
            db_session: The SQLAlchemy session for database interaction.
        """
        super().__init__()
        self.setupUi(self)
        self.db_session = db_session

        self.model = Qtg.QStandardItemModel()
        self.stud_sections_listView.setModel(self.model)

        self.setup_connections()
        self.populate_filters()
        self.populate_studs_list()

        self.material_filter_comboBox.setEnabled(self.material_filter_checkBox.isChecked())

    def setup_connections(self):
        """Connects widget signals to their corresponding slots."""
        self.new_stud_pushButton.clicked.connect(self.new_stud)
        self.delete_stud_pushButton.clicked.connect(self.delete_stud)
        self.save_stud_pushButton.clicked.connect(self.save_stud)
        self.stud_sections_listView.selectionModel().selectionChanged.connect(self.on_stud_selected)
        self.ok_pushButton.clicked.connect(self.accept)
        self.cancel_pushButton.clicked.connect(self.reject)

        self.material_filter_checkBox.stateChanged.connect(self.filter_studs)
        self.material_filter_comboBox.currentIndexChanged.connect(self.filter_studs)

        self.stud_width_lineEdit.textChanged.connect(self.update_section_properties)
        self.stud_deoth_lineEdit.textChanged.connect(self.update_section_properties)
        self.number_of_ply_spinBox.valueChanged.connect(self.update_section_properties)

    def populate_filters(self):
        """Populates the filter comboboxes with available materials."""
        self.material_filter_comboBox.addItem("All")
        materials = self.db_session.query(Wood).order_by(Wood.name).all()
        for material in materials:
            self.material_filter_comboBox.addItem(material.name, userData=material.id)
        self.stud_material_comboBox.addItems([m.name for m in materials])

    def populate_studs_list(self):
        """Populates the main list view with studs, applying any active filters."""
        self.model.clear()
        query = self.db_session.query(Stud)

        if self.material_filter_checkBox.isChecked():
            material_id = self.material_filter_comboBox.currentData()
            if material_id:
                query = query.filter(Stud.material_id == material_id)

        studs = query.order_by(Stud.name).all()
        for stud in studs:
            item = Qtg.QStandardItem(stud.name)
            item.setData(stud.id, Qtc.Qt.ItemDataRole.UserRole)
            self.model.appendRow(item)

    def filter_studs(self):
        """Slot to re-populate the studs list when a filter changes."""
        self.material_filter_comboBox.setEnabled(self.material_filter_checkBox.isChecked())
        self.populate_studs_list()

    def new_stud(self):
        """Clears the input fields to prepare for creating a new stud."""
        self.stud_sections_listView.clearSelection()
        self.stud_name_lineEdit.clear()
        self.stud_material_comboBox.setCurrentIndex(-1)
        self.stud_width_lineEdit.clear()
        self.stud_deoth_lineEdit.clear()
        self.number_of_ply_spinBox.setValue(1)
        self.clear_section_properties()
        self.stud_name_lineEdit.setFocus()

    def on_stud_selected(self, selected, deselected):
        """Populates the input fields when a stud is selected from the list."""
        if selected.indexes():
            item = self.model.itemFromIndex(selected.indexes()[0])
            stud_id = item.data(Qtc.Qt.ItemDataRole.UserRole)
            stud = self.db_session.query(Stud).get(stud_id)
            if stud:
                self.stud_name_lineEdit.setText(stud.name)
                self.stud_material_comboBox.setCurrentText(stud.material.name)
                self.stud_width_lineEdit.setText(str(stud.section.width))
                self.stud_deoth_lineEdit.setText(str(stud.section.depth))
                self.number_of_ply_spinBox.setValue(stud.section.plys)
                self.update_section_properties()
        else:
            self.new_stud()

    def save_stud(self):
        """Saves the current stud (new or existing) to the database."""
        name = self.stud_name_lineEdit.text().strip()
        if not name:
            Qtw.QMessageBox.warning(self, "Input Error", "Stud name cannot be empty.")
            return

        selected_indexes = self.stud_sections_listView.selectedIndexes()
        
        query = self.db_session.query(Stud).filter(Stud.name == name)
        if selected_indexes:
            item = self.model.itemFromIndex(selected_indexes[0])
            stud_id = item.data(Qtc.Qt.ItemDataRole.UserRole)
            query = query.filter(Stud.id != stud_id)
        
        if query.first():
            Qtw.QMessageBox.warning(self, "Input Error", f"A stud with the name '{name}' already exists.")
            return

        try:
            width = float(self.stud_width_lineEdit.text())
            depth = float(self.stud_deoth_lineEdit.text())
            plys = self.number_of_ply_spinBox.value()
        except ValueError:
            Qtw.QMessageBox.warning(self, "Input Error", "Please enter valid numbers for width and depth.")
            return

        material_name = self.stud_material_comboBox.currentText()
        material = self.db_session.query(Wood).filter_by(name=material_name).first()
        if not material:
            Qtw.QMessageBox.warning(self, "Input Error", "Please select a valid material.")
            return

        if selected_indexes:
            stud = self.db_session.query(Stud).get(stud_id)
            section = stud.section
        else:
            stud = Stud()
            section = Section()
            stud.section = section

        stud.name = name
        stud.material = material
        section.width = width
        section.depth = depth
        section.plys = plys

        self.db_session.add(stud)
        self.db_session.commit()
        self.populate_studs_list()

        for row in range(self.model.rowCount()):
            item = self.model.item(row)
            if item.data(Qtc.Qt.ItemDataRole.UserRole) == stud.id:
                self.stud_sections_listView.setCurrentIndex(self.model.indexFromItem(item))
                break

    def delete_stud(self):
        """Deletes the selected stud from the database."""
        selected_indexes = self.stud_sections_listView.selectedIndexes()
        if selected_indexes:
            item = self.model.itemFromIndex(selected_indexes[0])
            stud_id = item.data(Qtc.Qt.ItemDataRole.UserRole)
            
            reply = Qtw.QMessageBox.question(self, "Delete Stud",
                                           f"Are you sure you want to delete this stud?",
                                           Qtw.QMessageBox.StandardButton.Yes | Qtw.QMessageBox.StandardButton.No,
                                           Qtw.QMessageBox.StandardButton.No)

            if reply == Qtw.QMessageBox.StandardButton.Yes:
                stud = self.db_session.query(Stud).get(stud_id)
                if stud:
                    self.db_session.delete(stud.section) # Also deletes the section
                    self.db_session.delete(stud)
                    self.db_session.commit()
                    self.populate_studs_list()

    def update_section_properties(self):
        """Recalculates and displays the section properties based on the input fields."""
        try:
            width = float(self.stud_width_lineEdit.text())
            depth = float(self.stud_deoth_lineEdit.text())
            plys = self.number_of_ply_spinBox.value()
            
            temp_section = Section(width=width, depth=depth, plys=plys)

            self.stud_area_label.setText(f"{temp_section.Ag:.2f}")
            self.stud_ix_label.setText(f"{temp_section.Ix:.2f}")
            self.stud_iy_label.setText(f"{temp_section.Iy:.2f}")
            self.stud_sx_label.setText(f"{temp_section.Sx:.2f}")
            self.stud_sy_label.setText(f"{temp_section.Sy:.2f}")
        except ValueError:
            self.clear_section_properties()

    def clear_section_properties(self):
        """Clears the calculated section property labels."""
        self.stud_area_label.setText("")
        self.stud_ix_label.setText("")
        self.stud_iy_label.setText("")
        self.stud_sx_label.setText("")
        self.stud_sy_label.setText("")