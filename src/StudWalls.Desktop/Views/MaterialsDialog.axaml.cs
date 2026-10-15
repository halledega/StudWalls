using Avalonia.Controls;
using StudWalls.Desktop.ViewModels;

namespace StudWalls.Desktop.Views;

public partial class MaterialsDialog : Window
{
    public MaterialsDialog()
    {
        InitializeComponent();
        DataContextChanged += (_, _) =>
        {
            if (DataContext is MaterialsViewModel vm)
            {
                vm.CloseAction = Close;
            }
        };
    }
}
