using Avalonia.Controls;
using StudWalls.Desktop.ViewModels;

namespace StudWalls.Desktop.Views;

public partial class LoadsDialog : Window
{
    public LoadsDialog()
    {
        InitializeComponent();
        DataContextChanged += (_, _) =>
        {
            if (DataContext is LoadsViewModel vm)
            {
                vm.CloseAction = Close;
            }
        };
    }
}
