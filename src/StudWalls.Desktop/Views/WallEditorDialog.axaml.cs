using Avalonia.Controls;
using StudWalls.Desktop.ViewModels;

namespace StudWalls.Desktop.Views;

public partial class WallEditorDialog : Window
{
    public WallEditorDialog()
    {
        InitializeComponent();
        DataContextChanged += (_, _) =>
        {
            if (DataContext is WallEditorViewModel vm)
            {
                vm.CloseAction = Close;
            }
        };
    }
}
