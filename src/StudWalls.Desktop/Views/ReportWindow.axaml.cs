using Avalonia.Controls;
using Avalonia.Platform.Storage;
using StudWalls.Desktop.ViewModels;

namespace StudWalls.Desktop.Views;

public partial class ReportWindow : Window
{
    public ReportWindow()
    {
        InitializeComponent();
        DataContextChanged += (_, _) =>
        {
            if (DataContext is ReportViewModel vm)
            {
                vm.CloseAction = Close;
                vm.RequestSavePdfPath = RequestSavePdfPathAsync;
            }
        };
    }

    private async Task<string?> RequestSavePdfPathAsync(string title)
    {
        var topLevel = GetTopLevel(this);
        if (topLevel == null) return null;

        var file = await topLevel.StorageProvider.SaveFilePickerAsync(new FilePickerSaveOptions
        {
            Title = title,
            DefaultExtension = "pdf",
            ShowOverwritePrompt = true
        });

        return file?.Path.LocalPath;
    }
}
