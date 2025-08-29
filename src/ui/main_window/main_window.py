# Import system
import sys
# Python Imports
# PySide6 Imports
from PySide6 import QtCore as Qtc
from PySide6 import QtWidgets as Qtw
from PySide6 import QtGui as Qtgui
from PySide6.QtGui import QAction
# UI Imports
from src.ui.main_window.main_ui.main_window import Ui_MainWindow
# StudWall Imports
from src.core.units import Units, UnitSystem
from src.core.calculator import StudWallCalculator
from src.core.project import new_project
from src.core.database import get_working_db
# Models
from src.models.story import Story
from src.models.loads import Load
from src.models.wall import Wall


from src.ui.stories_dialog.stories_dialog import StoriesDialog
from src.ui.walls_dialog.walls_dialog import WallsDialog
from src.ui.about_dialog.about_dialog import AboutDialog
from src.ui.loads_dialog.loads_dialog import LoadsDialog
from src.ui.materials_dialog.materials_dialog import MaterialsDialog
from src.ui.studs_dialog.studs_dialog import StudsDialog


class MainWindow(Qtw.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        # Placeholder properties (These are set in other methods below)
        self.db_session = next(get_working_db())
        # Set up the UI elements from the loaded UI file
        self.setupUi(self)

        # Perform startup tasks (e.g., loading defaults or preparing the environment)
        self.start_up()

        # Initialize the calculator with Metric as default
        self.units = Units.Metric
        self.calculator = StudWallCalculator(self.units, db_session=self.db_session)

        # Connect menu actions to their corresponding slots
        self.connect_actions()

        # Display the main application window
        self.show()

    def start_up(self):
        """
        Perform startup tasks for the MainWindow.
        """
        # Assuming the combo box for units is named 'units_comboBox' in the UI file.
        self.units_comboBox.addItems(["Metric", "Imperial"])
        self.units_comboBox.setCurrentText("Metric")

        # Create a new project
        self.new_project()

    def new_project(self):
        """Creates a new project and updates the UI."""
        new_project()
        self.update_wall_comboBox()
        self.statusbar.showMessage("New project created.")


    def new_wall(self):
        """Creates a new wall by opening the editor dialog."""
        dialog = WallsDialog(self.db_session)
        if dialog.exec():
            self.update_wall_comboBox()

    def delete_wall(self):
        """Deletes the currently selected wall after confirmation."""
        current_wall_name = self.wall_comboBox.currentText()
        if not current_wall_name:
            Qtw.QMessageBox.warning(self, "No Wall Selected", "Please select a wall to delete.")
            return

        reply = Qtw.QMessageBox.question(self, "Delete Wall",
                                           f"Are you sure you want to delete '{current_wall_name}'?",
                                           Qtw.QMessageBox.StandardButton.Yes | Qtw.QMessageBox.StandardButton.No,
                                           Qtw.QMessageBox.StandardButton.No)

        if reply == Qtw.QMessageBox.StandardButton.Yes:
            wall_to_delete = self.db_session.query(Wall).filter_by(name=current_wall_name).first()
            if wall_to_delete:
                self.db_session.delete(wall_to_delete)
                self.db_session.commit()
                self.update_wall_comboBox()

    def update_wall_comboBox(self):
        """
        Updates the wall_comboBox with the names of the walls.
        """
        self.wall_comboBox.clear()
        walls = self.db_session.query(Wall).all()
        self.wall_comboBox.addItems([wall.name for wall in walls])

    def connect_actions(self):
        """
        Connect actions to their respective slots.
        """
        # Main window widgets
        self.run_pushButton.clicked.connect(self.run_calculation)
        self.new_wall_pushButton.clicked.connect(self.new_wall)
        self.delete_wall_pushButton.clicked.connect(self.delete_wall)

        # Menu Bar Actions
        self.actionNew.triggered.connect(self.new_project)
        self.actionLevels.triggered.connect(self.show_stories_dialog)
        self.actionWalls.triggered.connect(self.edit_wall)
        self.actionLoads.triggered.connect(self.show_loads_dialog)
        self.actionMaterials.triggered.connect(self.show_materials_dialog)
        self.actionStuds.triggered.connect(self.show_studs_dialog)
        self.actionClose.triggered.connect(self.close)
        self.actionAnalze_and_Code_Check.triggered.connect(self.run_calculation)
        self.actionAbout.triggered.connect(self.show_about_dialog)

        # Add delete action to Edit menu
        self.delete_wall_action = QAction("Delete Wall", self)
        self.menuEdit.addAction(self.delete_wall_action)
        self.delete_wall_action.triggered.connect(self.delete_wall)

        # Unit system ComboBox
        self.units_comboBox.currentTextChanged.connect(self.on_units_changed)

    def on_units_changed(self, unit_system_str):
        """
        Updates the calculator and UI when the unit system is changed, converting existing inputs.
        """
        old_units = self.units # Capture old unit system

        if unit_system_str == "Metric":
            self.units = Units.Metric
        else:
            self.units = Units.Imperial

        # Update the calculator's unit system
        self.calculator.unit_system = UnitSystem(self.units)
        self.statusbar.showMessage(f"Units: {self.units.name}")

    def run_calculation(self):
        """
        Gathers inputs from the UI, runs the calculation, and displays the results.
        """
        current_wall_name = self.wall_comboBox.currentText()
        if not current_wall_name:
            Qtw.QMessageBox.warning(self, "No Wall Selected", "Please select a wall to run the calculation on.")
            return

        wall = self.db_session.query(Wall).filter_by(name=current_wall_name).first()
        if wall:
            self.calculator.wall = wall
            summary_output, detailed_output = self.calculator.calculate()
            self.result_summary_textEdit.setText(summary_output)
            self.result_detailed_textEdit.setText(detailed_output)

    def show_stories_dialog(self):
        """Opens the dialog to edit all project stories."""
        used_story_names = {s.story.name for wall in self.db_session.query(Wall).all() for s in wall.stories}
        dialog = StoriesDialog(self.db_session, used_story_names)
        dialog.exec()

    def show_loads_dialog(self):
        """Opens the dialog to edit all project loads."""
        dialog = LoadsDialog(self.db_session)
        dialog.exec()

    def show_materials_dialog(self):
        """Opens the dialog to edit all project materials."""
        dialog = MaterialsDialog(self.db_session)
        dialog.exec()

    def show_studs_dialog(self):
        """Opens the dialog to edit all project studs."""
        dialog = StudsDialog(self.db_session)
        dialog.exec()

    def edit_wall(self):
        """Opens the editor dialog for the currently selected wall."""
        current_wall_name = self.wall_comboBox.currentText()
        if not current_wall_name:
            Qtw.QMessageBox.warning(self, "No Wall Selected", "Please select a wall to edit.")
            return

        wall_to_edit = self.db_session.query(Wall).filter_by(name=current_wall_name).first()
        if wall_to_edit:
            dialog = WallsDialog(self.db_session, wall_id=wall_to_edit.id)
            if dialog.exec():
                self.update_wall_comboBox()

    def show_about_dialog(self):
        """Shows the about dialog."""
        dialog = AboutDialog()
        dialog.exec()