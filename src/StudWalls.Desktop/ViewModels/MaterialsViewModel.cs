using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using StudWalls.Core.Models;

namespace StudWalls.Desktop.ViewModels;

/// <summary>
/// ViewModel managing the catalog of wood lumber materials and their specified design strengths.
/// </summary>
public partial class MaterialsViewModel : ViewModelBase
{
    private readonly List<WoodMaterial> _sourceList;

    public ObservableCollection<WoodMaterial> DisplayMaterials { get; } = new();
    public ObservableCollection<string> Categories { get; } = new();
    public ObservableCollection<string> SpeciesList { get; } = new();

    [ObservableProperty]
    private string _selectedCategoryFilter = "All";

    [ObservableProperty]
    private string _selectedSpeciesFilter = "All";

    [ObservableProperty]
    private bool _filterCategoryEnabled;

    [ObservableProperty]
    private bool _filterSpeciesEnabled;

    [ObservableProperty]
    private WoodMaterial? _selectedMaterial;

    // Editable properties for currently selected or new material
    [ObservableProperty] private string _editName = string.Empty;
    [ObservableProperty] private string _editCategory = "Joist and Plank";
    [ObservableProperty] private string _editSpecies = "Spruce-Pine-Fir";
    [ObservableProperty] private string _editGrade = "No1/No2";
    [ObservableProperty] private string _editMaterialType = "Sawn";
    [ObservableProperty] private double _editFb = 11.8;
    [ObservableProperty] private double _editFv = 1.5;
    [ObservableProperty] private double _editFc = 11.5;
    [ObservableProperty] private double _editFcp = 5.3;
    [ObservableProperty] private double _editFt = 5.5;
    [ObservableProperty] private double _editE = 9500.0;
    [ObservableProperty] private double _editE05 = 6500.0;

    public Action? CloseAction { get; set; }

    public MaterialsViewModel(List<WoodMaterial> materials)
    {
        _sourceList = materials;

        Categories.Add("All");
        foreach (var c in _sourceList.Select(m => m.Category).Distinct().OrderBy(c => c)) Categories.Add(c);

        SpeciesList.Add("All");
        foreach (var s in _sourceList.Select(m => m.Species).Distinct().OrderBy(s => s)) SpeciesList.Add(s);

        ApplyFilter();
        SelectedMaterial = DisplayMaterials.FirstOrDefault();
    }

    partial void OnSelectedCategoryFilterChanged(string value) => ApplyFilter();
    partial void OnSelectedSpeciesFilterChanged(string value) => ApplyFilter();
    partial void OnFilterCategoryEnabledChanged(bool value) => ApplyFilter();
    partial void OnFilterSpeciesEnabledChanged(bool value) => ApplyFilter();

    private void ApplyFilter()
    {
        DisplayMaterials.Clear();
        var query = _sourceList.AsEnumerable();

        if (FilterCategoryEnabled && SelectedCategoryFilter != "All")
            query = query.Where(m => m.Category == SelectedCategoryFilter);

        if (FilterSpeciesEnabled && SelectedSpeciesFilter != "All")
            query = query.Where(m => m.Species == SelectedSpeciesFilter);

        foreach (var m in query.OrderBy(m => m.Name))
        {
            DisplayMaterials.Add(m);
        }
    }

    partial void OnSelectedMaterialChanged(WoodMaterial? value)
    {
        if (value == null) return;
        EditName = value.Name;
        EditCategory = value.Category;
        EditSpecies = value.Species;
        EditGrade = value.Grade;
        EditMaterialType = value.MaterialType;
        EditFb = value.Fb;
        EditFv = value.Fv;
        EditFc = value.Fc;
        EditFcp = value.Fcp;
        EditFt = value.Ft;
        EditE = value.E;
        EditE05 = value.E05;
    }

    [RelayCommand]
    public void NewMaterial()
    {
        SelectedMaterial = null;
        EditName = "New Material";
        EditCategory = "Joist and Plank";
        EditSpecies = "SPF";
        EditGrade = "No1/No2";
        EditMaterialType = "Sawn";
        EditFb = 11.5;
        EditFv = 1.5;
        EditFc = 11.5;
        EditFcp = 5.0;
        EditFt = 5.0;
        EditE = 9500;
        EditE05 = 6500;
    }

    [RelayCommand]
    public void SaveMaterial()
    {
        if (string.IsNullOrWhiteSpace(EditName)) return;

        if (SelectedMaterial != null)
        {
            SelectedMaterial.Name = EditName;
            SelectedMaterial.Category = EditCategory;
            SelectedMaterial.Species = EditSpecies;
            SelectedMaterial.Grade = EditGrade;
            SelectedMaterial.MaterialType = EditMaterialType;
            SelectedMaterial.Fb = EditFb;
            SelectedMaterial.Fv = EditFv;
            SelectedMaterial.Fc = EditFc;
            SelectedMaterial.Fcp = EditFcp;
            SelectedMaterial.Ft = EditFt;
            SelectedMaterial.E = EditE;
            SelectedMaterial.E05 = EditE05;
        }
        else
        {
            int nextId = _sourceList.Count > 0 ? _sourceList.Max(m => m.Id) + 1 : 1;
            var created = new WoodMaterial
            {
                Id = nextId,
                Name = EditName,
                Category = EditCategory,
                Species = EditSpecies,
                Grade = EditGrade,
                MaterialType = EditMaterialType,
                Fb = EditFb,
                Fv = EditFv,
                Fc = EditFc,
                Fcp = EditFcp,
                Ft = EditFt,
                E = EditE,
                E05 = EditE05
            };
            _sourceList.Add(created);
            ApplyFilter();
            SelectedMaterial = created;
        }
    }

    [RelayCommand]
    public void DeleteMaterial()
    {
        if (SelectedMaterial == null) return;
        _sourceList.Remove(SelectedMaterial);
        ApplyFilter();
        SelectedMaterial = DisplayMaterials.FirstOrDefault();
    }

    [RelayCommand]
    public void Close() => CloseAction?.Invoke();
}
