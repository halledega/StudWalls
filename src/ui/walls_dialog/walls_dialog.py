"""
This module contains the logic for the Walls dialog window.
"""

from PySide6 import QtCore as Qtc, QtWidgets as Qtw, QtGui as Qtg
from PySide6.QtCore import QStringListModel
from src.ui.walls_dialog.walls_ui.walls_dialog import Ui_walls_Dialog
from src.models.wall import Wall
from src.models.story import Story
from src.models.loads import Load
from src.models.wall_story import WallStory

class WallsDialog(Qtw.QDialog, Ui_walls_Dialog):
    """
    Manages the user interface for creating and editing walls.
    """
    def __init__(self, db_session, wall_id=None, parent=None):
        """
        Initializes the WallsDialog.

        Args:
            db_session: The SQLAlchemy session for database interaction.
            wall_id (int, optional): The ID of the wall to edit. If None, a new wall is created. Defaults to None.
            parent (QWidget, optional): The parent widget. Defaults to None.
        """
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
        """Initializes the models for the table and list views."""
        self.tribs_model = Qtg.QStandardItemModel(self)
        self.tribs_tableView.setModel(self.tribs_model)
        self.tribs_tableView.verticalHeader().hide()
        header = self.tribs_tableView.horizontalHeader()
        header.setSectionResizeMode(Qtw.QHeaderView.ResizeMode.Stretch)

        self.left_loads_model = QStringListModel(self)
        self.left_loads_listView.setModel(self.left_loads_model)
        self.right_loads_model = QStringListModel(self)
        self.right_loads_listView.setModel(self.right_loads_model)
        self.available_loads_model = QStringListModel(self)
        self.loads_listView.setModel(self.available_loads_model)

    def _connect_signals(self):
        """Connects widget signals to their corresponding slots."""
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
        """Populates the dialog with the initial wall data."""
        self.wall_name_lineEdit.setText(self.wall.name)

        for story in self.stories:
            self.bottom_story_comboBox.addItem(story.name)
            self.top_story_comboBox.addItem(story.name)

        if self.wall.stories:
            self.bottom_story_comboBox.setCurrentText(self.wall.stories[0].story.name)
            self.top_story_comboBox.setCurrentText(self.wall.stories[-1].story.name)

        self._update_wall_span()

    def _update_wall_span(self):
        """Updates the dialog when the top or bottom story of the wall changes."""
        self._save_tribs_data()

        start_index = self.bottom_story_comboBox.currentIndex()
        end_index = self.top_story_comboBox.currentIndex()

        if end_index < start_index:
            self.n_stoiries_label.setText("Invalid Range")
            self.wall_height_label.setText("Invalid Range")
            self.tribs_model.clear()
            self.select_story_comboBox.clear()
            return

        selected_stories = self.stories[start_index:end_index + 1]
        num_stories = len(selected_stories)

        existing_wall_stories = {ws.story.id: ws for ws in self.wall.stories}
        new_wall_stories = []
        for story in selected_stories:
            if story.id in existing_wall_stories:
                new_wall_stories.append(existing_wall_stories[story.id])
            else:
                new_wall_stories.append(WallStory(story=story))
        
        self.wall.stories = new_wall_stories

        self._adjust_data_lists(num_stories)

        self.n_stoiries_label.setText(f"Stories: {num_stories}")
        total_height = sum(s.story.height for s in self.wall.stories)
        self.wall_height_label.setText(f"Height: {total_height / 1000:.2f} m")

        self._populate_trib_table()
        self._update_load_story_selector()

    def _adjust_data_lists(self, num_stories):
        """Ensures data lists (like tribs) match the number of stories."""
        if not self.wall.tribs:
            self.wall.tribs = []
        current_len = len(self.wall.tribs)
        if num_stories > current_len:
            self.wall.tribs.extend([[0, 0]] * (num_stories - current_len))
        else:
            self.wall.tribs = self.wall.tribs[:num_stories]

        if not self.wall.lu:
            self.wall.lu = []
        current_len = len(self.wall.lu)
        if num_stories > current_len:
            default_lu = self.wall.lu[-1] if self.wall.lu else [0, 0]
            self.wall.lu.extend([default_lu] * (num_stories - current_len))
        else:
            self.wall.lu = self.wall.lu[:num_stories]

    def _populate_trib_table(self):
        """Populates the tributary widths table."""
        self.tribs_model.clear()
        self.tribs_model.setHorizontalHeaderLabels(['Story', 'Left Trib (mm)', 'Right Trib (mm)'])
        for i, wall_story in enumerate(self.wall.stories):
            row = [
                Qtg.QStandardItem(wall_story.story.name),
                Qtg.QStandardItem(str(self.wall.tribs[i][0])),
                Qtg.QStandardItem(str(self.wall.tribs[i][1]))
            ]
            self.tribs_model.appendRow(row)

    def _update_load_story_selector(self):
        """Updates the story selector combobox for load assignment."""
        self.select_story_comboBox.blockSignals(True)
        self.select_story_comboBox.clear()

        story_names = [s.story.name for s in self.wall.stories]
        if story_names:
            self.select_story_comboBox.addItems(story_names)

        self.select_story_comboBox.blockSignals(False)

        self.current_load_story_index = self.select_story_comboBox.currentIndex()
        self._populate_load_views()

    def _on_load_story_changed(self, index):
        """Handles changing the story for which loads are being edited."""
        if index < 0:
            return

        self.current_load_story_index = index
        self._populate_load_views()

    def _populate_load_views(self):
        """Populates the available and assigned load lists for the current story."""
        self.available_loads_model.setStringList(sorted([l.name for l in self.all_loads]))

        if self.current_load_story_index < 0 or self.current_load_story_index >= len(self.wall.stories):
            self.left_loads_model.setStringList([])
            self.right_loads_model.setStringList([])
            return

        wall_story = self.wall.stories[self.current_load_story_index]
        assigned_left_names = [l.name for l in wall_story.loads_left]
        assigned_right_names = [l.name for l in wall_story.loads_right]

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
        """Adds a selected load to the specified side of the wall for the current story."""
        selection = self.loads_listView.selectedIndexes()
        if not selection:
            return

        load_name = self.available_loads_model.stringList()[selection[0].row()]
        load_obj = next((l for l in self.all_loads if l.name == load_name), None)

        if not load_obj:
            return

        wall_story = self.wall.stories[self.current_load_story_index]
        load_list = getattr(wall_story, side)
        if load_obj not in load_list:
            load_list.append(load_obj)

        self._populate_load_views()

    def _remove_load_from_side(self, side, view):
        """Removes a selected load from the specified side of the wall."""
        selection = view.selectedIndexes()
        if not selection:
            return

        load_name = view.model().stringList()[selection[0].row()]
        load_obj = next((l for l in self.all_loads if l.name == load_name), None)

        if not load_obj:
            return

        wall_story = self.wall.stories[self.current_load_story_index]
        load_list = getattr(wall_story, side)
        if load_obj in load_list:
            load_list.remove(load_obj)

        self._populate_load_views()

    def _save_tribs_data(self):
        """Saves the tributary width data from the table back to the wall object."""
        if self.tribs_model.rowCount() == 0:
            return
        for i in range(self.tribs_model.rowCount()):
            try:
                self.wall.tribs[i][0] = float(self.tribs_model.item(i, 1).text())
                self.wall.tribs[i][1] = float(self.tribs_model.item(i, 2).text())
            except (ValueError, AttributeError):
                pass

    def accept(self):
        """Saves all data to the wall object and commits to the database."""
        self.wall.name = self.wall_name_lineEdit.text()
        self._save_tribs_data()
        self.db_session.add(self.wall)
        self.db_session.commit()
        super().accept()