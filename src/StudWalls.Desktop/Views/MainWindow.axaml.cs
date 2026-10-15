using Avalonia;
using Avalonia.Controls;
using Avalonia.Input;
using Avalonia.Interactivity;
using Avalonia.Platform.Storage;
using Avalonia.VisualTree;
using StudWalls.Core.Models;
using StudWalls.Desktop.ViewModels;

namespace StudWalls.Desktop.Views;

public partial class MainWindow : Window
{
    public MainWindow()
    {
        InitializeComponent();
        DataContextChanged += OnDataContextChanged;
    }

    private void OnDataContextChanged(object? sender, EventArgs e)
    {
        if (DataContext is MainViewModel vm)
        {
            vm.ShowMaterialsDialogRequested = ShowMaterialsDialog;
            vm.ShowStudsDialogRequested = ShowStudsDialog;
            vm.ShowLevelsDialogRequested = ShowLevelsDialog;
            vm.ShowLoadsDialogRequested = ShowLoadsDialog;
            vm.ShowLoadCombosDialogRequested = ShowLoadCombosDialog;
            vm.ShowWallEditorRequested = ShowWallEditorDialog;
            vm.ShowAboutDialogRequested = ShowAboutDialog;
            vm.ShowPreferencesDialogRequested = ShowPreferencesDialog;
            vm.ShowCalculationLogRequested = ShowCalculationLogDialog;
            vm.ShowSizingCriteriaDialogRequested = ShowSizingCriteriaDialog;
            vm.ShowResultsDialogRequested = ShowResultsDialog;
            vm.ShowReportRequested = ShowReportWindow;
            vm.RequestSaveFilePath = RequestSaveFilePathAsync;
            vm.RequestOpenFilePath = RequestOpenFilePathAsync;
        }
    }

    private async Task<string?> RequestSaveFilePathAsync(string title)
    {
        var topLevel = GetTopLevel(this);
        if (topLevel == null) return null;

        var file = await topLevel.StorageProvider.SaveFilePickerAsync(new FilePickerSaveOptions
        {
            Title = title,
            DefaultExtension = "swproj",
            ShowOverwritePrompt = true
        });

        return file?.Path.LocalPath;
    }

    private async Task<string?> RequestOpenFilePathAsync(string title)
    {
        var topLevel = GetTopLevel(this);
        if (topLevel == null) return null;

        var files = await topLevel.StorageProvider.OpenFilePickerAsync(new FilePickerOpenOptions
        {
            Title = title,
            AllowMultiple = false
        });

        return files.Count > 0 ? files[0].Path.LocalPath : null;
    }

    private async void ShowMaterialsDialog()
    {
        if (DataContext is not MainViewModel vm) return;
        var dialog = new MaterialsDialog
        {
            DataContext = new MaterialsViewModel(vm.ProjectManager.Materials)
        };
        await dialog.ShowDialog(this);
        vm.RefreshProjectData();
    }

    private async void ShowStudsDialog()
    {
        if (DataContext is not MainViewModel vm) return;
        var dialog = new StudsDialog
        {
            DataContext = new StudsViewModel(vm.ProjectManager.Studs, vm.ProjectManager.Materials)
        };
        await dialog.ShowDialog(this);
        vm.RefreshProjectData();
    }

    private async void ShowLevelsDialog()
    {
        if (DataContext is not MainViewModel vm) return;
        var dialog = new LevelsDialog
        {
            DataContext = new LevelsViewModel(vm.ProjectManager.Stories, vm.ProjectManager.Walls)
        };
        await dialog.ShowDialog(this);
        vm.RefreshProjectData();
    }

    private async void ShowLoadsDialog()
    {
        if (DataContext is not MainViewModel vm) return;
        var dialog = new LoadsDialog
        {
            DataContext = new LoadsViewModel(vm.ProjectManager.Loads)
        };
        await dialog.ShowDialog(this);
        vm.RefreshProjectData();
    }

    private async void ShowLoadCombosDialog()
    {
        if (DataContext is not MainViewModel vm) return;
        var dialog = new LoadCombosDialog
        {
            DataContext = new LoadCombosViewModel(vm.ProjectManager.LoadCombinations, vm.ProjectManager.Loads)
        };
        await dialog.ShowDialog(this);
        vm.RefreshProjectData();
    }

    private async void ShowWallEditorDialog()
    {
        if (DataContext is not MainViewModel vm) return;
        var editorVm = new WallEditorViewModel(
            vm.ProjectManager.Walls,
            vm.SelectedWall,
            vm.ProjectManager.Stories,
            vm.ProjectManager.Loads);

        var dialog = new WallEditorDialog
        {
            DataContext = editorVm
        };
        await dialog.ShowDialog(this);

        if (editorVm.SelectedWall != null)
        {
            vm.SelectedWall = vm.ProjectManager.Walls.FirstOrDefault(w => w.Id == editorVm.SelectedWall.Id);
        }
        vm.RefreshProjectData();
    }

    private void ShowReportWindow(string reportText)
    {
        if (DataContext is not MainViewModel vm || vm.SelectedWall == null) return;
        var window = new ReportWindow
        {
            DataContext = new ReportViewModel(
                reportText,
                vm.ProjectManager.Project,
                vm.SelectedWall,
                vm.ProjectManager.Loads,
                vm.ProjectManager.LoadCombinations,
                vm.ProjectManager.Studs,
                vm.ProjectManager.Materials)
        };
        window.Show(this);
    }

    private async void ShowAboutDialog()
    {
        var dialog = new AboutDialog
        {
            DataContext = new AboutViewModel()
        };
        await dialog.ShowDialog(this);
    }

    private async void ShowPreferencesDialog()
    {
        if (DataContext is not MainViewModel vm) return;
        var dialog = new PreferencesDialog
        {
            DataContext = new PreferencesViewModel(vm.ProjectManager.Preferences, vm.ProjectManager.Materials)
        };
        await dialog.ShowDialog(this);
        vm.RefreshProjectData();
    }

    private async void ShowCalculationLogDialog(string wallName, string logText)
    {
        var dialog = new CalculationLogDialog
        {
            DataContext = new CalculationLogViewModel(wallName, logText)
        };
        await dialog.ShowDialog(this);
    }

    private async void ShowSizingCriteriaDialog(Wall wall, Action<SizingCriteria> onConfirmed)
    {
        if (DataContext is not MainViewModel vm) return;
        var dialog = new SizingCriteriaDialog
        {
            DataContext = new SizingCriteriaViewModel(
                wall,
                vm.ProjectManager.SizingCriteria,
                vm.ProjectManager.Materials,
                criteria => onConfirmed(criteria))
        };
        await dialog.ShowDialog(this);
    }

    private async void ShowResultsDialog(Wall wall)
    {
        if (DataContext is not MainViewModel vm) return;
        ResultsViewModel? resultsVm = null;
        resultsVm = new ResultsViewModel(
            wall,
            vm.ProjectManager.Stories,
            () => vm.GenerateReport(),
            () =>
            {
                vm.ProjectManager.IsDirty = true;
                vm.RefreshProjectData();
            },
            () =>
            {
                ShowSizingCriteriaDialog(wall, criteria =>
                {
                    vm.ExecuteCalculationWithCriteria(criteria);
                    resultsVm?.RefreshData();
                });
            });

        var dialog = new ResultsDialog
        {
            DataContext = resultsVm
        };
        await dialog.ShowDialog(this);
        vm.RefreshProjectData();
    }

    private void OnTreeViewDoubleTapped(object? sender, TappedEventArgs e)
    {
        if (DataContext is not MainViewModel vm) return;

        // Directly find the specific TreeViewItem that was double-tapped
        if (e.Source is Visual visual)
        {
            var treeViewItem = visual.FindAncestorOfType<TreeViewItem>();
            if (treeViewItem?.DataContext is ModelExplorerNode node)
            {
                vm.SelectedExplorerNode = node;
                node.OnActivate?.Invoke();
                e.Handled = true;
                return;
            }
        }

        vm.ActivateSelectedNode();
    }

    private void OnExitClick(object? sender, RoutedEventArgs e)
    {
        Close();
    }
}