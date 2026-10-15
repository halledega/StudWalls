using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using StudWalls.Core.Enums;
using StudWalls.Core.Models;

namespace StudWalls.Desktop.ViewModels;

/// <summary>
/// ViewModel coordinating the application preferences dialog.
/// 
/// Allows structural engineers to configure global application defaults:
/// 1. Measurement unit system (Metric vs Imperial) per national design standards.
/// 2. CSA O86 design constraint thresholds (maximum slenderness ratio Cc = 50 per Cl 6.5.6.2.2).
/// 3. Maximum allowable demand-to-capacity (D/C) ratio target.
/// 4. Default story height, wall self-weight, and stud spacing for newly created wall sections.
/// 5. Title block defaults (engineer of record and consulting firm name).
/// </summary>
public partial class PreferencesViewModel : ViewModelBase
{
    private readonly AppPreferences _preferences;

    [ObservableProperty]
    private UnitSystem _selectedUnitSystem;

    [ObservableProperty]
    private string _defaultEngineer;

    [ObservableProperty]
    private string _defaultCompany;

    [ObservableProperty]
    private double _defaultStoryHeight;

    [ObservableProperty]
    private double _defaultWallSelfWeight;

    [ObservableProperty]
    private double _defaultStudSpacing;

    [ObservableProperty]
    private double _maxAllowableCc;

    [ObservableProperty]
    private double _maxTargetDcRatio;

    [ObservableProperty]
    private string _selectedMaterialName;

    [ObservableProperty]
    private double _defaultServiceConditionFactor;

    /// <summary>
    /// Available measurement systems for selection.
    /// </summary>
    public ObservableCollection<UnitSystem> AvailableUnitSystems { get; } = new()
    {
        UnitSystem.Metric,
        UnitSystem.Imperial
    };

    /// <summary>
    /// Available lumber materials in the project library.
    /// </summary>
    public ObservableCollection<string> AvailableMaterials { get; } = new();

    /// <summary>
    /// Callback action to close the dialog window.
    /// </summary>
    public Action? CloseAction { get; set; }

    /// <summary>
    /// Initializes a new instance of the PreferencesViewModel with active preferences and materials.
    /// </summary>
    /// <param name="preferences">The active project preferences instance.</param>
    /// <param name="materials">The library of wood materials available in the project.</param>
    public PreferencesViewModel(AppPreferences preferences, IEnumerable<WoodMaterial> materials)
    {
        _preferences = preferences;

        // Initialize editable fields with current preferences
        _selectedUnitSystem = preferences.UnitSystem;
        _defaultEngineer = preferences.DefaultEngineer;
        _defaultCompany = preferences.DefaultCompany;
        _defaultStoryHeight = preferences.DefaultStoryHeight;
        _defaultWallSelfWeight = preferences.DefaultWallSelfWeight;
        _defaultStudSpacing = preferences.DefaultStudSpacing;
        _maxAllowableCc = preferences.MaxAllowableCc;
        _maxTargetDcRatio = preferences.MaxTargetDcRatio;
        _selectedMaterialName = preferences.DefaultMaterialName;
        _defaultServiceConditionFactor = preferences.DefaultServiceConditionFactor;

        foreach (var mat in materials)
        {
            AvailableMaterials.Add(mat.Name);
        }

        if (string.IsNullOrWhiteSpace(_selectedMaterialName) && AvailableMaterials.Count > 0)
        {
            _selectedMaterialName = AvailableMaterials[0];
        }
    }

    /// <summary>
    /// Saves all changes back to the underlying AppPreferences instance and closes the dialog.
    /// </summary>
    [RelayCommand]
    public void Save()
    {
        _preferences.UnitSystem = SelectedUnitSystem;
        _preferences.DefaultEngineer = DefaultEngineer;
        _preferences.DefaultCompany = DefaultCompany;
        _preferences.DefaultStoryHeight = DefaultStoryHeight;
        _preferences.DefaultWallSelfWeight = DefaultWallSelfWeight;
        _preferences.DefaultStudSpacing = DefaultStudSpacing;
        _preferences.MaxAllowableCc = MaxAllowableCc;
        _preferences.MaxTargetDcRatio = MaxTargetDcRatio;
        _preferences.DefaultMaterialName = SelectedMaterialName;
        _preferences.DefaultServiceConditionFactor = DefaultServiceConditionFactor;

        CloseAction?.Invoke();
    }

    /// <summary>
    /// Cancels changes and closes the dialog without saving.
    /// </summary>
    [RelayCommand]
    public void Cancel()
    {
        CloseAction?.Invoke();
    }
}
