using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using StudWalls.Core.Models;

namespace StudWalls.Desktop.ViewModels;

/// <summary>
/// ViewModel managing building levels/stories (elevations, clear heights, and floor thicknesses).
/// </summary>
public partial class LevelsViewModel : ViewModelBase
{
    private readonly List<Story> _sourceStories;
    private readonly List<Wall> _walls;

    public ObservableCollection<Story> Stories { get; } = new();

    [ObservableProperty]
    private Story? _selectedStory;

    [ObservableProperty] private string _editName = string.Empty;
    [ObservableProperty] private double _editHeight = 3000.0;
    [ObservableProperty] private double _editFloorThickness = 359.0;
    [ObservableProperty] private string _warningMessage = string.Empty;

    public Action? CloseAction { get; set; }

    public LevelsViewModel(List<Story> stories, List<Wall> walls)
    {
        _sourceStories = stories;
        _walls = walls;

        RefreshList();
        SelectedStory = Stories.FirstOrDefault();
    }

    private void RefreshList()
    {
        Stories.Clear();
        foreach (var s in _sourceStories) Stories.Add(s);
    }

    partial void OnSelectedStoryChanged(Story? value)
    {
        if (value == null) return;
        EditName = value.Name;
        EditHeight = value.Height;
        EditFloorThickness = value.FloorThickness;
        WarningMessage = string.Empty;
    }

    [RelayCommand]
    public void AddStory()
    {
        int nextId = _sourceStories.Count > 0 ? _sourceStories.Max(s => s.Id) + 1 : 1;
        var newStory = new Story
        {
            Id = nextId,
            Name = $"Story {nextId}",
            Height = 3000.0,
            FloorThickness = 359.0
        };

        _sourceStories.Add(newStory);
        RefreshList();
        SelectedStory = newStory;
    }

    [RelayCommand]
    public void SaveStory()
    {
        if (SelectedStory == null || string.IsNullOrWhiteSpace(EditName)) return;

        SelectedStory.Name = EditName;
        SelectedStory.Height = EditHeight;
        SelectedStory.FloorThickness = EditFloorThickness;

        RefreshList();
    }

    [RelayCommand]
    public void DeleteStory()
    {
        if (SelectedStory == null) return;

        // Prevent deletion if story is currently in use by any wall
        bool isUsed = _walls.Any(w => w.Stories.Any(ws => ws.StoryId == SelectedStory.Id));
        if (isUsed)
        {
            WarningMessage = $"Cannot delete '{SelectedStory.Name}' because it is in use by one or more walls.";
            return;
        }

        _sourceStories.Remove(SelectedStory);
        RefreshList();
        SelectedStory = Stories.FirstOrDefault();
    }

    [RelayCommand]
    public void Close() => CloseAction?.Invoke();
}
