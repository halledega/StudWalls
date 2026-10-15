using StudWalls.Core.Enums;

namespace StudWalls.Core.Models;

/// <summary>
/// Contains project-level metadata and administrative information for engineering reports and title blocks.
/// </summary>
public class ProjectInfo
{
    /// <summary>
    /// Unique database identifier for the project information record.
    /// </summary>
    public int Id { get; set; } = 1;

    /// <summary>
    /// Engineering project number or code (e.g. "PRJ-2026-001").
    /// </summary>
    public string ProjectNumber { get; set; } = "PRJ-001";

    /// <summary>
    /// Name or title of the project (e.g. "Cedar Creek Multi-Family Residence").
    /// </summary>
    public string ProjectName { get; set; } = "New Building Project";

    /// <summary>
    /// Primary project street address line.
    /// </summary>
    public string ProjectAddress1 { get; set; } = string.Empty;

    /// <summary>
    /// Secondary project address line (City, Province/State, Postal Code).
    /// </summary>
    public string ProjectAddress2 { get; set; } = string.Empty;

    /// <summary>
    /// Name or initials of the structural engineer of record (EOR).
    /// </summary>
    public string Engineer { get; set; } = "Engineer, P.Eng.";

    /// <summary>
    /// Date of the analysis calculation or report generation.
    /// </summary>
    public DateTime Date { get; set; } = DateTime.Today;

    /// <summary>
    /// Active unit system for display and input (Metric or Imperial).
    /// </summary>
    public UnitSystem UnitSystem { get; set; } = UnitSystem.Metric;
}
