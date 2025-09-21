"""
This module contains the logic for the Stories dialog window.
"""

from PySide6 import QtCore as Qtc, QtWidgets as Qtw
from src.ui.stories_dialog.stories_ui.story_dialog import Ui_stories_Dialog
from src.models.story import Story

class StoriesDialog(Qtw.QDialog, Ui_stories_Dialog):
    """
    Manages the user interface for creating, editing, and deleting stories (levels).
    """
    def __init__(self, db_session, used_story_names: set):
        """
        Initializes the StoriesDialog.

        Args:
            db_session: The SQLAlchemy session for database interaction.
            used_story_names (set): A set of story names that are currently in use by walls.
                                    This is used to prevent deletion of stories that are in use.
        """
        super().__init__()
        self.setupUi(self)
        self.db_session = db_session
        self.used_story_names = used_story_names

        self.setup_table()

        self.pushButton.clicked.connect(self.accept)
        self.add_level_pushButton.clicked.connect(self.add_level)
        self.delete_level_pushButton.clicked.connect(self.delete_level)

    def setup_table(self):
        """Initializes and sets the custom table model for the stories view."""
        self.levels_tableView.setModel(StoryTableModel(self.db_session))
        self.levels_tableView.verticalHeader().hide()
        header = self.levels_tableView.horizontalHeader()
        header.setSectionResizeMode(Qtw.QHeaderView.ResizeMode.Stretch)

    def add_level(self):
        """Adds a new story to the table and database."""
        model = self.levels_tableView.model()
        model.insertRow(model.rowCount())

    def delete_level(self):
        """Deletes the selected story, with a check to prevent deletion of stories in use."""
        model = self.levels_tableView.model()
        selected_row = self.levels_tableView.currentIndex().row()
        if selected_row < 0:
            return

        story_to_delete = model._stories[selected_row]
        if story_to_delete.name in self.used_story_names:
            Qtw.QMessageBox.warning(
                self, 
                "Story In Use", 
                f"Cannot delete '{story_to_delete.name}' because it is currently in use by one or more walls."
            )
            return
        
        model.removeRow(selected_row)


class StoryTableModel(Qtc.QAbstractTableModel):
    """
    A custom table model for managing Story objects.
    """
    def __init__(self, db_session):
        super().__init__()
        self.db_session = db_session
        self._stories = self.db_session.query(Story).all()
        self._headers = ["Name", "Height", "Floor Thickness"]

    def rowCount(self, parent=Qtc.QModelIndex()):
        return len(self._stories)

    def columnCount(self, parent=Qtc.QModelIndex()):
        return len(self._headers)

    def headerData(self, section, orientation, role):
        if role == Qtc.Qt.ItemDataRole.DisplayRole and orientation == Qtc.Qt.Orientation.Horizontal:
            return self._headers[section]

    def data(self, index, role):
        if role == Qtc.Qt.ItemDataRole.DisplayRole:
            story = self._stories[index.row()]
            if index.column() == 0:
                return story.name
            elif index.column() == 1:
                return story.height
            elif index.column() == 2:
                return story.floor_thickness

    def setData(self, index, value, role):
        if role == Qtc.Qt.ItemDataRole.EditRole:
            story = self._stories[index.row()]
            try:
                if index.column() == 0:
                    story.name = value
                elif index.column() == 1:
                    story.height = float(value)
                elif index.column() == 2:
                    story.floor_thickness = float(value)
                self.db_session.commit()
                self.dataChanged.emit(index, index)
                return True
            except ValueError:
                self.db_session.rollback()
                return False
        return False

    def flags(self, index):
        return super().flags(index) | Qtc.Qt.ItemFlag.ItemIsEditable

    def insertRow(self, row, parent=Qtc.QModelIndex()):
        self.beginInsertRows(parent, row, row)
        new_story = Story(name=f"Story {self.rowCount() + 1}", height=3000, floor_thickness=359)
        self.db_session.add(new_story)
        self.db_session.commit()
        self._stories.append(new_story)
        self.endInsertRows()
        return True

    def removeRow(self, row, parent=Qtc.QModelIndex()):
        self.beginRemoveRows(parent, row, row)
        story_to_delete = self._stories[row]
        self.db_session.delete(story_to_delete)
        self.db_session.commit()
        del self._stories[row]
        self.endRemoveRows()
        return True