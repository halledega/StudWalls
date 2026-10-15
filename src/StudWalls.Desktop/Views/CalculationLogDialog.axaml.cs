using Avalonia.Controls;
using Avalonia.Input.Platform;
using StudWalls.Desktop.ViewModels;

namespace StudWalls.Desktop.Views;

public partial class CalculationLogDialog : Window
{
    public CalculationLogDialog()
    {
        InitializeComponent();
        DataContextChanged += OnDataContextChanged;
    }

    private void OnDataContextChanged(object? sender, EventArgs e)
    {
        if (DataContext is CalculationLogViewModel vm)
        {
            vm.CloseAction = Close;
            vm.CopyAction = async text =>
            {
                if (Clipboard != null)
                {
                    await Clipboard.SetTextAsync(text);
                }
            };
        }
    }
}
