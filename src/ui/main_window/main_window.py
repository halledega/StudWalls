import sys
import os
from PySide6 import QtCore as Qtc, QtWidgets as Qtw, QtGui as Qtg
from PySide6.QtGui import QAction
from PySide6.QtPrintSupport import QPrintDialog

# UI and Core Imports
from src.ui.main_window.main_ui.main_window import Ui_MainWindow
from src.core.units import Units, UnitSystem
from src.core.calculator import StudWallCalculator
from src.core.project import new_project
from src.core.database import get_working_db

# Model Imports
from src.models.story import Story
from src.models.loads import Load
from src.models.wall import Wall
from src.models.result import Result
from src.models.load_combination import LoadCombination
from src.models.stud import Stud

# Dialog Imports
from src.ui.stories_dialog.stories_dialog import StoriesDialog
from src.ui.walls_dialog.walls_dialog import WallsDialog
from src.ui.about_dialog.about_dialog import AboutDialog
from src.ui.loads_dialog.loads_dialog import LoadsDialog
from src.ui.materials_dialog.materials_dialog import MaterialsDialog
from src.ui.studs_dialog.studs_dialog import StudsDialog
from src.ui.load_combos_dialog.load_combos_dialog import LoadCombosDialog


class MainWindow(Qtw.QMainWindow, Ui_MainWindow):
    """
    The main application window.

    This class inherits from QMainWindow, the standard Qt class for main application
    windows, and Ui_MainWindow, the class auto-generated from the main_window.ui file.
    It is responsible for initializing the application state, connecting UI signals
    to logic slots, and launching all the data management dialogs.
    """
    def __init__(self):
        """
        Initializes the MainWindow, sets up the UI, and connects actions.
        """
        super().__init__()
        # Obtain a database session for the application's lifetime.
        self.db_session = next(get_working_db())
        
        # Set up the UI elements from the loaded UI file.
        self.setupUi(self)

        # Perform startup tasks.
        self.start_up()

        # Initialize the core calculator engine.
        self.units = Units.Metric
        self.calculator = StudWallCalculator(self.units, db_session=self.db_session)

        # Connect menu actions and buttons to their corresponding methods.
        self.connect_actions()

        # Display the main application window.
        self.show()

    def start_up(self):
        """
        Performs initial startup tasks for the MainWindow.
        """
        self.units_comboBox.addItems(["Metric", "Imperial"])
        self.units_comboBox.setCurrentText("Metric")
        self.new_project()

    def new_project(self):
        """Creates a new project, which re-initializes the working database and updates the UI."""
        new_project()
        self.update_wall_comboBox()
        self.statusbar.showMessage("New project created.")

    def new_wall(self):
        """Launches the WallsDialog to create a new wall."""
        dialog = WallsDialog(self.db_session)
        if dialog.exec(): # dialog.exec() returns True if the user clicks OK
            self.update_wall_comboBox()

    def delete_wall(self):
        """Deletes the currently selected wall after a confirmation prompt."""
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
        Refreshes the wall selection combobox with the current list of walls from the database.
        """
        self.wall_comboBox.clear()
        walls = self.db_session.query(Wall).all()
        self.wall_comboBox.addItems([wall.name for wall in walls])

    def connect_actions(self):
        """
        Connects all QAction and button signals to their corresponding slots (methods).
        This is a central place for all UI event handling connections.
        """
        # Main window widgets
        self.run_pushButton.clicked.connect(self.run_calculation)
        self.new_wall_pushButton.clicked.connect(self.new_wall)
        self.delete_wall_pushButton.clicked.connect(self.delete_wall)
        self.finalize_pushButton.clicked.connect(self.finalize_results)
        self.generate_report_pushButton.clicked.connect(self.generate_report)

        # Menu Bar Actions
        self.actionNew.triggered.connect(self.new_project)
        self.actionLevels.triggered.connect(self.show_stories_dialog)
        self.actionWalls.triggered.connect(self.edit_wall)
        self.actionLoads.triggered.connect(self.show_loads_dialog)
        self.actionMaterials.triggered.connect(self.show_materials_dialog)
        self.actionStuds.triggered.connect(self.show_studs_dialog)
        self.actionLoad_Combinations.triggered.connect(self.show_load_combos_dialog)
        self.actionClose.triggered.connect(self.close)
        self.actionAnalze_and_Code_Check.triggered.connect(self.run_calculation)
        self.actionAbout.triggered.connect(self.show_about_dialog)

        # Dynamically add a "Delete Wall" action to the Edit menu.
        self.delete_wall_action = QAction("Delete Wall", self)
        self.menuEdit.addAction(self.delete_wall_action)
        self.delete_wall_action.triggered.connect(self.delete_wall)

        # Unit system ComboBox
        self.units_comboBox.currentTextChanged.connect(self.on_units_changed)

    def on_units_changed(self, unit_system_str: str):
        """
        Slot that updates the calculator's unit system when the user changes the selection.
        
        Args:
            unit_system_str (str): The selected unit system name ("Metric" or "Imperial").
        """
        if unit_system_str == "Metric":
            self.units = Units.Metric
        else:
            self.units = Units.Imperial

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
            summary_output, _ = self.calculator.calculate()
            self.result_summary_textEdit.setText(summary_output)
            self.populate_results_table(wall)

    def populate_results_table(self, wall):
        """
        Populates the results table with the results from the database for the given wall.
        """
        self.results_tableWidget.clear()
        self.results_tableWidget.setRowCount(0)

        headers = ["ID", "Level", "Load Combo", "Section", "Material", "Grade", "Kd", "Kh", "Kse", "Ksc", "Kt", "Cf", "Pr", "DC", "Final"]
        self.results_tableWidget.setColumnCount(len(headers))
        self.results_tableWidget.setHorizontalHeaderLabels(headers)
        self.results_tableWidget.setColumnHidden(0, True) # Hide the ID column

        for wall_story in wall.stories:
            for result in wall_story.results:
                row_position = self.results_tableWidget.rowCount()
                self.results_tableWidget.insertRow(row_position)

                self.results_tableWidget.setItem(row_position, 0, Qtw.QTableWidgetItem(str(result.id)))
                self.results_tableWidget.setItem(row_position, 1, Qtw.QTableWidgetItem(str(wall_story.story.name)))
                self.results_tableWidget.setItem(row_position, 2, Qtw.QTableWidgetItem(result.governing_combo))
                self.results_tableWidget.setItem(row_position, 3, Qtw.QTableWidgetItem(f"{result.plys}-{result.stud.name}"))
                self.results_tableWidget.setItem(row_position, 4, Qtw.QTableWidgetItem(result.stud.material.name))
                self.results_tableWidget.setItem(row_position, 5, Qtw.QTableWidgetItem(result.stud.material.grade))
                self.results_tableWidget.setItem(row_position, 6, Qtw.QTableWidgetItem(f"{result.k_factors.get('Kd', ''):.2f}"))
                self.results_tableWidget.setItem(row_position, 7, Qtw.QTableWidgetItem(f"{result.k_factors.get('Kh', ''):.2f}"))
                self.results_tableWidget.setItem(row_position, 8, Qtw.QTableWidgetItem(f"{result.k_factors.get('Kse', ''):.2f}"))
                self.results_tableWidget.setItem(row_position, 9, Qtw.QTableWidgetItem(f"{result.k_factors.get('Ksc', ''):.2f}"))
                self.results_tableWidget.setItem(row_position, 10, Qtw.QTableWidgetItem(f"{result.k_factors.get('Kt', ''):.2f}"))
                self.results_tableWidget.setItem(row_position, 11, Qtw.QTableWidgetItem("")) # Cf - not in result model
                self.results_tableWidget.setItem(row_position, 12, Qtw.QTableWidgetItem(f"{result.Pr:.2f}"))
                self.results_tableWidget.setItem(row_position, 13, Qtw.QTableWidgetItem(f"{result.dc_ratio:.2f}"))

                # Add a checkbox for the 'is_final' status
                checkbox = Qtw.QCheckBox()
                checkbox.setChecked(result.is_final)
                self.results_tableWidget.setCellWidget(row_position, 14, checkbox)


    def finalize_results(self):
        """
        Updates the 'is_final' status of the results in the database based on the
        user's selection in the results table.
        """
        current_wall_name = self.wall_comboBox.currentText()
        if not current_wall_name:
            return

        wall = self.db_session.query(Wall).filter_by(name=current_wall_name).first()
        if not wall:
            return

        for row in range(self.results_tableWidget.rowCount()):
            result_id = int(self.results_tableWidget.item(row, 0).text())
            checkbox = self.results_tableWidget.cellWidget(row, 14)
            is_final = checkbox.isChecked()

            result = self.db_session.query(Result).filter_by(id=result_id).first()
            if result:
                result.is_final = is_final
        
        self.db_session.commit()
        self.statusbar.showMessage("Finalized results saved.")

    def generate_report(self):
        """Generates a report from the final results and displays it in a new dialog."""
        current_wall_name = self.wall_comboBox.currentText()
        if not current_wall_name:
            Qtw.QMessageBox.warning(self, "No Wall Selected", "Please select a wall to generate a report for.")
            return

        wall = self.db_session.query(Wall).filter_by(name=current_wall_name).first()
        if not wall:
            return

        # Get project info from UI
        project_info = {
            "[Date]": self.project_date_dateEdit.text(),
            "[Project Number]": self.project_number_lineEdit.text(),
            "[Project Name]": self.project_name_lineEdit.text(),
            "[Engineer]": self.engineer_lineEdit.text(),
            "[Wall Number]": current_wall_name
        }

        # Read the template
        template_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "OutPutExample.txt")
        with open(template_path, "r") as f:
            report_content = f.read()

        # Replace placeholders
        for placeholder, value in project_info.items():
            report_content = report_content.replace(placeholder, value)

        # Add tables
        report_content = report_content.replace("[Table of Load Cases]", self._generate_load_cases_table())
        report_content = report_content.replace("[Table of Load Combinations]", self._generate_load_combinations_table())
        report_content = report_content.replace("[Table of stud sections]", self._generate_stud_sections_table())
        report_content = report_content.replace("[Table of materials]", self._generate_materials_table())
        report_content = report_content.replace("[Table of Levels]", self._generate_levels_table(wall))
        report_content = report_content.replace("[Result Summary Table]", self._generate_results_summary_table(wall))
        report_content = report_content.replace("[Table of detail results]", self._generate_detailed_results_table(wall))

        # Display the report
        report_dialog = Qtw.QDialog(self)
        report_dialog.setWindowTitle("Generated Report")
        layout = Qtw.QVBoxLayout(report_dialog)
        text_edit = Qtw.QTextEdit(report_dialog)
        text_edit.setReadOnly(True)
        text_edit.setText(report_content)
        layout.addWidget(text_edit)

        # Add a print button
        print_button = Qtw.QPushButton("Print/Export to PDF", report_dialog)
        print_button.clicked.connect(lambda: self.print_report(text_edit))
        layout.addWidget(print_button)

        report_dialog.exec()

    def print_report(self, text_edit):
        """Prints the content of the given QTextEdit."""
        dialog = QPrintDialog()
        if dialog.exec() == Qtw.QDialog.Accepted:
            text_edit.print_(dialog.printer())

    def _generate_load_cases_table(self):
        loads = self.db_session.query(Load).all()
        table = "Load Cases\n" + "-"*20 + "\n"
        for load in loads:
            table += f"{load.name}: {load.value} {load.case}\n"
        return table

    def _generate_load_combinations_table(self):
        combos = self.db_session.query(LoadCombination).all()
        table = "Load Combinations\n" + "-"*20 + "\n"
        for combo in combos:
            table += f"{combo.name}\n"
        return table

    def _generate_stud_sections_table(self):
        studs = self.db_session.query(Stud).all()
        table = "Stud Sections\n" + "-"*20 + "\n"
        for stud in studs:
            table += f"{stud.name}\n"
        return table

    def _generate_materials_table(self):
        # This is a placeholder. The user should specify what to show here.
        return "Materials Table Placeholder"

    def _generate_levels_table(self, wall):
        table = "Levels\n" + "-"*20 + "\n"
        for ws in wall.stories:
            table += f"{ws.story.name}: {ws.story.height} mm\n"
        return table

    def _generate_results_summary_table(self, wall):
        final_results = self.db_session.query(Result).join(Result.wall_story).filter(Wall.id == wall.id, Result.is_final == True).all()
        table = "Results Summary\n" + "-"*20 + "\n"
        for result in final_results:
            table += f"Level {result.wall_story.story.name}: {result.plys}-{result.stud.name} @ {result.spacing}mm o/c\n"
        return table

    def _generate_detailed_results_table(self, wall):
        table = "Detailed Results\n" + "-"*20 + "\n"
        for ws in wall.stories:
            table += f"Floor: {ws.story.name}\n"
            for result in ws.results:
                table += f"  {result.governing_combo}: {result.dc_ratio:.2f}\n"
        return table

    # --- Dialog Launching Methods ---

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

    def show_load_combos_dialog(self):
        """Opens the dialog to edit all load combinations."""
        dialog = LoadCombosDialog(self.db_session)
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


