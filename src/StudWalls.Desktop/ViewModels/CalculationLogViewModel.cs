using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;

namespace StudWalls.Desktop.ViewModels;

/// <summary>
/// ViewModel coordinating the Calculation Log & Analysis Summary modal dialog.
/// 
/// Displays the complete CSA O86-20 calculation audit trail whenever an analysis run is executed:
/// 1. Top-down cumulative axial load accumulation (Dead, Live, Snow, Self-Weight).
/// 2. Factored load combinations per NBCC 2020.
/// 3. Stud cross-section properties, slenderness ratio Cc (Cl 6.5.6.2.2), and compressive resistance Pr (Cl 6.5.6.2.3).
/// 4. Demand-to-capacity (D/C) ratios and optimal member sizing summary.
/// </summary>
public partial class CalculationLogViewModel : ViewModelBase
{
    [ObservableProperty]
    private string _wallName = string.Empty;

    [ObservableProperty]
    private string _logContent = string.Empty;

    /// <summary>
    /// Action to close the dialog window.
    /// </summary>
    public Action? CloseAction { get; set; }

    /// <summary>
    /// Action to copy the calculation log text to the system clipboard.
    /// </summary>
    public Action<string>? CopyAction { get; set; }

    public CalculationLogViewModel(string wallName, string logContent)
    {
        _wallName = wallName;
        _logContent = logContent;
    }

    /// <summary>
    /// Copies the full plain-text calculation log to the operating system clipboard.
    /// </summary>
    [RelayCommand]
    public void CopyToClipboard()
    {
        CopyAction?.Invoke(LogContent);
    }

    /// <summary>
    /// Closes the modal dialog and returns to the main window workspace.
    /// </summary>
    [RelayCommand]
    public void Close()
    {
        CloseAction?.Invoke();
    }
}
