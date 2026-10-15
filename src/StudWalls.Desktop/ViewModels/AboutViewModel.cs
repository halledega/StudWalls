using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;

namespace StudWalls.Desktop.ViewModels;

/// <summary>
/// ViewModel providing application metadata, standard references, and licensing.
/// </summary>
public partial class AboutViewModel : ViewModelBase
{
    public string AppTitle => "StudWalls - Wood Stud Wall Sizing Software";
    public string Version => "Version 2.0 (.NET 10 / Avalonia UI)";
    public string Standards => "Design Standards: CSA O86-20 (Engineering Design in Wood) & NBCC 2020";
    public string License => "Open Source: Free and permissively licensed for commercial software (MIT License)";
    public string Description => "StudWalls automates the structural analysis and sizing of multi-story wood light-frame stud walls. It accumulates roof and floor gravity loads, executes factored NBCC load combinations, checks strong- and weak-axis column buckling according to CSA O86, and determines the most economical stud size and spacing.";

    public Action? CloseAction { get; set; }

    [RelayCommand]
    public void Close() => CloseAction?.Invoke();
}
