# Import system
import sys
import json

# Python Imports
# PySide6 Imports
from PySide6 import QtCore as Qtc, QtWidgets
from PySide6 import QtWidgets as Qtw
from PySide6 import QtGui as Qtgui
from PySide6.QtCore import QStringListModel

# UI Imports
from src.ui.walls_dialog.walls_ui.walls_dialog import Ui_walls_Dialog
# StudWall Imports
from src.models.wall import Wall
from src.models.story import Story
from src.models.loads import Load


class WallsDialog(QtWidgets.QDialog, Ui_walls_Dialog):
    def __init__(self, db_session, wall_id=None, parent=None):
        super().__init__()
        self.setupUi(self)

        self.db_session = db_session
        self.wall_id = wall_id

        if self.wall_id:
            self.wall = self.db_session.query(Wall).get(self.wall_id)
        else:
            self.wall = Wall(name=f"W{self.db_session.query(Wall).count() + 1}")

        self.stories = self.db_session.query(Story).all()
        self.all_loads = self.db_session.query(Load).all()
        self.current_load_story_index = 0

        self._setup_models()
        self._load_wall_data()
        self._connect_signals()

    def _setup_models(self):
        """Setup table and list models"""
        self.tribs_model = Qtgui.QStandardItemModel(self)
        self.tribs_tableView.setModel(self.tribs_model)

        self.left_loads_model = QStringListModel(self)
        self.left_loads_listView.setModel(self.left_loads_model)
        self.right_loads_model = QStringListModel(self)
        self.right_loads_listView.setModel(self.right_loads_model)
        self.available_loads_model = QStringListModel(self)
        self.loads_listView.setModel(self.available_loads_model)

    def _connect_signals(self):
        self.bottom_story_comboBox.currentIndexChanged.connect(self._update_wall_span)
        self.top_story_comboBox.currentIndexChanged.connect(self._update_wall_span)
        self.select_story_comboBox.currentIndexChanged.connect(self._on_load_story_changed)

        self.add_loads_left_pushButton.clicked.connect(self._add_load_left)
        self.delete_loads_left_pushButton.clicked.connect(self._remove_load_left)
        self.add_loads_right_pushButton.clicked.connect(self._add_load_right)
        self.delete_loads_right_pushButton.clicked.connect(self._remove_load_right)

        self.ok_pushButton.clicked.connect(self.accept)
        self.cancel_pushButton.clicked.connect(self.reject)

    def _load_wall_data(self):
        """Populate the dialog with the initial wall data."""
        self.wall_name_lineEdit.setText(self.wall.name)

        for story in self.stories:
            self.bottom_story_comboBox.addItem(story.name)
            self.top_story_comboBox.addItem(story.name)

        if self.wall.stories:
            self.bottom_story_comboBox.setCurrentText(self.wall.stories[0].name)
            self.top_story_comboBox.setCurrentText(self.wall.stories[-1].name)

        self._update_wall_span()

    def _update_wall_span(self):
        """Update the dialog display based on the selected top and bottom stories."""
        self._save_tribs_data() # Save any edits before repopulating

        start_index = self.bottom_story_comboBox.currentIndex()
        end_index = self.top_story_comboBox.currentIndex()

        if end_index < start_index:
            self.n_stoiries_label.setText("Invalid Range")
            self.wall_height_label.setText("Invalid Range")
            self.tribs_model.clear()
            self.select_story_comboBox.clear()
            return

        self.wall.stories = self.stories[start_index:end_index + 1]
        num_stories = len(self.wall.stories)

        # Adjust data lists to match story count
        self._adjust_data_lists(num_stories)

        self.n_stoiries_label.setText(f"Stories: {num_stories}")
        total_height = sum(s.height for s in self.wall.stories)
        self.wall_height_label.setText(f"Height: {total_height / 1000:.2f} m")

        self._populate_trib_table()
        self._update_load_story_selector()

    def _adjust_data_lists(self, num_stories):
        """Truncate or extend data lists to match the number of stories."""
        # Tribs
        if not self.wall.tribs:
            self.wall.tribs = []
        current_len = len(self.wall.tribs)
        if num_stories > current_len:
            self.wall.tribs.extend([[0, 0]] * (num_stories - current_len))
        else:
            self.wall.tribs = self.wall.tribs[:num_stories]

        # Loads
        for load_list_name in ['loads_left', 'loads_right']:
            if not getattr(self.wall, load_list_name):
                setattr(self.wall, load_list_name, [])
            load_list = getattr(self.wall, load_list_name)
            current_len = len(load_list)
            if num_stories > current_len:
                load_list.extend([[] for _ in range(num_stories - current_len)])
            else:
                setattr(self.wall, load_list_name, load_list[:num_stories])

        # Unsupported Lengths (lu)
        if not self.wall.lu:
            self.wall.lu = []
        current_len = len(self.wall.lu)
        if num_stories > current_len:
            default_lu = self.wall.lu[-1] if self.wall.lu else [0, 0]
            self.wall.lu.extend([default_lu] * (num_stories - current_len))
        else:
            self.wall.lu = self.wall.lu[:num_stories]


    def _populate_trib_table(self):
        self.tribs_model.clear()
        self.tribs_model.setHorizontalHeaderLabels(['Story', 'Left Trib (mm)', 'Right Trib (mm)'])
        for i, story in enumerate(self.wall.stories):
            row = [
                Qtgui.QStandardItem(story.name),
                Qtgui.QStandardItem(str(self.wall.tribs[i][0])),
                Qtgui.QStandardItem(str(self.wall.tribs[i][1]))
            ]
            self.tribs_model.appendRow(row)

    def _update_load_story_selector(self):
        """Update the story selector combobox for loads, and populate loads for the first story."""
        self.select_story_comboBox.blockSignals(True)
        self.select_story_comboBox.clear()

        story_names = [s.name for s in self.wall.stories]
        if story_names:
            self.select_story_comboBox.addItems(story_names)

        self.select_story_comboBox.blockSignals(False)

        # Manually set index and populate for the first time or after wall span changes.
        self.current_load_story_index = self.select_story_comboBox.currentIndex()
        self._populate_load_views()

    def _on_load_story_changed(self, index):
        """Handle user changing the story to edit loads for."""
        if index < 0:
            return

        # Save data for the story we are leaving, then populate for the new one.
        self._save_loads_data(self.current_load_story_index)
        self.current_load_story_index = index
        self._populate_load_views()

    def _populate_load_views(self):
        """Populate the three load list views for the currently selected story."""
        # Always display all possible loads in the center list
        self.available_loads_model.setStringList(sorted([l.name for l in self.all_loads]))

        if self.current_load_story_index < 0 or self.current_load_story_index >= len(self.wall.stories):
            self.left_loads_model.setStringList([])
            self.right_loads_model.setStringList([])
            return

        # Get assigned loads for the current story
        assigned_left_load_ids = self.wall.loads_left[self.current_load_story_index]
        assigned_right_load_ids = self.wall.loads_right[self.current_load_story_index]

        assigned_left_loads = self.db_session.query(Load).filter(Load.id.in_(assigned_left_load_ids)).all()
        assigned_right_loads = self.db_session.query(Load).filter(Load.id.in_(assigned_right_load_ids)).all()

        assigned_left_names = [l.name for l in assigned_left_loads]
        assigned_right_names = [l.name for l in assigned_right_loads]

        self.left_loads_model.setStringList(sorted(assigned_left_names))
        self.right_loads_model.setStringList(sorted(assigned_right_names))

    def _add_load_left(self):
        self._add_load_to_side('loads_left')

    def _remove_load_left(self):
        self._remove_load_from_side('loads_left', self.left_loads_listView)

    def _add_load_right(self):
        self._add_load_to_side('loads_right')

    def _remove_load_right(self):
        self._remove_load_from_side('loads_right', self.right_loads_listView)

    def _add_load_to_side(self, side):
        selection = self.loads_listView.selectedIndexes()
        if not selection:
            return

        load_name = self.available_loads_model.stringList()[selection[0].row()]
        load_obj = next((l for l in self.all_loads if l.name == load_name), None)

        if not load_obj:
            return

        load_list = getattr(self.wall, side)[self.current_load_story_index]
        if load_obj.id not in load_list:
            load_list.append(load_obj.id)

        self._populate_load_views()

    def _remove_load_from_side(self, side, view):
        selection = view.selectedIndexes()
        if not selection:
            return

        load_name = view.model().stringList()[selection[0].row()]
        load_obj = next((l for l in self.all_loads if l.name == load_name), None)

        if not load_obj:
            return

        load_list = getattr(self.wall, side)[self.current_load_story_index]
        if load_obj.id in load_list:
            load_list.remove(load_obj.id)

        self._populate_load_views()

    def _save_tribs_data(self):
        if self.tribs_model.rowCount() == 0:
            return
        for i in range(self.tribs_model.rowCount()):
            try:
                self.wall.tribs[i][0] = float(self.tribs_model.item(i, 1).text())
                self.wall.tribs[i][1] = float(self.tribs_model.item(i, 2).text())
            except (ValueError, AttributeError): # Handle empty or non-numeric cells gracefully
                pass

    def _save_loads_data(self, story_index):
        # This method is no longer needed as we are modifying the lists directly
        pass

    def accept(self):
        self.wall.name = self.wall_name_lineEdit.text()
        self._save_tribs_data()
        self.db_session.add(self.wall)
        self.db_session.commit()
        super().accept()