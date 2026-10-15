using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using StudWalls.Core.Models;
using StudWalls.Core.Reporting;

namespace StudWalls.Desktop.ViewModels;

/// <summary>
/// ViewModel managing report previewing and PDF document export.
/// </summary>
public partial class ReportViewModel : ViewModelBase
{
    private readonly ProjectInfo _project;
    private readonly Wall _wall;
    private readonly IReadOnlyList<Load> _loads;
    private readonly IReadOnlyList<LoadCombination> _combos;
    private readonly IReadOnlyList<Stud> _studs;
    private readonly IReadOnlyList<WoodMaterial> _materials;

    [ObservableProperty]
    private string _reportContent = string.Empty;

    [ObservableProperty]
    private string _statusMessage = string.Empty;

    public Func<string, Task<string?>>? RequestSavePdfPath { get; set; }
    public Action? CloseAction { get; set; }

    public ReportViewModel(
        string reportContent,
        ProjectInfo project,
        Wall wall,
        IReadOnlyList<Load> loads,
        IReadOnlyList<LoadCombination> combos,
        IReadOnlyList<Stud> studs,
        IReadOnlyList<WoodMaterial> materials)
    {
        _reportContent = reportContent;
        _project = project;
        _wall = wall;
        _loads = loads;
        _combos = combos;
        _studs = studs;
        _materials = materials;
    }

    [RelayCommand]
    public async Task ExportPdfAsync()
    {
        if (RequestSavePdfPath == null) return;

        var path = await RequestSavePdfPath("Export PDF Report (*.pdf)");
        if (string.IsNullOrWhiteSpace(path)) return;

        try
        {
            PdfReportExporter.ExportToPdf(path, _project, _wall, _loads, _combos, _studs, _materials);
            StatusMessage = $"Successfully exported PDF to: {path}";
        }
        catch (Exception ex)
        {
            StatusMessage = $"PDF export failed: {ex.Message}";
        }
    }

    [RelayCommand]
    public void Close() => CloseAction?.Invoke();
}
