using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using StudWalls.Core.Models;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;

namespace StudWalls.Desktop.ViewModels;

/// <summary>
/// Option model for the Level filtering ComboBox in the ResultsDialog.
/// Allows viewing all stories simultaneously or focusing on a specific story.
/// </summary>
public class StoryFilterOption
{
    public int? StoryId { get; set; }
    public string DisplayName { get; set; } = string.Empty;

    public override string ToString() => DisplayName;
}

/// <summary>
/// ViewModel managing the standalone Engineering Results dialog.
/// Provides per-level filtering, passing-only filtering, final member specification,
/// and direct access to report generation.
/// </summary>
public partial class ResultsViewModel : ViewModelBase
{
    private readonly Wall _wall;
    private readonly Action? _generateReportAction;
    private readonly Action? _onFinalizedAction;
    private readonly Action? _openSizingCriteriaAction;

    [ObservableProperty]
    private string _title = "Engineering Results";

    [ObservableProperty]
    private string _resultsSummaryText = string.Empty;

    [ObservableProperty]
    private StoryFilterOption? _selectedLevelFilter;

    [ObservableProperty]
    private bool _showPassingOnly = true;

    [ObservableProperty]
    private DesignResult? _selectedResult;

    public ObservableCollection<StoryFilterOption> LevelFilterOptions { get; } = new();

    public ObservableCollection<DesignResult> FilteredResults { get; } = new();

    public Action? CloseAction { get; set; }

    public ResultsViewModel(
        Wall wall,
        IEnumerable<Story> stories,
        Action? generateReportAction = null,
        Action? onFinalizedAction = null,
        Action? openSizingCriteriaAction = null)
    {
        _wall = wall;
        _generateReportAction = generateReportAction;
        _onFinalizedAction = onFinalizedAction;
        _openSizingCriteriaAction = openSizingCriteriaAction;

        Title = $"Engineering Sizing Results - {_wall.Name}";

        // Populate Level filter options: "All Levels" + each story present on the wall
        LevelFilterOptions.Add(new StoryFilterOption { StoryId = null, DisplayName = "All Levels" });

        foreach (var ws in _wall.Stories)
        {
            var storyName = ws.Story?.Name ?? $"Level {ws.StoryId}";
            LevelFilterOptions.Add(new StoryFilterOption { StoryId = ws.StoryId, DisplayName = storyName });
        }

        _selectedLevelFilter = LevelFilterOptions.FirstOrDefault();

        ApplyFilter();
    }

    partial void OnSelectedLevelFilterChanged(StoryFilterOption? value)
    {
        ApplyFilter();
    }

    partial void OnShowPassingOnlyChanged(bool value)
    {
        ApplyFilter();
    }

    private void ApplyFilter()
    {
        FilteredResults.Clear();

        int totalEvaluated = 0;
        int totalPassing = 0;

        foreach (var ws in _wall.Stories)
        {
            // If a specific level is selected, skip other levels
            if (SelectedLevelFilter?.StoryId != null && ws.StoryId != SelectedLevelFilter.StoryId)
            {
                continue;
            }

            foreach (var r in ws.Results)
            {
                totalEvaluated++;
                if (r.DcRatio <= 1.0001)
                {
                    totalPassing++;
                }

                // Apply passing filter
                if (ShowPassingOnly && r.DcRatio > 1.0001)
                {
                    continue;
                }

                FilteredResults.Add(r);
            }
        }

        // Sort by Story ID, then by WoodVolume ascending (most economical first)
        var sorted = FilteredResults
            .OrderBy(r => r.WallStoryId)
            .ThenBy(r => r.WoodVolume)
            .ToList();

        FilteredResults.Clear();
        foreach (var r in sorted)
        {
            FilteredResults.Add(r);
        }

        SelectedResult = FilteredResults.FirstOrDefault(r => r.IsFinal) ?? FilteredResults.FirstOrDefault();

        string levelContext = SelectedLevelFilter?.StoryId == null
            ? "all levels"
            : SelectedLevelFilter.DisplayName;

        ResultsSummaryText = $"Wall: {_wall.Name} ({levelContext}) | {FilteredResults.Count} options displayed ({totalPassing} passing of {totalEvaluated} evaluated)";
    }

    [RelayCommand]
    public void FinalizeResults()
    {
        _onFinalizedAction?.Invoke();
        CloseAction?.Invoke();
    }

    [RelayCommand]
    public void GenerateReport()
    {
        _generateReportAction?.Invoke();
    }

    [RelayCommand]
    public void OpenSizingCriteria()
    {
        _openSizingCriteriaAction?.Invoke();
    }

    public void RefreshData()
    {
        ApplyFilter();
    }

    [RelayCommand]
    public void Close()
    {
        CloseAction?.Invoke();
    }
}
