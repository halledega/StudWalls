using Avalonia.Controls;
using StudWalls.Desktop.ViewModels;

namespace StudWalls.Desktop.Views;

public partial class LoadCombosDialog : Window
{
    public LoadCombosDialog()
    {
        InitializeComponent();
        DataContextChanged += (_, _) =>
        {
            if (DataContext is LoadCombosViewModel vm)
            {
                vm.CloseAction = Close;
            }
        };
    }
}
