using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using StudWalls.Core.Models;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;

namespace StudWalls.Desktop.ViewModels;

/// <summary>
/// Generic selectable item model with Observable IsSelected state for check lists.
/// </summary>
public partial class SelectableOption<T> : ObservableObject
{
    public T Value { get; set; }
    public string DisplayName { get; set; } = string.Empty;

    [ObservableProperty]
    private bool _isSelected;

    public SelectableOption(T value, string displayName, bool isSelected = false)
    {
        Value = value;
        DisplayName = displayName;
        _isSelected = isSelected;
    }

    public override string ToString() => DisplayName;
}

/// <summary>
/// ViewModel managing the Sizing Criteria dialog presented when clicking "Run Sizing".
/// Allows the engineer to constrain the search space to desired sections, spacings,
/// materials, and built-up plys before running CSA O86-20 calculations.
/// </summary>
public partial class SizingCriteriaViewModel : ViewModelBase
{
    private readonly SizingCriteria _criteria;
    private readonly Action<SizingCriteria>? _onRunConfirmed;

    [ObservableProperty]
    private string _title = "Sizing Criteria & Design Options";

    [ObservableProperty]
    private string _wallSummaryText = string.Empty;

    [ObservableProperty]
    private double _maxTargetDcRatio = 1.00;

    public ObservableCollection<SelectableOption<string>> SectionOptions { get; } = new();
    public ObservableCollection<SelectableOption<double>> SpacingOptions { get; } = new();
    public ObservableCollection<SelectableOption<int>> PlyOptions { get; } = new();
    public ObservableCollection<SelectableOption<int>> MaterialOptions { get; } = new();

    public Action? CloseAction { get; set; }

    public SizingCriteriaViewModel(
        Wall wall,
        SizingCriteria criteria,
        IEnumerable<WoodMaterial> availableMaterials,
        Action<SizingCriteria>? onRunConfirmed = null)
    {
        _criteria = criteria;
        _onRunConfirmed = onRunConfirmed;

        Title = $"Sizing Criteria & Design Options - {wall.Name}";
        WallSummaryText = $"Active Wall: {wall.Name} (Length: {wall.Length / 1000.0:F2} m, Height: {wall.TotalHeight / 1000.0:F2} m, {wall.Stories.Count} stories)";
        MaxTargetDcRatio = criteria.MaxTargetDcRatio > 0 ? criteria.MaxTargetDcRatio : 1.00;

        // 1. Nominal lumber section choices
        var standardSections = new[]
        {
            ("2x4", "2x4 (38 x 89 mm)"),
            ("2x6", "2x6 (38 x 140 mm)"),
            ("2x8", "2x8 (38 x 184 mm)"),
            ("2x10", "2x10 (38 x 235 mm)")
        };

        foreach (var (code, label) in standardSections)
        {
            bool selected = criteria.AllowedSections.Contains(code);
            SectionOptions.Add(new SelectableOption<string>(code, label, selected));
        }

        // Default to 2x4 and 2x6 if none selected
        if (!SectionOptions.Any(o => o.IsSelected))
        {
            var opt2x4 = SectionOptions.FirstOrDefault(o => o.Value == "2x4");
            if (opt2x4 != null) opt2x4.IsSelected = true;
            var opt2x6 = SectionOptions.FirstOrDefault(o => o.Value == "2x6");
            if (opt2x6 != null) opt2x6.IsSelected = true;
        }

        // 2. Center-to-center spacing choices
        var standardSpacings = new[]
        {
            (609.6, "24\" o/c (610 mm)"),
            (406.4, "16\" o/c (406 mm)"),
            (304.8, "12\" o/c (305 mm)"),
            (203.2, "8\" o/c (203 mm)")
        };

        foreach (var (spc, label) in standardSpacings)
        {
            bool selected = criteria.AllowedSpacings.Any(s => Math.Abs(s - spc) < 5.0);
            SpacingOptions.Add(new SelectableOption<double>(spc, label, selected));
        }

        // Default to 16" and 12" if none selected
        if (!SpacingOptions.Any(o => o.IsSelected))
        {
            var opt16 = SpacingOptions.FirstOrDefault(o => Math.Abs(o.Value - 406.4) < 5.0);
            if (opt16 != null) opt16.IsSelected = true;
            var opt12 = SpacingOptions.FirstOrDefault(o => Math.Abs(o.Value - 304.8) < 5.0);
            if (opt12 != null) opt12.IsSelected = true;
        }

        // 3. Built-up member plys
        var standardPlys = new[]
        {
            (1, "1-Ply (Single Stud)"),
            (2, "2-Ply (Double Stud)"),
            (3, "3-Ply (Triple Stud)")
        };

        foreach (var (ply, label) in standardPlys)
        {
            bool selected = criteria.AllowedPlys.Contains(ply);
            PlyOptions.Add(new SelectableOption<int>(ply, label, selected));
        }

        if (!PlyOptions.Any(o => o.IsSelected))
        {
            var p1 = PlyOptions.FirstOrDefault(o => o.Value == 1);
            if (p1 != null) p1.IsSelected = true;
            var p2 = PlyOptions.FirstOrDefault(o => o.Value == 2);
            if (p2 != null) p2.IsSelected = true;
        }

        // 4. Available Wood Materials
        foreach (var mat in availableMaterials)
        {
            bool selected = criteria.AllowedMaterialIds.Count == 0 || criteria.AllowedMaterialIds.Contains(mat.Id);
            MaterialOptions.Add(new SelectableOption<int>(mat.Id, mat.Name, selected));
        }

        if (!MaterialOptions.Any(o => o.IsSelected) && MaterialOptions.Count > 0)
        {
            MaterialOptions.First().IsSelected = true;
        }
    }

    [RelayCommand]
    public void RunSizing()
    {
        // Harvest selected options
        var selectedSections = SectionOptions.Where(o => o.IsSelected).Select(o => o.Value).ToList();
        var selectedSpacings = SpacingOptions.Where(o => o.IsSelected).Select(o => o.Value).ToList();
        var selectedPlys = PlyOptions.Where(o => o.IsSelected).Select(o => o.Value).ToList();
        var selectedMaterials = MaterialOptions.Where(o => o.IsSelected).Select(o => o.Value).ToList();

        // Enforce safe fallbacks if user unchecked everything in a category
        if (selectedSections.Count == 0) selectedSections.AddRange(new[] { "2x4", "2x6" });
        if (selectedSpacings.Count == 0) selectedSpacings.AddRange(new[] { 406.4, 304.8 });
        if (selectedPlys.Count == 0) selectedPlys.AddRange(new[] { 1, 2 });

        _criteria.AllowedSections = selectedSections;
        _criteria.AllowedSpacings = selectedSpacings;
        _criteria.AllowedPlys = selectedPlys;
        _criteria.AllowedMaterialIds = selectedMaterials;
        _criteria.MaxTargetDcRatio = MaxTargetDcRatio;

        CloseAction?.Invoke();
        _onRunConfirmed?.Invoke(_criteria);
    }

    [RelayCommand]
    public void Cancel()
    {
        CloseAction?.Invoke();
    }
}
