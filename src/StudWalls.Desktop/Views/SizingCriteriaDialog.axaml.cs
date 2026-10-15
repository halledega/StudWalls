using Avalonia.Controls;
using StudWalls.Desktop.ViewModels;

namespace StudWalls.Desktop.Views;

public partial class SizingCriteriaDialog : Window
{
    public SizingCriteriaDialog()
    {
        InitializeComponent();
        DataContextChanged += (_, _) =>
        {
            if (DataContext is SizingCriteriaViewModel vm)
            {
                vm.CloseAction = Close;
            }
        };
    }
}
