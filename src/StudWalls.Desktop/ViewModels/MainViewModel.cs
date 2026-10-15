using System.Collections.ObjectModel;
using Avalonia.Controls;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using StudWalls.Core.Data;
using StudWalls.Core.Engineering;
using StudWalls.Core.Enums;
using StudWalls.Core.Models;
using StudWalls.Core.Reporting;

namespace StudWalls.Desktop.ViewModels;

/// <summary>
/// Primary coordinator ViewModel for the StudWalls desktop application.
/// Manages active project state, wall selection, calculation runs, results finalization,
/// and interactions with child editors and graphics canvases.
/// </summary>
public partial class MainViewModel : ViewModelBase
{
    private readonly StudWallEngine _engine = new();

    public ProjectManager ProjectManager { get; }

    [ObservableProperty]
    private string _statusMessage = "Ready";

    [ObservableProperty]
    private string _calculationSummary = "Click 'Run Analysis & Sizing' to calculate the active wall.";

    [ObservableProperty]
    private Wall? _selectedWall;

    [ObservableProperty]
    private Story? _activeStory;

    [ObservableProperty]
    private bool _showTributaries = true;

    [ObservableProperty]
    private bool _showLoads = true;

    /// <summary>
    /// Controls whether the bottom resizable engineering results dock panel is expanded or collapsed.
    /// When true, opens up below the main graphics canvas with a draggable splitter.
    /// </summary>
    [ObservableProperty]
    private bool _isResultsOpen = true;

    /// <summary>
    /// Height of the bottom results dock row. Bound TwoWay so dragging the GridSplitter updates this value.
    /// </summary>
    [ObservableProperty]
    private GridLength _resultsRowHeight = new(320, GridUnitType.Pixel);

    private double _previousResultsHeight = 320.0;

    /// <summary>
    /// Status text showing how many passing stud sizing options were evaluated for the active wall.
    /// </summary>
    public string ResultsCountText
    {
        get
        {
            if (CurrentResults.Count == 0) return "(No results yet - click 'Run Sizing')";
            int passCount = CurrentResults.Count(r => r.DcRatio <= 1.0001);
            if (passCount > 0)
                return $"({passCount} passing options)";
            return $"({CurrentResults.Count} evaluated - none pass D/C <= 1.0)";
        }
    }

    /// <summary>
    /// Label for the results open/collapse toggle button.
    /// </summary>
    public string ResultsToggleLabel => IsResultsOpen ? "Hide Results ▼" : "Show Results ▲";

    public ObservableCollection<Wall> Walls { get; } = new();
    public ObservableCollection<Story> Stories { get; } = new();
    public ObservableCollection<DesignResult> CurrentResults { get; } = new();

    /// <summary>
    /// The currently selected candidate stud option in the bottom results table.
    /// When selected, its full multi-load combination breakdown is displayed below it.
    /// </summary>
    [ObservableProperty]
    private DesignResult? _selectedResult;

    /// <summary>
    /// Hierarchical items for the ETABS-like Model Explorer tree view in the left sidebar.
    /// </summary>
    public ObservableCollection<ModelExplorerNode> ExplorerNodes { get; } = new();

    [ObservableProperty]
    private ModelExplorerNode? _selectedExplorerNode;

    private bool _isSyncingTreeSelection;

    partial void OnSelectedExplorerNodeChanged(ModelExplorerNode? value)
    {
        ActivateSelectedNodeCommand.NotifyCanExecuteChanged();
        if (value == null || _isSyncingTreeSelection) return;

        // Synchronize active wall or story when selected in tree view
        if (value.Tag is Wall wall)
        {
            _isSyncingTreeSelection = true;
            SelectedWall = wall;
            _isSyncingTreeSelection = false;
        }
        else if (value.Tag is Story story)
        {
            ActiveStory = story;
        }
    }

    public bool CanActivateSelectedNode => SelectedExplorerNode != null;

    [RelayCommand(CanExecute = nameof(CanActivateSelectedNode))]
    public void ActivateSelectedNode()
    {
        SelectedExplorerNode?.OnActivate?.Invoke();
    }

    // Dialog launch action delegates wired by the View/Code-behind
    public Action? ShowMaterialsDialogRequested { get; set; }
    public Action? ShowStudsDialogRequested { get; set; }
    public Action? ShowLevelsDialogRequested { get; set; }
    public Action? ShowLoadsDialogRequested { get; set; }
    public Action? ShowLoadCombosDialogRequested { get; set; }
    public Action? ShowWallEditorRequested { get; set; }
    public Action? ShowAboutDialogRequested { get; set; }
    public Action? ShowPreferencesDialogRequested { get; set; }
    public Action<string, string>? ShowCalculationLogRequested { get; set; }
    public Action<Wall, Action<SizingCriteria>>? ShowSizingCriteriaDialogRequested { get; set; }
    public Action<Wall>? ShowResultsDialogRequested { get; set; }
    public Action<string>? ShowReportRequested { get; set; }
    public Func<string, Task<string?>>? RequestSaveFilePath { get; set; }
    public Func<string, Task<string?>>? RequestOpenFilePath { get; set; }

    public MainViewModel()
    {
        ProjectManager = new ProjectManager();
        RefreshProjectData();
    }

    /// <summary>
    /// Synchronizes ViewModel observable collections with the underlying ProjectManager models.
    /// Rebuilds the ETABS-style Model Explorer tree view.
    /// </summary>
    public void RefreshProjectData()
    {
        int? currentWallId = SelectedWall?.Id;
        int? currentStoryId = ActiveStory?.Id;

        Walls.Clear();
        foreach (var w in ProjectManager.Walls) Walls.Add(w);

        Stories.Clear();
        foreach (var s in ProjectManager.Stories) Stories.Add(s);

        SelectedWall = Walls.FirstOrDefault(w => w.Id == currentWallId) ?? Walls.FirstOrDefault();
        ActiveStory = Stories.FirstOrDefault(s => s.Id == currentStoryId) ?? Stories.FirstOrDefault();

        RefreshCurrentResults();
        BuildModelExplorerTree();
        OnPropertyChanged(nameof(ProjectManager));
    }

    /// <summary>
    /// Constructs the ETABS-like Model Explorer hierarchical tree view.
    /// Organizes Project Info, Structural Definitions (Materials, Studs, Levels, Loads, Combos),
    /// Structural Objects (Walls), and Analysis actions into navigable branches.
    /// </summary>
    public void BuildModelExplorerTree()
    {
        ExplorerNodes.Clear();

        var root = new ModelExplorerNode
        {
            Title = $"Project: {ProjectManager.Project.ProjectName}",
            Subtitle = ProjectManager.Project.ProjectNumber,
            NodeType = ExplorerNodeType.RootProject,
            IsExpanded = true
        };

        // 1. Project Information
        var projInfoNode = new ModelExplorerNode
        {
            Title = "Project Information & Settings",
            Subtitle = $"Engineer: {ProjectManager.Project.Engineer}",
            NodeType = ExplorerNodeType.ProjectInfo,
            OnActivate = OpenPreferences
        };
        root.Children.Add(projInfoNode);

        // 2. Properties & Definitions
        var defsNode = new ModelExplorerNode
        {
            Title = "Structural Definitions",
            NodeType = ExplorerNodeType.DefinitionsCategory,
            IsExpanded = false
        };

        // Materials branch
        var matsNode = new ModelExplorerNode
        {
            Title = "Wood Materials",
            Subtitle = $"{ProjectManager.Materials.Count} materials",
            NodeType = ExplorerNodeType.MaterialsGroup,
            OnActivate = OpenMaterials
        };
        foreach (var mat in ProjectManager.Materials)
        {
            matsNode.Children.Add(new ModelExplorerNode
            {
                Title = mat.Name,
                Subtitle = $"{mat.Species} {mat.Grade}",
                NodeType = ExplorerNodeType.MaterialItem,
                Tag = mat,
                OnActivate = OpenMaterials
            });
        }
        defsNode.Children.Add(matsNode);

        // Stud Sections branch
        var studsNode = new ModelExplorerNode
        {
            Title = "Stud Cross-Sections",
            Subtitle = $"{ProjectManager.Studs.Count} sections",
            NodeType = ExplorerNodeType.StudsGroup,
            OnActivate = OpenStuds
        };
        foreach (var stud in ProjectManager.Studs)
        {
            studsNode.Children.Add(new ModelExplorerNode
            {
                Title = stud.Name,
                Subtitle = $"{stud.Section.Width:F0}x{stud.Section.Depth:F0} mm",
                NodeType = ExplorerNodeType.StudItem,
                Tag = stud,
                OnActivate = OpenStuds
            });
        }
        defsNode.Children.Add(studsNode);

        // Stories / Levels branch
        var storiesNode = new ModelExplorerNode
        {
            Title = "Building Stories / Levels",
            Subtitle = $"{ProjectManager.Stories.Count} levels",
            NodeType = ExplorerNodeType.StoriesGroup,
            OnActivate = OpenLevels
        };
        foreach (var story in ProjectManager.Stories)
        {
            storiesNode.Children.Add(new ModelExplorerNode
            {
                Title = story.Name,
                Subtitle = $"Height: {story.Height:F0} mm",
                NodeType = ExplorerNodeType.StoryItem,
                Tag = story,
                OnActivate = () => { ActiveStory = story; OpenLevels(); }
            });
        }
        defsNode.Children.Add(storiesNode);

        // Specified Loads branch
        var loadsNode = new ModelExplorerNode
        {
            Title = "Specified Loads",
            Subtitle = $"{ProjectManager.Loads.Count} cases",
            NodeType = ExplorerNodeType.LoadsGroup,
            OnActivate = OpenLoads
        };
        foreach (var load in ProjectManager.Loads)
        {
            loadsNode.Children.Add(new ModelExplorerNode
            {
                Title = load.Name,
                Subtitle = $"{load.Value:F2} kPa ({load.Case})",
                NodeType = ExplorerNodeType.LoadItem,
                Tag = load,
                OnActivate = OpenLoads
            });
        }
        defsNode.Children.Add(loadsNode);

        // Load Combinations branch
        var combosNode = new ModelExplorerNode
        {
            Title = "Load Combinations (NBCC)",
            Subtitle = $"{ProjectManager.LoadCombinations.Count} combos",
            NodeType = ExplorerNodeType.LoadCombosGroup,
            OnActivate = OpenLoadCombos
        };
        foreach (var combo in ProjectManager.LoadCombinations)
        {
            combosNode.Children.Add(new ModelExplorerNode
            {
                Title = combo.Name,
                NodeType = ExplorerNodeType.LoadComboItem,
                Tag = combo,
                OnActivate = OpenLoadCombos
            });
        }
        defsNode.Children.Add(combosNode);

        root.Children.Add(defsNode);

        // 3. Structural Model Objects (Walls)
        var modelNode = new ModelExplorerNode
        {
            Title = "Structural Objects",
            NodeType = ExplorerNodeType.ModelCategory,
            IsExpanded = false
        };
        var wallsGroupNode = new ModelExplorerNode
        {
            Title = "Walls",
            Subtitle = $"{ProjectManager.Walls.Count} walls",
            NodeType = ExplorerNodeType.WallsGroup,
            OnActivate = OpenWallEditor
        };
        foreach (var wall in ProjectManager.Walls)
        {
            wallsGroupNode.Children.Add(new ModelExplorerNode
            {
                Title = wall.Name,
                Subtitle = $"Length: {wall.Length:F0} mm, {wall.Stories.Count} floors",
                NodeType = ExplorerNodeType.WallItem,
                Tag = wall,
                OnActivate = () => { SelectedWall = wall; OpenWallEditor(); }
            });
        }
        modelNode.Children.Add(wallsGroupNode);
        root.Children.Add(modelNode);

        // 4. Analysis & Design Actions
        var analysisNode = new ModelExplorerNode
        {
            Title = "Analysis & Design",
            NodeType = ExplorerNodeType.AnalysisCategory,
            IsExpanded = false
        };
        analysisNode.Children.Add(new ModelExplorerNode
        {
            Title = "Run Analysis & Sizing",
            Subtitle = "CSA O86-20 code checks",
            NodeType = ExplorerNodeType.RunAnalysisAction,
            OnActivate = RunCalculation
        });
        analysisNode.Children.Add(new ModelExplorerNode
        {
            Title = "Engineering Results",
            Subtitle = "View passing options by level",
            NodeType = ExplorerNodeType.ReportAction,
            OnActivate = OpenResultsDialog
        });
        analysisNode.Children.Add(new ModelExplorerNode
        {
            Title = "Calculation Report",
            Subtitle = "Preview and PDF export",
            NodeType = ExplorerNodeType.ReportAction,
            OnActivate = GenerateReport
        });
        analysisNode.Children.Add(new ModelExplorerNode
        {
            Title = "Application Preferences",
            Subtitle = "Units and defaults",
            NodeType = ExplorerNodeType.PreferencesAction,
            OnActivate = OpenPreferences
        });
        root.Children.Add(analysisNode);

        ExplorerNodes.Add(root);
    }

    partial void OnSelectedWallChanged(Wall? value)
    {
        RefreshCurrentResults();
        StatusMessage = value != null ? $"Active Wall: {value.Name}" : "No wall selected";

        if (!_isSyncingTreeSelection && value != null)
        {
            var node = FindNodeByTag(ExplorerNodes, value);
            if (node != null && SelectedExplorerNode != node)
            {
                _isSyncingTreeSelection = true;
                SelectedExplorerNode = node;
                _isSyncingTreeSelection = false;
            }
        }
    }

    private static ModelExplorerNode? FindNodeByTag(IEnumerable<ModelExplorerNode> nodes, object targetTag)
    {
        foreach (var node in nodes)
        {
            if (ReferenceEquals(node.Tag, targetTag) || Equals(node.Tag, targetTag))
            {
                return node;
            }
            var childMatch = FindNodeByTag(node.Children, targetTag);
            if (childMatch != null) return childMatch;
        }
        return null;
    }

    partial void OnIsResultsOpenChanged(bool value)
    {
        if (value)
        {
            // Restore previous height or default 240px
            ResultsRowHeight = new GridLength(_previousResultsHeight > 60 ? _previousResultsHeight : 240, GridUnitType.Pixel);
        }
        else
        {
            // Remember current height before collapsing down to the header dock bar
            if (ResultsRowHeight.IsAbsolute && ResultsRowHeight.Value > 60)
            {
                _previousResultsHeight = ResultsRowHeight.Value;
            }
            ResultsRowHeight = new GridLength(32, GridUnitType.Pixel);
        }

        OnPropertyChanged(nameof(ResultsToggleLabel));
    }

    private void RefreshCurrentResults()
    {
        CurrentResults.Clear();
        if (SelectedWall == null)
        {
            OnPropertyChanged(nameof(ResultsCountText));
            return;
        }

        foreach (var ws in SelectedWall.Stories)
        {
            // Only show passing solutions (D/C <= 1.0) sorted by wood volume ascending
            var passing = ws.Results.Where(r => r.DcRatio <= 1.0001).OrderBy(r => r.WoodVolume).ToList();
            if (passing.Count > 0)
            {
                foreach (var r in passing)
                {
                    CurrentResults.Add(r);
                }
            }
            else
            {
                // Fallback: If no candidate passed this floor level, display evaluated options so engineer can review overstress
                foreach (var r in ws.Results.OrderBy(r => r.WoodVolume))
                {
                    CurrentResults.Add(r);
                }
            }
        }

        SelectedResult = CurrentResults.FirstOrDefault(r => r.IsFinal) ?? CurrentResults.FirstOrDefault();

        OnPropertyChanged(nameof(ResultsCountText));
    }

    [RelayCommand]
    public void ToggleResults()
    {
        IsResultsOpen = !IsResultsOpen;
    }

    [RelayCommand]
    public void RunCalculation()
    {
        if (SelectedWall == null)
        {
            StatusMessage = "Please select a wall to analyze.";
            return;
        }

        // Present the Sizing Criteria dialog per user preference before running analysis
        if (ShowSizingCriteriaDialogRequested != null)
        {
            ShowSizingCriteriaDialogRequested.Invoke(SelectedWall, criteria =>
            {
                ExecuteCalculationWithCriteria(criteria);
            });
        }
        else
        {
            ExecuteCalculationWithCriteria(ProjectManager.SizingCriteria);
        }
    }

    public void ExecuteCalculationWithCriteria(SizingCriteria criteria)
    {
        if (SelectedWall == null) return;

        StatusMessage = $"Analyzing {SelectedWall.Name} per CSA O86-20...";

        var (summary, detailed) = _engine.Calculate(
            SelectedWall,
            ProjectManager.Studs,
            ProjectManager.LoadCombinations,
            criteria);

        CalculationSummary = summary;
        RefreshCurrentResults();

        // Automatically open up the results panel from below the main canvas
        IsResultsOpen = true;

        StatusMessage = $"Calculation complete for {SelectedWall.Name}.";
        ProjectManager.IsDirty = true;

        // Automatically open the dedicated results dialog with level filtering
        ShowResultsDialogRequested?.Invoke(SelectedWall);
    }

    [RelayCommand]
    public void OpenResultsDialog()
    {
        if (SelectedWall == null)
        {
            StatusMessage = "Please select a wall to view results.";
            return;
        }

        ShowResultsDialogRequested?.Invoke(SelectedWall);
    }

    [RelayCommand]
    public void FinalizeResults()
    {
        if (SelectedWall == null) return;

        // Persist selections
        ProjectManager.IsDirty = true;
        StatusMessage = $"Finalized design results saved for {SelectedWall.Name}.";
    }

    [RelayCommand]
    public void NewProject()
    {
        ProjectManager.CreateNewProject();
        RefreshProjectData();
        CalculationSummary = "New project created.";
        StatusMessage = "New project initialized.";
    }

    [RelayCommand]
    public async Task OpenProjectAsync()
    {
        if (RequestOpenFilePath == null) return;

        var path = await RequestOpenFilePath("Open Project File (*.swproj;*.json)");
        if (string.IsNullOrWhiteSpace(path)) return;

        try
        {
            ProjectManager.OpenProject(path);
            RefreshProjectData();
            CalculationSummary = $"Loaded project from: {Path.GetFileName(path)}";
            StatusMessage = $"Project loaded: {path}";
        }
        catch (Exception ex)
        {
            StatusMessage = $"Error opening project: {ex.Message}";
        }
    }

    [RelayCommand]
    public async Task SaveProjectAsync()
    {
        if (string.IsNullOrWhiteSpace(ProjectManager.CurrentFilePath))
        {
            await SaveProjectAsAsync();
            return;
        }

        try
        {
            ProjectManager.SaveProject();
            StatusMessage = $"Project saved to {ProjectManager.CurrentFilePath}";
        }
        catch (Exception ex)
        {
            StatusMessage = $"Error saving project: {ex.Message}";
        }
    }

    [RelayCommand]
    public async Task SaveProjectAsAsync()
    {
        if (RequestSaveFilePath == null) return;

        var path = await RequestSaveFilePath("Save Project File (*.swproj)");
        if (string.IsNullOrWhiteSpace(path)) return;

        try
        {
            ProjectManager.SaveProject(path);
            StatusMessage = $"Project saved as {path}";
        }
        catch (Exception ex)
        {
            StatusMessage = $"Error saving project: {ex.Message}";
        }
    }

    [RelayCommand]
    public async Task ExportJsonAsync()
    {
        if (RequestSaveFilePath == null) return;

        var path = await RequestSaveFilePath("Export JSON File (*.json)");
        if (string.IsNullOrWhiteSpace(path)) return;

        try
        {
            ProjectManager.ExportToJson(path);
            StatusMessage = $"Exported project JSON to {path}";
        }
        catch (Exception ex)
        {
            StatusMessage = $"Export failed: {ex.Message}";
        }
    }

    [RelayCommand]
    public async Task ImportJsonAsync()
    {
        if (RequestOpenFilePath == null) return;

        var path = await RequestOpenFilePath("Import JSON File (*.json)");
        if (string.IsNullOrWhiteSpace(path)) return;

        try
        {
            ProjectManager.ImportFromJson(path);
            RefreshProjectData();
            StatusMessage = $"Imported project from JSON: {path}";
        }
        catch (Exception ex)
        {
            StatusMessage = $"Import failed: {ex.Message}";
        }
    }

    [RelayCommand]
    public void NewWall()
    {
        int newId = ProjectManager.Walls.Count > 0 ? ProjectManager.Walls.Max(w => w.Id) + 1 : 1;
        var newWall = new Wall
        {
            Id = newId,
            Name = $"Wall {newId}",
            Length = 5000.0,
            SelfWeight = 0.50,
            PlanX = 1000.0 + (ProjectManager.Walls.Count * 1200.0),
            PlanY = 1000.0
        };

        // Attach top 3 stories by default
        foreach (var s in ProjectManager.Stories.Take(3))
        {
            newWall.Stories.Add(new WallStory
            {
                WallId = newWall.Id,
                Wall = newWall,
                StoryId = s.Id,
                Story = s,
                TribWidthLeft = 1000.0,
                TribWidthRight = 1500.0,
                LuDepth = s.Height,
                LuWidth = 152.0
            });
        }

        ProjectManager.Walls.Add(newWall);
        Walls.Add(newWall);
        BuildModelExplorerTree();
        SelectedWall = newWall;
        StatusMessage = $"Created {newWall.Name}";
        ProjectManager.IsDirty = true;
    }

    [RelayCommand]
    public void DeleteWall()
    {
        if (SelectedWall == null) return;

        var toRemove = SelectedWall;
        ProjectManager.Walls.Remove(toRemove);
        Walls.Remove(toRemove);
        SelectedWall = Walls.FirstOrDefault();
        BuildModelExplorerTree();

        StatusMessage = $"Deleted {toRemove.Name}";
        ProjectManager.IsDirty = true;
    }

    [RelayCommand]
    public void CopyWall()
    {
        if (SelectedWall == null) return;

        int newId = ProjectManager.Walls.Max(w => w.Id) + 1;
        var clone = new Wall
        {
            Id = newId,
            Name = $"{SelectedWall.Name} (Copy)",
            Length = SelectedWall.Length,
            SelfWeight = SelectedWall.SelfWeight,
            PlanX = SelectedWall.PlanX + 500.0,
            PlanY = SelectedWall.PlanY + 500.0,
            RotationDegrees = SelectedWall.RotationDegrees
        };

        foreach (var ws in SelectedWall.Stories)
        {
            var wsClone = new WallStory
            {
                WallId = clone.Id,
                Wall = clone,
                StoryId = ws.StoryId,
                Story = ws.Story,
                TribWidthLeft = ws.TribWidthLeft,
                TribWidthRight = ws.TribWidthRight,
                LuDepth = ws.LuDepth,
                LuWidth = ws.LuWidth,
                LoadsLeft = new List<Load>(ws.LoadsLeft),
                LoadsRight = new List<Load>(ws.LoadsRight)
            };
            clone.Stories.Add(wsClone);
        }

        ProjectManager.Walls.Add(clone);
        Walls.Add(clone);
        BuildModelExplorerTree();
        SelectedWall = clone;
        StatusMessage = $"Copied {SelectedWall.Name}";
        ProjectManager.IsDirty = true;
    }

    [RelayCommand]
    public void GenerateReport()
    {
        if (SelectedWall == null)
        {
            StatusMessage = "Please select a wall to generate a report.";
            return;
        }

        var reportText = DesignReportGenerator.GenerateReport(
            ProjectManager.Project,
            SelectedWall,
            ProjectManager.Loads,
            ProjectManager.LoadCombinations,
            ProjectManager.Studs,
            ProjectManager.Materials);

        ShowReportRequested?.Invoke(reportText);
    }

    [RelayCommand] public void OpenMaterials() => ShowMaterialsDialogRequested?.Invoke();
    [RelayCommand] public void OpenStuds() => ShowStudsDialogRequested?.Invoke();
    [RelayCommand] public void OpenLevels() => ShowLevelsDialogRequested?.Invoke();
    [RelayCommand] public void OpenLoads() => ShowLoadsDialogRequested?.Invoke();
    [RelayCommand] public void OpenLoadCombos() => ShowLoadCombosDialogRequested?.Invoke();
    [RelayCommand] public void OpenWallEditor() => ShowWallEditorRequested?.Invoke();
    [RelayCommand] public void OpenAbout() => ShowAboutDialogRequested?.Invoke();
    [RelayCommand] public void OpenPreferences() => ShowPreferencesDialogRequested?.Invoke();
}
