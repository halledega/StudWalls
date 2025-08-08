# Product Requirements Document (PRD)
## Wood Frame Stud Wall Sizing Application (CSA O86)

### 1. Project Overview

**Application Name:** Stud Wall Sizer Pro  
**Primary Purpose:** Size wood frame stud walls according to CSA O86 engineering standards  
**Target Users:** Structural engineers, building designers, and construction professionals  
**Current State:** ~~Basic command-line application structure exists~~ Fully functional command-line application with detailed output.
**Development Language:** Python 3.x  

### 2. MVP Requirements

#### 2.1. Core Functionality Enhancement

##### 2.1.1. Building on Existing Structure
- ~~Extend current command-line functionality to support MVP requirements~~
- ~~Leverage existing Section class implementation (if present)~~
- Enhance current PySide6 UI to include MVP input forms
- ~~Integrate with existing CSA O86 calculation modules~~

##### 2.1.2. Input Management (Enhanced)
- ~~Extend existing input handling to support:~~
  - ~~Number of building levels definition~~
  - ~~Level heights for each floor~~
  - ~~Wall tributary widths per level~~
  - ~~Loads per level (dead load, live load, wind load, seismic load)~~
- Build upon current validation logic
- Integrate input forms into existing PySide6 interface

##### 2.1.3. Stud Section Library (Extension)
- ~~Enhance existing Section class with any missing properties~~
- ~~Extend current stud database with complete standard sizes~~
- ~~Ensure compatibility with existing calculation methods~~
- ~~Maintain current material property storage approach~~

##### 2.1.4. Analysis Engine (Integration)
- ~~Build upon existing calculation framework~~
- ~~Extend current analysis to handle multi-level buildings~~
- ~~Integrate DC ratio calculations with existing code structure~~
- ~~Enhance current results storage and filtering~~

##### 2.1.5. Output Generation (UI Integration)
- Extend existing PySide6 interface to display results
- ~~Build upon current output formatting~~
- Integrate results display with existing UI components
- ~~Maintain compatibility with command-line output~~

#### 2.2. Technical Architecture (Existing Codebase Integration)

##### 2.2.1. Current Structure Analysis
- ~~Review existing class hierarchy and identify reusable components~~
- ~~Assess current Section implementation and extend as needed~~
- Evaluate existing PySide6 UI structure and build upon it
- ~~Identify current calculation modules and enhance for multi-level analysis~~

##### 2.2.2. Integration Approach
```
# Work with existing structure, likely similar to:
StudWalls/
├── [existing files and structure]
├── [enhance existing classes]
└── [extend current modules]
```

##### 2.2.3. Enhancement Strategy
1. **Extend Existing Classes:** ~~Build upon current Section, analysis, and UI classes~~
2. **Preserve Current Logic:** ~~Maintain existing CSA O86 calculations~~
3. **UI Integration:** Enhance PySide6 interface with MVP requirements
4. **Backward Compatibility:** ~~Ensure command-line functionality remains intact~~

### 3. Code Quality Requirements

#### 3.1. Documentation Standards
- Comprehensive docstrings for all classes and methods (Google or NumPy style)
- Inline comments explaining complex calculations and CSA O86 references
- README file with installation, usage, and examples
- Code comments should explain engineering principles, not just code logic

#### 3.2. Code Style
- ~~Follow PEP 8 Python style guidelines strictly for all NEW code~~
- **EXISTING CODE PEP 8:** ~~Identify existing code that doesn't conform to PEP 8, but only propose corrections after user approval~~
- ~~Use descriptive variable names that reflect engineering terminology~~
- ~~Keep functions small and focused (single responsibility principle)~~
- ~~Use type hints for better code clarity~~
- Implement error handling with meaningful error messages

#### 3.3. Third-Party Review Considerations
- ~~Code must be readable by non-programmers (structural engineers)~~
- ~~Use engineering terminology in variable/function names~~
- Include extensive comments explaining CSA O86 code references
- ~~Provide clear separation between input, calculation, and output sections~~
- ~~Use meaningful class and method names that reflect engineering concepts~~

### 4. Technical Specifications

#### 4.1. Dependencies
- Python 3.8+
- PySide6 (already implemented in PySide branch)
- Standard libraries: math, typing, dataclasses
- Optional: pandas (for data management), numpy (for calculations)

#### 4.2. Existing Codebase Integration
- ~~Work with current file structure from StudWalls repository~~
- ~~Utilize existing modules and classes where applicable~~
- Build upon PySide6 implementation already in progress
- ~~Maintain compatibility with existing command-line functionality~~

#### 4.3. Development Approach
- ~~Analyze existing code structure and identify reusable components~~
- ~~Extend current classes rather than rewriting from scratch~~
- ~~Preserve any existing CSA O86 calculations and validation logic~~
- ~~Integrate new features seamlessly with current architecture~~

### 5. Future Features (Post-MVP)

#### 5.1. User Interface Enhancement
- Expand existing PySide6 GUI with advanced input forms
- Add visual building representation and load diagrams
- Implement interactive results display with filtering
- Add export functionality (PDF reports, CSV data)
- Enhance current UI with professional styling and layouts

#### 5.2. Enhanced Analysis (Building on Current)
- Extend existing calculations for advanced load combinations
- Add deflection analysis to current structural checks
- Implement multi-span analysis capabilities
- Enhance current code compliance checking

#### 5.3. Advanced Features
- Build project save/load on existing data structure
- Extend current reporting with detailed calculation steps
- Add database connectivity for project management
- Integrate with other structural analysis modules

### 6. Success Criteria

#### 6.1. MVP Success Metrics
- ~~Successfully analyze a 3-story building with different loads per level~~
- ~~Generate accurate DC ratios matching hand calculations~~
- ~~Produce clear, understandable output for engineering review~~
- ~~Code passes review by non-programmer structural engineers~~
- All calculations traceable to CSA O86 code sections

#### 6.2. Quality Metrics
- 100% of code covered by docstrings
- All engineering calculations include CSA O86 clause references
- Error handling covers all anticipated input scenarios
- Code review approval from structural engineering team

### 7. AI Agent Guidelines

#### 7.1. Critical First Step
- **REVIEW EXISTING CODE FIRST:** Before making any changes or suggestions, thoroughly analyze the entire StudWalls codebase, particularly the PySide6 branch. Understand the current file structure, existing classes, implemented functionality, UI components, calculation methods, and coding patterns. This review is mandatory before proceeding with any development work.
- **NO CHANGES WITHOUT CONFIRMATION:** Never modify, delete, or refactor existing code without explicit user approval. Always propose changes and wait for confirmation before implementing them.

#### 7.2. Development Approach
- **Work WITH Existing Code:** Always extend and enhance existing functionality rather than replacing it
- **Preserve All Current Features:** Ensure existing command-line and UI capabilities remain fully intact
- **Request Permission for Changes:** Before modifying any existing code, clearly explain what needs to be changed and why, then wait for explicit approval
- **Add, Don't Alter:** Focus on adding new features and capabilities to existing structure
- **Incremental Development:** Add features step-by-step to existing structure without breaking current functionality

#### 7.3. Integration Strategy
- Study existing PySide6 implementation and extend it
- Identify current Section class properties and enhance as needed
- Work with existing calculation modules and add multi-level support
- Maintain compatibility with current file structure and naming conventions

#### 7.4. Documentation Requirements
- Document all changes and extensions to existing code
- Explain how new features integrate with current structure
- Provide migration notes for any modified existing functionality
- Include rationale for architectural decisions when extending current code

#### 7.5. Existing Codebase Considerations
- **Respect All Current Code:** Never assume existing code needs improvement without user request
- **Maintain Exact Compatibility:** Ensure all existing functionality works exactly as before
- **Propose, Don't Implement:** When identifying potential improvements (including PEP 8 violations), propose changes but wait for approval before implementing
- **Extend Existing Patterns:** Use current coding style and patterns when adding new features
- **Zero Breaking Changes:** New features must not break or alter existing functionality

### 8. Constraints and Assumptions

#### 8.1. Technical Constraints
- Must comply with CSA O86-19 (or latest version)
- Python-based solution required
- Must be maintainable by structural engineers with basic coding knowledge

#### 8.2. Engineering Assumptions
- Standard wood construction methods
- Typical residential/commercial building loads
- Pin-pin column conditions (unless specified otherwise)
- Standard lumber grades and species

#### 8.3. Project Constraints
- ~~MVP must be completed before UI development~~
- Code must pass structural engineering review
- All calculations must be verifiable against manual methods

### 9. Deliverables

#### 9.1. MVP Phase
- ~~Fully functional command-line application~~
- Complete documentation package
- Unit test suite with >90% coverage
- Example usage scenarios with validation

#### 9.2. Future Phases
- PySide6 GUI implementation
- Advanced analysis features
- Professional report generation
- User manual and training materials

### 10. Next Steps

1.  **Develop PySide6 GUI:** Create the graphical user interface for inputting wall parameters and viewing results.
2.  **Implement Unit Tests:** Build a comprehensive test suite to ensure the accuracy and reliability of the calculations.
3.  **Add Deflection Analysis:** Enhance the analysis engine to include deflection checks based on serviceability limit states.