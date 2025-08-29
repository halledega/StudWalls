from PySide6 import QtCore as Qtc, QtWidgets as Qtw, QtGui as Qtg
from src.ui.materials_dialog.materials_ui.materials_dialog import Ui_materials_Dialog
from src.models.wood import Wood

class MaterialsDialog(Qtw.QDialog, Ui_materials_Dialog):
    def __init__(self, db_session):
        super().__init__()
        # Place holder properties
        self.model = None

        self.setupUi(self)
        self.db_session = db_session

        self.setup_model()
        self.setup_connections()

        self.populate_filters()
        self.populate_property_combos()
        self.populate_materials_list()

        # Initial state for filters
        self.category_filter_comboBox.setEnabled(self.category_filter_checkBox.isChecked())
        self.species_filter_comboBox.setEnabled(self.species_filter_checkBox.isChecked())

    def setup_model(self):
        self.model = Qtg.QStandardItemModel()
        self.materials_listView.setModel(self.model)
        self.materials_listView.setSelectionMode(Qtw.QAbstractItemView.SelectionMode.SingleSelection)

    def setup_connections(self):
        self.save_material_pushButton.clicked.connect(self.save_material)
        self.new_material_pushButton.clicked.connect(self.new_material)
        self.delete_material_pushButton.clicked.connect(self.delete_material)
        self.materials_listView.selectionModel().selectionChanged.connect(self.on_material_selected)
        self.ok_pushButton.clicked.connect(self.accept)
        self.cancel_pushButton.clicked.connect(self.reject)

        # Filters
        self.category_filter_checkBox.stateChanged.connect(self.filter_materials)
        self.species_filter_checkBox.stateChanged.connect(self.filter_materials)
        self.category_filter_comboBox.currentIndexChanged.connect(self.filter_materials)
        self.species_filter_comboBox.currentIndexChanged.connect(self.filter_materials)

    def populate_filters(self):
        self.category_filter_comboBox.addItem("All")
        categories = [c[0] for c in self.db_session.query(Wood.category).distinct().all() if c[0]]
        self.category_filter_comboBox.addItems(categories)

        self.species_filter_comboBox.addItem("All")
        species = [s[0] for s in self.db_session.query(Wood.species).distinct().all() if s[0]]
        self.species_filter_comboBox.addItems(species)

    def populate_property_combos(self):
        categories = [c[0] for c in self.db_session.query(Wood.category).distinct().all() if c[0]]
        self.material_category_comboBox.addItems(categories)
        self.material_category_comboBox.setEditable(True)
        species = [s[0] for s in self.db_session.query(Wood.species).distinct().all() if s[0]]
        self.material_species_comboBox.addItems(species)
        self.material_species_comboBox.setEditable(True)
        types = [t[0] for t in self.db_session.query(Wood.material_type).distinct().all() if t[0]]
        self.material_type_comboBox.addItems(types)
        self.material_type_comboBox.setEditable(True)
        grades = [g[0] for g in self.db_session.query(Wood.grade).distinct().all() if g[0]]
        self.material_grade_comboBox.addItems(grades)
        self.material_grade_comboBox.setEditable(True)

    def populate_materials_list(self):
        self.model.clear()
        query = self.db_session.query(Wood)

        if self.category_filter_checkBox.isChecked():
            category = self.category_filter_comboBox.currentText()
            if category != "All":
                query = query.filter(Wood.category == category)

        if self.species_filter_checkBox.isChecked():
            species = self.species_filter_comboBox.currentText()
            if species != "All":
                query = query.filter(Wood.species == species)

        materials = query.order_by(Wood.name).all()
        for material in materials:
            item = Qtg.QStandardItem(material.name)
            item.setData(material.id, Qtc.Qt.ItemDataRole.UserRole)
            self.model.appendRow(item)

    def filter_materials(self):
        self.category_filter_comboBox.setEnabled(self.category_filter_checkBox.isChecked())
        self.species_filter_comboBox.setEnabled(self.species_filter_checkBox.isChecked())
        self.populate_materials_list()

    def new_material(self):
        self.materials_listView.clearSelection()
        self.material_name_lineEdit.clear()
        self.material_category_comboBox.setCurrentIndex(-1)
        self.material_species_comboBox.setCurrentIndex(-1)
        self.material_type_comboBox.setCurrentIndex(-1)
        self.material_grade_comboBox.setCurrentIndex(-1)
        self.material_fb_lineEdit.clear()
        self.material_fv_lineEdit.clear()
        self.material_fc_lineEdit.clear()
        self.meterial_fcp_lineEdit.clear()
        self.material_ft_lineEdit.clear()
        self.meterial_e_lineEdit.clear()
        self.material_name_lineEdit.setFocus()

    def on_material_selected(self, selected, deselected):
        if selected.indexes():
            item = self.model.itemFromIndex(selected.indexes()[0])
            material_id = item.data(Qtc.Qt.ItemDataRole.UserRole)
            material = self.db_session.query(Wood).get(material_id)
            if material:
                self.material_name_lineEdit.setText(material.name.strip() if material.name else "")
                self.material_category_comboBox.setCurrentText(material.category.strip() if material.category else "")
                self.material_species_comboBox.setCurrentText(material.species.strip() if material.species else "")
                self.material_type_comboBox.setCurrentText(material.material_type.strip() if material.material_type else "")
                self.material_grade_comboBox.setCurrentText(material.grade.strip() if material.grade else "")
                self.material_fb_lineEdit.setText(str(material.fb) if material.fb is not None else "")
                self.material_fv_lineEdit.setText(str(material.fv) if material.fv is not None else "")
                self.material_fc_lineEdit.setText(str(material.fc) if material.fc is not None else "")
                self.meterial_fcp_lineEdit.setText(str(material.fcp) if material.fcp is not None else "")
                self.material_ft_lineEdit.setText(str(material.ft) if material.ft is not None else "")
                self.meterial_e_lineEdit.setText(str(material.E05) if material.E05 is not None else "")

    def save_material(self):
        name = self.material_name_lineEdit.text().strip()
        if not name:
            Qtw.QMessageBox.warning(self, "Input Error", "Material name cannot be empty.")
            return

        selected_indexes = self.materials_listView.selectedIndexes()
        
        # Check for name uniqueness
        query = self.db_session.query(Wood).filter(Wood.name == name)
        if selected_indexes: # Editing existing material
            item = self.model.itemFromIndex(selected_indexes[0])
            material_id = item.data(Qtc.Qt.ItemDataRole.UserRole)
            # Exclude the current material from the uniqueness check
            query = query.filter(Wood.id != material_id)
        
        if query.first():
            Qtw.QMessageBox.warning(self, "Input Error", f"A material with the name '{name}' already exists.")
            return

        if selected_indexes: # Editing
            material = self.db_session.query(Wood).get(material_id)
        else: # Creating new
            material = Wood()

        # Populate data from UI
        material.name = name
        material.category = self.material_category_comboBox.currentText()
        material.species = self.material_species_comboBox.currentText()
        material.material_type = self.material_type_comboBox.currentText()
        material.grade = self.material_grade_comboBox.currentText()
        try:
            material.fb = float(self.material_fb_lineEdit.text()) if self.material_fb_lineEdit.text() else None
            material.fv = float(self.material_fv_lineEdit.text()) if self.material_fv_lineEdit.text() else None
            material.fc = float(self.material_fc_lineEdit.text()) if self.material_fc_lineEdit.text() else None
            material.fcp = float(self.meterial_fcp_lineEdit.text()) if self.meterial_fcp_lineEdit.text() else None
            material.ft = float(self.material_ft_lineEdit.text()) if self.material_ft_lineEdit.text() else None
            material.E05 = float(self.meterial_e_lineEdit.text()) if self.meterial_e_lineEdit.text() else None
        except ValueError:
            Qtw.QMessageBox.warning(self, "Input Error", "Please enter valid numbers for material properties.")
            return

        self.db_session.add(material)
        self.db_session.commit()

        # Repopulate combos to include any new values
        self.material_category_comboBox.clear()
        self.material_species_comboBox.clear()
        self.material_type_comboBox.clear()
        self.material_grade_comboBox.clear()
        self.populate_property_combos()

        self.category_filter_comboBox.clear()
        self.species_filter_comboBox.clear()
        self.populate_filters()

        self.populate_materials_list()
        
        # Reselect the saved item
        for row in range(self.model.rowCount()):
            item = self.model.item(row)
            if item.data(Qtc.Qt.ItemDataRole.UserRole) == material.id:
                self.materials_listView.setCurrentIndex(self.model.indexFromItem(item))
                break

    def delete_material(self):
        selected_indexes = self.materials_listView.selectedIndexes()
        if selected_indexes:
            item = self.model.itemFromIndex(selected_indexes[0])
            material_id = item.data(Qtc.Qt.ItemDataRole.UserRole)
            
            reply = Qtw.QMessageBox.question(self, "Delete Material",
                                           f"Are you sure you want to delete this material?",
                                           Qtw.QMessageBox.StandardButton.Yes | Qtw.QMessageBox.StandardButton.No,
                                           Qtw.QMessageBox.StandardButton.No)

            if reply == Qtw.QMessageBox.StandardButton.Yes:
                material = self.db_session.query(Wood).get(material_id)
                if material:
                    self.db_session.delete(material)
                    self.db_session.commit()
                    self.populate_materials_list()
