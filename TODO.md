# TODO List

1.  Complete actions in Define menu (review @src/ui/main_window/main_ui, sub task for each action not implemented)
    - [ ] Implement "Materials" action
    - [ ] Implement "Studs" action
    - [ ] Implement "Loads" action
    - [ ] Implement "Load Combinations" action
2.  Complete actions in File and Help menu (again review he ui file and make sub tasks based on each item not implemented)
    - [ ] Implement "New" action
    - [ ] Implement "Open" action
    - [ ] Implement "Save" action
    - [ ] Implement "Save As" action
    - [ ] Implement "Preferences" action
    - [ ] Create and implement "Help" menu actions
3.  I'd like to review using a database both for storing/retrveing data at runtime and for the file format for saving (sqlite?, with sqlalchemy?)
    - [x] Add `sqlalchemy` to `pyproject.toml`
    - [x] Define all necessary database models in `src/models` as SQLAlchemy models.
    - [x] Create a database engine/session management module for two databases (library and working).
    - [x] Create a migration script to populate a `library.db` with default data (wood materials, etc.) and dummy project data (stories, loads, walls).
    - [x] Refactor data access logic to use the two-database system.
    - [x] Refactor Wall/Story/Load relationship to use proper SQLAlchemy relationships instead of JSON.
4.  Implement graphics ot the graphics view widgets. The currently active wall shoudl be drawn (setion and elevator?)
5.  Update testing to fully capture anything changed or missing
6.  Review final app and suggest any cleanup or improvements
7.  Fully document all code so even a novice python programmer or someone unfamiliar with PySide can review the code
8.  Create executable with pysintaller or similar. I'd like you to suggest some options with pros and cons features etc.
9.  Run application after any major refactoring to check for regressions. (Recurring task)