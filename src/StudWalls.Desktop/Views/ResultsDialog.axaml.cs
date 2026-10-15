using Avalonia.Controls;
using StudWalls.Desktop.ViewModels;

namespace StudWalls.Desktop.Views;

public partial class ResultsDialog : Window
{
    public ResultsDialog()
    {
        InitializeComponent();
        DataContextChanged += (_, _) =>
        {
            if (DataContext is ResultsViewModel vm)
            {
                vm.CloseAction = Close;
            }
        };
    }
}
