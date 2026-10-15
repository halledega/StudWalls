using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using StudWalls.Core.Models;

namespace StudWalls.Desktop.ViewModels;

/// <summary>
/// ViewModel managing the catalog of stud sections, dimensional geometry, and material bindings.
/// Calculates gross area and moments of inertia in real time.
/// </summary>
public partial class StudsViewModel : ViewModelBase
{
    private readonly List<Stud> _sourceStuds;
    private readonly List<WoodMaterial> _materials;

    public ObservableCollection<Stud> DisplayStuds { get; } = new();
    public ObservableCollection<WoodMaterial> AvailableMaterials { get; } = new();

    [ObservableProperty]
    private Stud? _selectedStud;

    [ObservableProperty] private string _editName = string.Empty;
    [ObservableProperty] private double _editWidth = 38.1;
    [ObservableProperty] private double _editDepth = 139.7;
    [ObservableProperty] private int _editPlys = 1;
    [ObservableProperty] private WoodMaterial? _editMaterial;

    // Real-time calculated properties
    public double CalculatedAg => EditWidth * EditDepth * EditPlys;
    public double CalculatedIx => (EditWidth * EditPlys * Math.Pow(EditDepth, 3)) / 12.0;
    public double CalculatedIy => (EditDepth * Math.Pow(EditWidth * EditPlys, 3)) / 12.0;
    public double CalculatedSx => EditDepth > 0 ? CalculatedIx / (EditDepth / 2.0) : 0;
    public double CalculatedSy => (EditWidth * EditPlys) > 0 ? CalculatedIy / ((EditWidth * EditPlys) / 2.0) : 0;

    public Action? CloseAction { get; set; }

    public StudsViewModel(List<Stud> studs, List<WoodMaterial> materials)
    {
        _sourceStuds = studs;
        _materials = materials;

        foreach (var m in _materials) AvailableMaterials.Add(m);
        RefreshList();
        SelectedStud = DisplayStuds.FirstOrDefault();
    }

    private void RefreshList()
    {
        DisplayStuds.Clear();
        foreach (var s in _sourceStuds) DisplayStuds.Add(s);
    }

    partial void OnSelectedStudChanged(Stud? value)
    {
        if (value == null) return;
        EditName = value.Name;
        EditWidth = value.Section.Width;
        EditDepth = value.Section.Depth;
        EditPlys = value.Section.Plys;
        EditMaterial = AvailableMaterials.FirstOrDefault(m => m.Id == value.MaterialId) ?? AvailableMaterials.FirstOrDefault();
        NotifyCalculationsChanged();
    }

    partial void OnEditWidthChanged(double value) => NotifyCalculationsChanged();
    partial void OnEditDepthChanged(double value) => NotifyCalculationsChanged();
    partial void OnEditPlysChanged(int value) => NotifyCalculationsChanged();

    private void NotifyCalculationsChanged()
    {
        OnPropertyChanged(nameof(CalculatedAg));
        OnPropertyChanged(nameof(CalculatedIx));
        OnPropertyChanged(nameof(CalculatedIy));
        OnPropertyChanged(nameof(CalculatedSx));
        OnPropertyChanged(nameof(CalculatedSy));
    }

    [RelayCommand]
    public void NewStud()
    {
        SelectedStud = null;
        EditName = "2x6 SPF";
        EditWidth = 38.1;
        EditDepth = 139.7;
        EditPlys = 1;
        EditMaterial = AvailableMaterials.FirstOrDefault();
        NotifyCalculationsChanged();
    }

    [RelayCommand]
    public void SaveStud()
    {
        if (string.IsNullOrWhiteSpace(EditName) || EditMaterial == null) return;

        if (SelectedStud != null)
        {
            SelectedStud.Name = EditName;
            SelectedStud.Section.Width = EditWidth;
            SelectedStud.Section.Depth = EditDepth;
            SelectedStud.Section.Plys = EditPlys;
            SelectedStud.MaterialId = EditMaterial.Id;
            SelectedStud.Material = EditMaterial;
        }
        else
        {
            int nextId = _sourceStuds.Count > 0 ? _sourceStuds.Max(s => s.Id) + 1 : 1;
            var created = new Stud
            {
                Id = nextId,
                Name = EditName,
                SectionId = nextId,
                Section = new Section { Id = nextId, Width = EditWidth, Depth = EditDepth, Plys = EditPlys },
                MaterialId = EditMaterial.Id,
                Material = EditMaterial
            };
            _sourceStuds.Add(created);
            RefreshList();
            SelectedStud = created;
        }
    }

    [RelayCommand]
    public void DeleteStud()
    {
        if (SelectedStud == null) return;
        _sourceStuds.Remove(SelectedStud);
        RefreshList();
        SelectedStud = DisplayStuds.FirstOrDefault();
    }

    [RelayCommand]
    public void Close() => CloseAction?.Invoke();
}
