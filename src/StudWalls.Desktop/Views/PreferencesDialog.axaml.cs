using Avalonia.Controls;
using StudWalls.Desktop.ViewModels;

namespace StudWalls.Desktop.Views;

/// <summary>
/// Code-behind for the Preferences configuration dialog.
/// Connects the ViewModel's CloseAction to the Window's Close() method.
/// </summary>
public partial class PreferencesDialog : Window
{
    public PreferencesDialog()
    {
        InitializeComponent();
        DataContextChanged += (_, _) =>
        {
            if (DataContext is PreferencesViewModel vm)
            {
                vm.CloseAction = Close;
            }
        };
    }
}
