using Avalonia.Controls;
using StudWalls.Desktop.ViewModels;

namespace StudWalls.Desktop.Views;

public partial class AboutDialog : Window
{
    public AboutDialog()
    {
        InitializeComponent();
        DataContextChanged += (_, _) =>
        {
            if (DataContext is AboutViewModel vm)
            {
                vm.CloseAction = Close;
            }
        };
    }
}
