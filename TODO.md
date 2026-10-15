# Project Role, Core Responsibilities & Architectural Constraints

## Role & Goal
Expert software developer specializing in .NET (targeting .NET 10 / .NET 8 compatibility), Avalonia UI, and cross-platform desktop applications (Linux and Windows). The mission is to port the "StudWalls" wood stud wall sizing application from Python/PySide6 to C#/.NET using Avalonia UI and CommunityToolkit.Mvvm, and execute the roadmap to completion.

## Critical Engineering & UI Constraints
1. **Universal Code Readability**:
   - The core logic involves structural engineering calculations per **CSA O86-20** standards.
   - All code—including domain models, mathematical load accumulation, governing combo permutations, ViewModels, and UI logic—must be **exhaustively commented in plain English**.
   - Explicitly cite applicable CSA O86 clauses (e.g. Cl 5.3.2.2 for Kd, Cl 6.5.6.2.2 for Cc slenderness, Cl 6.5.6.2.3 for Pr compressive resistance, Cl 6.5.6.2.4 for Kc column stability, Cl 6.5.6.2.5 for Kzc size factor).
   - Any structural engineer with zero programming background must be able to read, verify, and approve the entire codebase.
2. **Out-of-the-Box (OOTB) UI Styling**:
   - **DO NOT** apply custom styles, icons, emoji, or non-standard visual flourishes.
   - Use clean, standard, out-of-the-box Avalonia Fluent/native controls. Focus entirely on rock-solid functional logic, data binding, and engineering correctness first.
3. **Graphics View Requirement**:
   - Interactive **Building Plan View** displaying all walls.
   - Toggles to display:
     - [x] Tributary widths (shaded bands on left and right sides of walls)
     - [x] Applied loads (load annotations and arrows on tributary zones)
     - [x] Level selector to navigate between stories
     - [x] Secondary detail view for Stud Cross-Section (1, 2, 3 plys with dimensions)
4. **Data Layer & Dual Database Architecture**:
   - Replicate the dual SQLite database system:
     - `library.db`: Persistent library containing wood material properties (from joist_and_plank dataset), standard stud sections, and default load cases/combinations.
     - Working Project Database: Active project data (Walls, Stories, WallStories, assigned loads, results).
   - Project file formats:
     - Primary: `.swproj` (SQLite database file with full ACID integrity).
     - Export/Import: Built-in JSON export and import for plain-text Git diffability.
5. **PDF Export & Commercial Licensing**:
   - Must be 100% free, open source, and permissively licensed for commercial software (MIT license).
   - Implemented via SkiaSharp PDF vector drawing (matching `OutPutExample.txt`).

---

# Instructions

a) Always fully explain all proposed changes including reasoning and impact
b) Always ask to run app after code changes to review runtime error
c) Keep the list below updated with new tasks and checking off complete ones

---

# Migration & Development Task List

## Phase 1: Solution Architecture & Project Scaffolding
- [x] Create .NET Solution `StudWalls.slnx` with projects:
  - [x] `StudWalls.Core` (Class library: models, engineering engine, database, reporting)
  - [x] `StudWalls.Desktop` (Avalonia UI + CommunityToolkit.Mvvm desktop application)
  - [x] `StudWalls.Tests` (xUnit test suite for calculations and database operations)
- [x] Replace Python files with C# solution in the `dotnet` branch.

## Phase 2: Data Models & Dual Database System
- [x] Port domain models with exhaustive documentation:
  - [x] `WoodMaterial` (Lumber species, grade, category, design properties Fb, Fv, Fc, Fcp, Ft, E, E05)
  - [x] `Section` (Geometric properties: width, depth, plys, Ag, Ix, Iy, Sx, Sy)
  - [x] `Stud` (Relationship between Section and WoodMaterial)
  - [x] `Story` (Name, Height, FloorThickness)
  - [x] `Load` (Name, Case: Dead/Live/Snow/Wind/Seismic/Partition, Value, LoadType)
  - [x] `Wall` (Name, Length, SelfWeight)
  - [x] `WallStory` (Relational links between Wall, Story, TribWidthLeft, TribWidthRight, LuWidth, LuDepth, LoadsLeft, LoadsRight)
  - [x] `LoadCombination` & `LoadCombinationItem` (Combo name and factored load multipliers)
  - [x] `DesignResult` (Governing combo, Pf, Pr, DC ratio, Kd, Kh, Kse, Ksc, Kt, wood volume, IsFinal flag)
  - [x] `ProjectInfo` (Project Number, Project Name, Address, Engineer, Date)
  - [x] `AppPreferences` (Unit system, slenderness limits, target D/C ratio, defaults)
- [x] Implement database layer:
  - [x] Persistent `library.db` SQLite database with embedded seed data from `joist_and_plank.csv`
  - [x] Working project database context (in-memory or file-backed)
  - [x] `ProjectManager` handling New, Open, Save, Save As (`.swproj`), and JSON Export/Import

## Phase 3: Core Engineering Engine (CSA O86-20)
- [x] Implement `CsaO86_20` calculation module with line-by-line clause references:
  - [x] Clause 5.3.2.2 / 5.3.2.3: Load duration factor ($K_D$)
  - [x] Clause 6.5.6.2.2: Slenderness ratio ($C_c = L_u / d$) and maximum limit ($C_c \le 50$)
  - [x] Clause 6.5.6.2.3: Factored compressive resistance parallel to grain ($P_r$)
  - [x] Clause 6.5.6.2.4: Column stability factor ($K_c$)
  - [x] Clause 6.5.6.2.5: Size factor ($K_{zc}$)
  - [x] Material E05 adjustments (Sawn vs MSR vs MEL)
- [x] Implement `StudWallEngine`:
  - [x] Top-down cumulative load accumulation per floor (Dead, Live, Snow, Partitions, Wall Self-Weight)
  - [x] Factored load combinations per floor
  - [x] Permutation solver: studs x spacings (406, 305, 203 mm) x plys (1, 2, 3)
  - [x] Optimization by wood volume proxy ($A_g / \text{spacing}$)
- [x] Unit conversions module (`UnitConverter`) supporting Metric and Imperial

## Phase 4: Avalonia UI Desktop Implementation (OOTB Styling)
- [x] Set up MVVM framework using `CommunityToolkit.Mvvm`
- [x] Main Window:
  - [x] Menu bar: File, Edit, Define, Run, Help
  - [x] Dock panel with Tabs:
    - [x] Project Information & Wall Selection
    - [x] Results Table with checkbox selection and "Finalize Results" button
  - [x] Status bar
- [x] Dialogs / Sub-windows (using clean OOTB controls):
  - [x] `MaterialsWindow`: View, filter, and edit wood materials
  - [x] `StudsWindow`: View and edit stud sizes with live section properties
  - [x] `StoriesWindow`: Add, edit, and delete building stories
  - [x] `LoadsWindow`: Manage project load cases
  - [x] `LoadCombosWindow`: Manage load combinations and factors
  - [x] `WallEditorWindow`: Configure wall stories, tributary widths, and load assignments
  - [x] `AboutWindow`: App information and licenses
  - [x] `PreferencesWindow`: Configure units, design thresholds, and geometric defaults
- [x] Interactive Plan View Graphics Canvas:
  - [x] Architectural plan view of all walls
  - [x] Toggle: Show tributary widths
  - [x] Toggle: Show applied loads
  - [x] Active wall selection highlight
  - [x] Level selector (switch between floor plans)
  - [x] Stud section detail view (1, 2, 3 plys with dimension labels)

## Phase 5: Results Finalization & PDF Reporting
- [x] Results selection interface:
  - [x] Display passing solutions per floor
  - [x] Auto-select optimal solution (lowest wood volume) by default
  - [x] Allow manual engineer override
  - [x] "Finalize Results" persistence to database
- [x] Engineering report generation:
  - [x] Plain text / preview dialog matching `OutPutExample.txt`
  - [x] CSA O86-20 design equations and clause references (Cl 6.5.6.2.2, Cl 6.5.6.2.3, Cl 6.5.6.2.4, Cl 6.5.6.2.5)
  - [x] Candidate stud axial capacity breakdown tables for governing load combinations per story level
  - [x] PDF Export using SkiaSharp vector rendering (100% MIT permissive commercial license) with multi-page pagination

## Phase 6: Automated Testing & Verification
- [x] xUnit test suite for CSA O86 calculations against hand calculations
- [x] Multi-story load accumulation verification
- [x] Database clone, save, and reload tests (.swproj SQLite and JSON)
- [x] Unit conversions verification tests
- [x] Report generation and SkiaSharp PDF export verification tests (12 unit tests passing)

---

## Session Handover & Status (2026-09-30)

### Current State:
- **Branch**: `dotnet` at `/home/mwrh/Documents/Repos/StudWalls/`.
- **Target Platform**: .NET 10 / Avalonia UI (CommunityToolkit.Mvvm).
- **Core Port**: 100% complete and fully verified.
  - All legacy Python files removed.
  - Complete CSA O86-20 calculation engine (`CsaO86_20.cs`, `StudWallEngine.cs`).
  - Dual SQLite database system (`.swproj`) + git-diffable JSON export/import.
  - Main Window with Building Plan View (toggles for tributary widths & loads), Story level switcher, and Stud Cross-Section detail canvas.
  - Results finalization table with wood volume optimization.
  - 100% permissive commercial vector PDF export via SkiaSharp (`PdfReportExporter.cs`).
  - Full Preferences dialog (`File -> Preferences...`) with design criteria, unit choices, and geometric defaults.
- **Verification Status**:
  - `dotnet build StudWalls.slnx`: **0 Errors, 0 Warnings** (all SkiaSharp 3.x APIs modernized to `SKFont`).
  - `dotnet test StudWalls.slnx`: **9 Passed, 0 Failed**.
  - Binary executable compiled and ready at `src/StudWalls.Desktop/bin/Debug/net10.0/StudWalls.Desktop`.

### Completed Engineering & UI Improvements (2026-09-30):
- [x] Two-Pass Structural Analysis & Sizing Engine (`StudWallEngine.cs`):
  - [x] **Pass 1 (Candidate Screening & Optimization)**: Iterates across all defined stud sections and spacings (16", 12", 8" o/c, 1-3 plys), evaluating capacity against all ULS combinations. Identifies valid passing options ($D/C \le 1.0$) and selects the design with the lowest wood volume ($A_g / \text{spacing}$) as the optimal recommendation (`IsFinal = true`).
  - [x] **Pass 2 (Multi-Combination Envelope Check)**: Re-evaluates every viable section/spacing combination across every defined NBCC load combination, computing and storing the complete array of $P_f$, $P_r$, $K_d$, $K_c$, $D/C$ ratio, and governing status.
  - [x] Comprehensive reporting in both `CalculationLogDialog` and detailed logs showing full multi-combo tables for each level.
- [x] Results Dock Master-Detail Interface (Option A):
  - [x] Upper Table: Lists all candidate stud configurations per level with governing combination, factored demand $P_f$, resistance $P_r$, governing D/C ratio, and wood volume proxy.
  - [x] Sub-table Splitter: Draggable horizontal divider allowing engineers to adjust the breakdown view height.
  - [x] Lower Table: Dynamically displays the full multi-combination envelope check for the currently selected stud option, listing every load combination with $K_d$, $P_f$, $P_r$, $K_c$, $D/C$ ratio, Pass/Fail status, and governing checkbox. Automatically defaults to the optimal design on calculation run.
- [x] Traditional Command Toolbar:
  - [x] Dedicated button groups matching each menu (File, Edit, Define, Run, Help).
  - [x] Cleaned up toolbar button groups by removing text labels ("File:", "Edit:", etc.) and keeping clean vertical dividers.
  - [x] Streamlined File group by removing redundant action buttons (`Preferences`, `Export JSON`, `Import JSON`, `Exit`) per markup, keeping standard project actions (`New`, `Open`, `Save`, `Save As`).
  - [x] Clear vertical group dividers and horizontal scrolling support.
- [x] ETABS-like Model Explorer TreeView (Left Sidebar):
  - [x] Hierarchical TreeView organizing:
    - Root Project (Project Name & Number)
    - Project Information & Settings
    - Structural Definitions (Wood Materials, Stud Cross-Sections, Stories/Levels, Specified Loads, Load Combinations)
    - Structural Objects (Walls with dimensions and assigned stories)
    - Analysis & Design actions (Run Analysis & Sizing, Report, Preferences)
  - [x] Removed header action buttons (`Edit Selected`, `New Wall`, `Run Sizing`) per markup.
  - [x] Tree levels collapsed by default per markup (`IsExpanded = false`), keeping only the root project expanded.
  - [x] Fixed TreeView theme styling (removed hardcoded light background) so all text items render crisply in Dark mode.
  - [x] Double-click item activation to open dedicated definition or wall configuration editors.
  - [x] Bidirectional synchronization: selecting a Wall node in the TreeView updates `SelectedWall`, highlighting it in the 2D Plan View and updating the Results DataGrid; selecting a wall from code or canvas synchronizes back to the tree.
  - [x] Automatic tree refresh on wall addition (`New Wall`), deletion (`Delete Wall`), copying (`Copy Wall`), and after closing any definition editor dialog.
- [x] Wall configuration dialog supporting switching between all project walls (similar to Materials and Studs dialogs) with New Wall, Save Wall, Delete Wall, Close commands and live selection sync.
- [x] Calculation Log & Analysis Summary Dialog:
  - [x] Removed calculation log from the bottom of the left sidebar per markup, allowing the Model Explorer to occupy full sidebar height.
  - [x] Created `CalculationLogDialog` modal window that automatically pops up upon running analysis (`Run Sizing`), presenting the full plain-text CSA O86-20 calculation log and audit trail with a "Copy Log" clipboard button.
- [x] Main Canvas Area:
  - [x] Removed `Stud Cross-Section Detail` tab per markup.
  - [x] `WallGraphicsCanvas` (Building Plan View) directly occupies the main graphics view with tributary width and load toggles.

### Completed Engineering & UI Improvements (2026-10-02):
- [x] Walls Dialog Multi-Wall Switcher (`WallEditorDialog.axaml`, `WallEditorViewModel.cs`):
  - [x] **Left-hand Wall Selector**: Added standard `ListBox` on the left of the dialog displaying all project walls, matching the interaction pattern in `MaterialsDialog` and `StudsDialog`.
  - [x] **Seamless Wall Switching**: Selecting a wall loads its properties, tributary widths table, and assigned story loads. Unsaved edits to the outgoing wall are automatically committed so inputs are never lost when clicking another wall.
  - [x] **Reactive Domain Model**: Updated [`Wall`](file:///home/mwrh/Documents/Repos/StudWalls/src/StudWalls.Core/Models/Wall.cs) to inherit from `ObservableObject`, enabling live property notifications and immediate list name updates when renaming walls.
  - [x] **Standard Action Buttons**: Added `New Wall`, `Save Wall`, `Delete Wall`, and `Close` buttons in the bottom action bar, aligning with all other entity dialogs.
  - [x] **Selection Persistence**: Enhanced `RefreshProjectData()` in [`MainViewModel`](file:///home/mwrh/Documents/Repos/StudWalls/src/StudWalls.Desktop/ViewModels/MainViewModel.cs) to preserve the selected wall and active story across dialog close and collection rebuild events.
- [x] Report Design Equations & Governing Axial Capacity Tables (`DesignReportGenerator.cs`, `PdfReportExporter.cs`):
  - [x] **CSA O86-20 Code Equations & Clauses**: Documented and rendered the 6 governing equations and clause references:
    - Slenderness Ratio $C_c = L_u / d \le 50$ (CSA O86-20 Clause 6.5.6.2.2)
    - Factored Compressive Strength $F_c = f_c \cdot (K_D \cdot K_H \cdot K_{Sc} \cdot K_T)$ (Clause 6.5.6.2.3)
    - Size Factor $K_{Zc} = \min(6.3 \cdot (d \cdot L_u)^{-0.13}, 1.30)$ (Clause 6.5.6.2.5)
    - Column Stability Factor $K_c = [1.0 + (F_c \cdot K_{Zc} \cdot C_c^3) / (35 \cdot E_{05} \cdot K_{Se} \cdot K_T)]^{-1}$ (Clause 6.5.6.2.4)
    - Factored Compressive Resistance $P_r = \phi \cdot F_c \cdot A_g \cdot K_c \cdot K_{Zc}$ with $\phi = 0.80$ (Clause 6.5.6.2.1 / 6.5.6.2.3)
    - Demand-to-Capacity Check $D/C = P_f / P_r \le 1.00$ ($P_f = w_f \cdot \text{Spacing}$, Clause 6.5.6.2)
  - [x] **Governing Axial Capacities Table**: Added per-floor tables listing candidate stud evaluations under the governing load combination (Member, Spacing, $A_g$, $C_c$, $K_D$, $K_{Zc}$, $K_c$, $P_f$, $P_r$, $D/C$, Status) with clear indication of the finalized/selected option.
  - [x] **Multi-Page Vector PDF Pagination**: Implemented dynamic page-break calculation in `PdfReportExporter.cs` ensuring multi-story structures paginate cleanly without clipping.
  - [x] **Results Dock Streamlining & Passing Solutions Filter** (`MainWindow.axaml`, `MainViewModel.cs`, `DesignResult.cs`):
    - [x] **Passing Solutions Only**: Filtered `CurrentResults` in `MainViewModel` to display passing configurations ($D/C \le 1.0$) sorted by Wood Volume ascending per floor level. If no candidate passes, displays evaluated candidates as an engineering fallback.
    - [x] **Concise Columns**: Streamlined the Results table from detailed breakdowns to the exact 6 columns requested: `Level`, `Member` (`plys-section`, e.g. `1-2x4`, `2-2x4`, `1-2x6`), `Spacing` (e.g. `16"`, `12"`), `Gov D/C` (e.g. `0.98`), `Wood Volume` (e.g. `1.135`), and `Final Selection` (CheckBox).
    - [x] **Radio-like Final Selection**: Made `DesignResult` inherit `ObservableObject` with an automated `OnIsFinalChanged` handler enforcing single final specification per story.
  - [x] **Results Dialog with Per-Level Filtering** (`ResultsDialog.axaml`, `ResultsViewModel.cs`, `MainWindow.axaml`, `MainViewModel.cs`):
    - [x] **Dedicated Results Dialog**: Created full-sized modal `ResultsDialog` presenting evaluated member sizing options with ample vertical space.
    - [x] **Level Filter Dropdown**: Filter results by "All Levels" or focus specifically on a single story (e.g. "Level 1", "Level 2"), eliminating long list scrolling.
    - [x] **Show Passing Only Toggle**: Quick toggle between passing options ($D/C \le 1.0$) and all evaluated options.
    - [x] **Integrated Workflow**: Automatically launches upon clicking "Run Sizing", accessible from the Toolbar ("Results"), from the Results dock ("Open in Dialog..."), and from the Model Explorer under "Analysis & Design".
    - [x] **Actions**: Includes "Generate Report...", "Finalize & Save" (persisting selections), and "Close".

- [x] User-Selectable Sizing Criteria & Optimization Scope:
  - [x] Model for selecting allowed stud sections (e.g. 2x4, 2x6, 2x8), species/grades, maximum plys (1, 2, 3), and allowed spacings (12", 16", 24", 8") (`SizingCriteria.cs`).
  - [x] `SizingCriteriaDialog.axaml` and `SizingCriteriaViewModel.cs` launched directly upon clicking "Run Sizing" and accessible from Results dialog.
  - [x] Criteria persisted in project file (`.swproj` SQLite table and JSON).
  - [x] Updated `StudWallEngine` to evaluate only user-selected candidate permutations.
  - [x] Full unit test coverage in `EngineeringTests.cs` (17 tests passing).

### Queued for Next Tasks:
- [ ] DXF Import and Tracing / Drawing of Walls (Next Priority):
  - Import CAD DXF floor plans (.dxf) as canvas background underlay / vector layers.
  - Layer visibility toggles and scale calibration.
  - Tracing and interactive drawing tools for walls (click start/end points, ortho snapping, length inputs).
  - Tracing tools for floor tributary areas and load assignments.
- [ ] Plan canvas interactivity enhancements:
  - Click-to-select wall directly on 2D Plan View canvas (synchronizing with Model Explorer and Results).
  - Mouse click-and-drag to reposition walls on the floor plan canvas.
- [ ] Dynamic unit conversion reactivity across all open dialog inputs when toggling Metric $\leftrightarrow$ Imperial in Preferences.
- [ ] Project templates (e.g., 2-story residential wood frame, 4-story light commercial).
- [ ] Additional custom engineering rules, wind/seismic shear wall checks, or print layout tweaks as requested.