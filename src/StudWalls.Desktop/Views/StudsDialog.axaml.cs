using Avalonia.Controls;
using StudWalls.Desktop.ViewModels;

namespace StudWalls.Desktop.Views;

public partial class StudsDialog : Window
{
    public StudsDialog()
    {
        InitializeComponent();
        DataContextChanged += (_, _) =>
        {
            if (DataContext is StudsViewModel vm)
            {
                vm.CloseAction = Close;
            }
        };
    }
}
