# Instructions

a) Always fully explain all proposed changes including reasoning and impact
b) Always ask to run app after code changes to review runtime error
c) keep the list below updated with new tasks and checking off complete ones

# TODO List

1.  Complete actions in Define menu (review @src/ui/main_window/main_ui, sub task for each action not implemented)
    - [x] Implement "Materials" action
        - [x] Allow adding new categories, types, grades and species to a material.
    - [x] Implement "Studs" action
    - [x] Implement "Loads" action
    - [x] Implement "Load Combinations" action
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
10. Clean up table widget columns to use available space.
    - [ ] Adjust dialog sizes for tables with many columns.
11. Update and finalize design output.
    - [ ] Save all results to database.
    - [ ] Clear results when inputs have changed.
    - [ ] Add action to run menu to display results.
    - [ ] Allow users to select from a list of valid results for each floor. This could be in a separate dialog or the results tab of the main window. A "Finalize Results" button should be included that saves the final chosen results to the database (separately from the global results). By default, the 'final results' should be the results with the lowest wood volume of all the combos on a per-floor basis.
    - [ ] Display final results in formatted output (see `OutPutExample.txt` for formatting).
        - Detailed Results Table Columns: Load Combo, section, materials, grade, kd, kh, kse, ksc, kt, Cf, Pr, DC
        - Results Summary Table Columns: Same as Detailed Results, but only for the governing load combo.
        - Input Data Tables: Use DB tables as a reference for columns.
        - Engineer field should be part of project data (use dummy info for now).
    - [ ] Add option to print/export final results to a PDF.