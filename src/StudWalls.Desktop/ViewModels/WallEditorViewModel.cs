using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using StudWalls.Core.Models;

namespace StudWalls.Desktop.ViewModels;

/// <summary>
/// ViewModel managing the detailed configuration and geometry of load-bearing wood stud walls:
/// allows switching between all project walls (similar to Materials and Studs dialogs),
/// editing wall dimensions (length, self-weight), vertical story span, tributary widths,
/// unsupported buckling lengths (CSA O86-20 Clause 6.5.6.2.2), and applied story loads.
/// </summary>
public partial class WallEditorViewModel : ViewModelBase
{
    private readonly IList<Wall> _allWalls;
    private readonly IReadOnlyList<Story> _allStories;
    private readonly IReadOnlyList<Load> _allLoads;

    /// <summary>
    /// Collection of all walls in the project displayed in the selector list on the left.
    /// </summary>
    public ObservableCollection<Wall> Walls { get; } = new();

    /// <summary>
    /// Currently selected wall being inspected and edited in the dialog.
    /// </summary>
    [ObservableProperty]
    private Wall? _selectedWall;

    /// <summary>
    /// Backwards compatibility accessor for the active wall.
    /// </summary>
    public Wall? TargetWall => SelectedWall;

    // Editable scalar properties for the selected wall
    [ObservableProperty] private string _wallName = string.Empty;
    [ObservableProperty] private double _length = 5000.0;
    [ObservableProperty] private double _selfWeight = 0.50;
    [ObservableProperty] private Story? _bottomStory;
    [ObservableProperty] private Story? _topStory;

    // Story and load assignment selections
    [ObservableProperty] private WallStory? _selectedWallStory;
    [ObservableProperty] private Load? _selectedAvailableLoad;
    [ObservableProperty] private Load? _selectedLeftLoad;
    [ObservableProperty] private Load? _selectedRightLoad;

    /// <summary>
    /// All available building levels/stories in the project.
    /// </summary>
    public ObservableCollection<Story> AvailableStories { get; } = new();

    /// <summary>
    /// Multi-story segments comprising the currently selected wall.
    /// </summary>
    public ObservableCollection<WallStory> WallStories { get; } = new();

    /// <summary>
    /// All defined project loads available for assignment to tributary zones.
    /// </summary>
    public ObservableCollection<Load> AvailableLoads { get; } = new();

    /// <summary>
    /// Specific loads applied to the left tributary zone of the selected story.
    /// </summary>
    public ObservableCollection<Load> CurrentStoryLoadsLeft { get; } = new();

    /// <summary>
    /// Specific loads applied to the right tributary zone of the selected story.
    /// </summary>
    public ObservableCollection<Load> CurrentStoryLoadsRight { get; } = new();

    /// <summary>
    /// Callback action to close the modal dialog.
    /// </summary>
    public Action? CloseAction { get; set; }

    /// <summary>
    /// Primary constructor supporting switching between all project walls.
    /// </summary>
    /// <param name="allWalls">Master list of walls from the project manager.</param>
    /// <param name="initialWall">Initial wall to select upon opening, or null for first wall.</param>
    /// <param name="allStories">Master catalog of stories in the project.</param>
    /// <param name="allLoads">Master catalog of load cases in the project.</param>
    public WallEditorViewModel(IList<Wall> allWalls, Wall? initialWall, IReadOnlyList<Story> allStories, IReadOnlyList<Load> allLoads)
    {
        _allWalls = allWalls;
        _allStories = allStories;
        _allLoads = allLoads;

        foreach (var s in _allStories) AvailableStories.Add(s);
        foreach (var l in _allLoads) AvailableLoads.Add(l);

        foreach (var w in _allWalls) Walls.Add(w);

        // Select initial wall or default to first
        SelectedWall = initialWall ?? Walls.FirstOrDefault();
    }

    /// <summary>
    /// Legacy constructor accepting a single wall, wrapping it into a collection.
    /// </summary>
    public WallEditorViewModel(Wall wall, IReadOnlyList<Story> allStories, IReadOnlyList<Load> allLoads)
        : this(new List<Wall> { wall }, wall, allStories, allLoads)
    {
    }

    /// <summary>
    /// Invoked immediately before SelectedWall changes.
    /// Commits user-entered edits to the outgoing wall so modifications are never lost when clicking another wall.
    /// </summary>
    partial void OnSelectedWallChanging(Wall? oldValue, Wall? newValue)
    {
        if (oldValue != null)
        {
            oldValue.Name = WallName;
            oldValue.Length = Length;
            oldValue.SelfWeight = SelfWeight;
        }
    }

    /// <summary>
    /// Invoked whenever the user selects a different wall from the left-hand selector list.
    /// Populates the dialog fields with the newly selected wall's dimensions, stories, and assigned loads.
    /// </summary>
    partial void OnSelectedWallChanged(Wall? value)
    {
        WallStories.Clear();
        CurrentStoryLoadsLeft.Clear();
        CurrentStoryLoadsRight.Clear();

        if (value == null)
        {
            WallName = string.Empty;
            Length = 5000.0;
            SelfWeight = 0.50;
            BottomStory = null;
            TopStory = null;
            SelectedWallStory = null;
            return;
        }

        WallName = value.Name;
        Length = value.Length;
        SelfWeight = value.SelfWeight;

        foreach (var ws in value.Stories)
        {
            WallStories.Add(ws);
        }

        if (WallStories.Count > 0)
        {
            BottomStory = AvailableStories.FirstOrDefault(s => s.Id == WallStories.Last().StoryId);
            TopStory = AvailableStories.FirstOrDefault(s => s.Id == WallStories.First().StoryId);
        }
        else
        {
            BottomStory = AvailableStories.LastOrDefault();
            TopStory = AvailableStories.FirstOrDefault();
        }

        SelectedWallStory = WallStories.FirstOrDefault();
    }

    /// <summary>
    /// Invoked when the user selects a story row in the tributary table or loads tab.
    /// Updates the Left and Right load assignment lists for the active story.
    /// </summary>
    partial void OnSelectedWallStoryChanged(WallStory? value)
    {
        CurrentStoryLoadsLeft.Clear();
        CurrentStoryLoadsRight.Clear();

        if (value == null) return;

        foreach (var l in value.LoadsLeft) CurrentStoryLoadsLeft.Add(l);
        foreach (var l in value.LoadsRight) CurrentStoryLoadsRight.Add(l);
    }

    /// <summary>
    /// Re-spans the wall across the selected vertical range of stories (from TopStory down to BottomStory).
    /// Preserves existing tributary widths and load assignments where the story ID matches.
    /// </summary>
    [RelayCommand]
    public void UpdateLevelSpan()
    {
        if (SelectedWall == null || BottomStory == null || TopStory == null) return;

        int topIdx = _allStories.ToList().IndexOf(TopStory);
        int botIdx = _allStories.ToList().IndexOf(BottomStory);

        if (topIdx < 0 || botIdx < 0) return;

        int start = Math.Min(topIdx, botIdx);
        int end = Math.Max(topIdx, botIdx);

        var spanStories = _allStories.Skip(start).Take(end - start + 1).ToList();

        // Preserve existing WallStory settings where possible
        var existingMap = SelectedWall.Stories.ToDictionary(ws => ws.StoryId);
        var newWallStories = new List<WallStory>();

        foreach (var s in spanStories)
        {
            if (existingMap.TryGetValue(s.Id, out var existing))
            {
                newWallStories.Add(existing);
            }
            else
            {
                newWallStories.Add(new WallStory
                {
                    WallId = SelectedWall.Id,
                    Wall = SelectedWall,
                    StoryId = s.Id,
                    Story = s,
                    TribWidthLeft = 1000.0,
                    TribWidthRight = 1500.0,
                    LuDepth = s.Height,
                    LuWidth = 152.0
                });
            }
        }

        SelectedWall.Stories = newWallStories;
        WallStories.Clear();
        foreach (var ws in SelectedWall.Stories) WallStories.Add(ws);
        SelectedWallStory = WallStories.FirstOrDefault();
    }

    /// <summary>
    /// Adds a selected project load to the left tributary zone of the active story.
    /// </summary>
    [RelayCommand]
    public void AddLoadLeft()
    {
        if (SelectedWallStory == null || SelectedAvailableLoad == null) return;
        if (!SelectedWallStory.LoadsLeft.Contains(SelectedAvailableLoad))
        {
            SelectedWallStory.LoadsLeft.Add(SelectedAvailableLoad);
            CurrentStoryLoadsLeft.Add(SelectedAvailableLoad);
        }
    }

    /// <summary>
    /// Removes the selected load from the left tributary zone of the active story.
    /// </summary>
    [RelayCommand]
    public void RemoveLoadLeft()
    {
        if (SelectedWallStory == null || SelectedLeftLoad == null) return;
        SelectedWallStory.LoadsLeft.Remove(SelectedLeftLoad);
        CurrentStoryLoadsLeft.Remove(SelectedLeftLoad);
    }

    /// <summary>
    /// Adds a selected project load to the right tributary zone of the active story.
    /// </summary>
    [RelayCommand]
    public void AddLoadRight()
    {
        if (SelectedWallStory == null || SelectedAvailableLoad == null) return;
        if (!SelectedWallStory.LoadsRight.Contains(SelectedAvailableLoad))
        {
            SelectedWallStory.LoadsRight.Add(SelectedAvailableLoad);
            CurrentStoryLoadsRight.Add(SelectedAvailableLoad);
        }
    }

    /// <summary>
    /// Removes the selected load from the right tributary zone of the active story.
    /// </summary>
    [RelayCommand]
    public void RemoveLoadRight()
    {
        if (SelectedWallStory == null || SelectedRightLoad == null) return;
        SelectedWallStory.LoadsRight.Remove(SelectedRightLoad);
        CurrentStoryLoadsRight.Remove(SelectedRightLoad);
    }

    /// <summary>
    /// Creates a new wall with default dimensions, spans across all stories,
    /// adds it to the project wall catalog, and selects it in the left list.
    /// </summary>
    [RelayCommand]
    public void NewWall()
    {
        // Commit current changes to the active wall
        if (SelectedWall != null)
        {
            SelectedWall.Name = WallName;
            SelectedWall.Length = Length;
            SelectedWall.SelfWeight = SelfWeight;
        }

        int nextId = _allWalls.Count > 0 ? _allWalls.Max(w => w.Id) + 1 : 1;
        var newWall = new Wall
        {
            Id = nextId,
            Name = $"Wall {nextId}",
            Length = 5000.0,
            SelfWeight = 0.50,
            PlanX = 1000.0 + (_allWalls.Count * 1200.0),
            PlanY = 2000.0
        };

        foreach (var story in _allStories)
        {
            newWall.Stories.Add(new WallStory
            {
                WallId = newWall.Id,
                Wall = newWall,
                StoryId = story.Id,
                Story = story,
                TribWidthLeft = 1000.0,
                TribWidthRight = 1500.0,
                LuDepth = story.Height,
                LuWidth = 152.0
            });
        }

        _allWalls.Add(newWall);
        Walls.Add(newWall);
        SelectedWall = newWall;
    }

    /// <summary>
    /// Explicitly commits all current field inputs (name, length, self-weight) to the active wall.
    /// </summary>
    [RelayCommand]
    public void SaveWall()
    {
        if (SelectedWall == null) return;
        SelectedWall.Name = WallName;
        SelectedWall.Length = Length;
        SelectedWall.SelfWeight = SelfWeight;
    }

    /// <summary>
    /// Deletes the currently selected wall from the project catalog.
    /// Ensures at least one wall remains in the building model.
    /// </summary>
    [RelayCommand]
    public void DeleteWall()
    {
        if (SelectedWall == null || Walls.Count <= 1) return;

        var toRemove = SelectedWall;
        _allWalls.Remove(toRemove);
        Walls.Remove(toRemove);
        SelectedWall = Walls.FirstOrDefault();
    }

    /// <summary>
    /// Commits all pending edits on the active wall and closes the dialog window.
    /// </summary>
    [RelayCommand]
    public void Close()
    {
        if (SelectedWall != null)
        {
            SelectedWall.Name = WallName;
            SelectedWall.Length = Length;
            SelectedWall.SelfWeight = SelfWeight;
        }
        CloseAction?.Invoke();
    }

    /// <summary>
    /// Backwards compatible command aliases.
    /// </summary>
    [RelayCommand]
    public void SaveAndClose() => Close();

    [RelayCommand]
    public void Cancel() => CloseAction?.Invoke();
}
