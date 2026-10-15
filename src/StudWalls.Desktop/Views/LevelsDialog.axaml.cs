using Avalonia.Controls;
using StudWalls.Desktop.ViewModels;

namespace StudWalls.Desktop.Views;

public partial class LevelsDialog : Window
{
    public LevelsDialog()
    {
        InitializeComponent();
        DataContextChanged += (_, _) =>
        {
            if (DataContext is LevelsViewModel vm)
            {
                vm.CloseAction = Close;
            }
        };
    }
}
