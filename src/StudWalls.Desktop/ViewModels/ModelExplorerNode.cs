using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;

namespace StudWalls.Desktop.ViewModels;

/// <summary>
/// Identifies the structural engineering entity or action represented by an explorer tree node.
/// Mirrors standard structural BIM software organizational taxonomy (e.g., ETABS Model Explorer).
/// </summary>
public enum ExplorerNodeType
{
    RootProject,
    ProjectInfo,
    DefinitionsCategory,
    MaterialsGroup,
    MaterialItem,
    StudsGroup,
    StudItem,
    StoriesGroup,
    StoryItem,
    LoadsGroup,
    LoadItem,
    LoadCombosGroup,
    LoadComboItem,
    ModelCategory,
    WallsGroup,
    WallItem,
    AnalysisCategory,
    RunAnalysisAction,
    ReportAction,
    PreferencesAction
}

/// <summary>
/// Represents a hierarchical item in the ETABS-like Model Explorer tree view.
/// 
/// Organizes project data into an engineering model tree:
/// 1. Project Information & Metadata
/// 2. Structural Definitions (Wood Materials, Stud Cross-Sections, Stories/Levels, Specified Loads, NBCC Combinations)
/// 3. Structural Model Objects (Wall elements and their assigned stories)
/// 4. Analysis and Code Checking Actions (CSA O86 calculation execution and report generation)
/// 
/// Single-clicking an object node (such as a Wall or Story) synchronizes the active selection
/// across the 2D Plan View graphics canvas and results table. Double-clicking any definition
/// or object opens its dedicated editing dialog.
/// </summary>
public partial class ModelExplorerNode : ObservableObject
{
    [ObservableProperty]
    private string _title = string.Empty;

    [ObservableProperty]
    private string? _subtitle;

    [ObservableProperty]
    private bool _isExpanded;

    [ObservableProperty]
    private bool _isSelected;

    /// <summary>
    /// Semantic category of the node in the structural engineering hierarchy.
    /// </summary>
    public ExplorerNodeType NodeType { get; set; } = ExplorerNodeType.RootProject;

    /// <summary>
    /// Underlying domain entity associated with this node (e.g. Wall, WoodMaterial, Stud, Story, Load, LoadCombination).
    /// </summary>
    public object? Tag { get; set; }

    /// <summary>
    /// Callback action executed when this node is activated (via double-click or editor shortcut).
    /// </summary>
    public Action? OnActivate { get; set; }

    /// <summary>
    /// Sub-nodes nested beneath this node in the model hierarchy.
    /// </summary>
    public ObservableCollection<ModelExplorerNode> Children { get; } = new();

    /// <summary>
    /// Human-readable display label formatted with descriptive structural metadata.
    /// Example: "Roof (Height: 2700 mm)" or "SPF No.1/No.2 (Sawn)".
    /// </summary>
    public string DisplayText => string.IsNullOrWhiteSpace(Subtitle)
        ? Title
        : $"{Title} ({Subtitle})";

    public override string ToString() => DisplayText;
}
