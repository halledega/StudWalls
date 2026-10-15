using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using StudWalls.Core.Enums;
using StudWalls.Core.Models;

namespace StudWalls.Desktop.ViewModels;

/// <summary>
/// ViewModel managing project specified load definitions (Dead, Live, Snow, etc.).
/// </summary>
public partial class LoadsViewModel : ViewModelBase
{
    private readonly List<Load> _sourceLoads;

    public ObservableCollection<Load> Loads { get; } = new();
    public ObservableCollection<LoadCase> AvailableCases { get; } = new();

    [ObservableProperty]
    private Load? _selectedLoad;

    [ObservableProperty] private string _editName = string.Empty;
    [ObservableProperty] private LoadCase _editCase = LoadCase.Dead;
    [ObservableProperty] private double _editValue = 1.0;
    [ObservableProperty] private LoadType _editType = LoadType.Area;

    public Action? CloseAction { get; set; }

    public LoadsViewModel(List<Load> loads)
    {
        _sourceLoads = loads;

        foreach (var c in Enum.GetValues<LoadCase>()) AvailableCases.Add(c);

        RefreshList();
        SelectedLoad = Loads.FirstOrDefault();
    }

    private void RefreshList()
    {
        Loads.Clear();
        foreach (var l in _sourceLoads) Loads.Add(l);
    }

    partial void OnSelectedLoadChanged(Load? value)
    {
        if (value == null) return;
        EditName = value.Name;
        EditCase = value.Case;
        EditValue = value.Value;
        EditType = value.LoadType;
    }

    [RelayCommand]
    public void AddLoad()
    {
        int nextId = _sourceLoads.Count > 0 ? _sourceLoads.Max(l => l.Id) + 1 : 1;
        var newLoad = new Load
        {
            Id = nextId,
            Name = $"New Load {nextId}",
            Case = LoadCase.Dead,
            Value = 1.0,
            LoadType = LoadType.Area
        };

        _sourceLoads.Add(newLoad);
        RefreshList();
        SelectedLoad = newLoad;
    }

    [RelayCommand]
    public void SaveLoad()
    {
        if (SelectedLoad == null || string.IsNullOrWhiteSpace(EditName)) return;

        SelectedLoad.Name = EditName;
        SelectedLoad.Case = EditCase;
        SelectedLoad.Value = EditValue;
        SelectedLoad.LoadType = EditType;

        RefreshList();
    }

    [RelayCommand]
    public void DeleteLoad()
    {
        if (SelectedLoad == null) return;
        _sourceLoads.Remove(SelectedLoad);
        RefreshList();
        SelectedLoad = Loads.FirstOrDefault();
    }

    [RelayCommand]
    public void Close() => CloseAction?.Invoke();
}
