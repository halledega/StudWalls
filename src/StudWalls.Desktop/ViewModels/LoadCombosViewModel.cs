using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using StudWalls.Core.Models;

namespace StudWalls.Desktop.ViewModels;

/// <summary>
/// ViewModel managing factored load combinations (NBCC ULS combinations) and item load factors.
/// </summary>
public partial class LoadCombosViewModel : ViewModelBase
{
    private readonly List<LoadCombination> _sourceCombos;
    private readonly List<Load> _availableLoads;

    public ObservableCollection<LoadCombination> Combinations { get; } = new();
    public ObservableCollection<LoadCombinationItem> Items { get; } = new();
    public ObservableCollection<Load> AvailableLoads { get; } = new();

    [ObservableProperty]
    private LoadCombination? _selectedCombo;

    [ObservableProperty]
    private LoadCombinationItem? _selectedItem;

    [ObservableProperty] private string _editName = string.Empty;
    [ObservableProperty] private Load? _selectedLoadForNewItem;
    [ObservableProperty] private double _newFactor = 1.0;

    public Action? CloseAction { get; set; }

    public LoadCombosViewModel(List<LoadCombination> combos, List<Load> loads)
    {
        _sourceCombos = combos;
        _availableLoads = loads;

        foreach (var l in _availableLoads) AvailableLoads.Add(l);
        SelectedLoadForNewItem = AvailableLoads.FirstOrDefault();

        RefreshCombos();
        SelectedCombo = Combinations.FirstOrDefault();
    }

    private void RefreshCombos()
    {
        Combinations.Clear();
        foreach (var c in _sourceCombos) Combinations.Add(c);
    }

    partial void OnSelectedComboChanged(LoadCombination? value)
    {
        Items.Clear();
        if (value == null)
        {
            EditName = string.Empty;
            return;
        }

        EditName = value.Name;
        foreach (var item in value.Items)
        {
            Items.Add(item);
        }
    }

    [RelayCommand]
    public void AddCombination()
    {
        int nextId = _sourceCombos.Count > 0 ? _sourceCombos.Max(c => c.Id) + 1 : 1;
        var newCombo = new LoadCombination
        {
            Id = nextId,
            Name = $"Combo {nextId}"
        };

        _sourceCombos.Add(newCombo);
        RefreshCombos();
        SelectedCombo = newCombo;
    }

    [RelayCommand]
    public void SaveCombinationName()
    {
        if (SelectedCombo == null || string.IsNullOrWhiteSpace(EditName)) return;
        SelectedCombo.Name = EditName;
        RefreshCombos();
    }

    [RelayCommand]
    public void DeleteCombination()
    {
        if (SelectedCombo == null) return;
        _sourceCombos.Remove(SelectedCombo);
        RefreshCombos();
        SelectedCombo = Combinations.FirstOrDefault();
    }

    [RelayCommand]
    public void AddItemToCombo()
    {
        if (SelectedCombo == null || SelectedLoadForNewItem == null) return;

        var newItem = new LoadCombinationItem
        {
            LoadCombinationId = SelectedCombo.Id,
            LoadCombination = SelectedCombo,
            LoadId = SelectedLoadForNewItem.Id,
            Load = SelectedLoadForNewItem,
            Factor = NewFactor
        };

        SelectedCombo.Items.Add(newItem);
        Items.Add(newItem);
    }

    [RelayCommand]
    public void RemoveItemFromCombo()
    {
        if (SelectedCombo == null || SelectedItem == null) return;

        SelectedCombo.Items.Remove(SelectedItem);
        Items.Remove(SelectedItem);
    }

    [RelayCommand]
    public void Close() => CloseAction?.Invoke();
}
