using System.Collections.Generic;

namespace StudWalls.Core.Models;

/// <summary>
/// Defines the engineer-specified search space and framing criteria
/// evaluated during automated wall stud sizing per CSA O86-20.
/// Restricts permutation loops to allowed lumber sections, materials, spacings, and plys.
/// </summary>
public class SizingCriteria
{
    /// <summary>
    /// Candidate nominal section designations to evaluate (e.g., "2x4", "2x6", "2x8", "2x10").
    /// </summary>
    public List<string> AllowedSections { get; set; } = new() { "2x4", "2x6" };

    /// <summary>
    /// Candidate on-center stud spacings in millimeters (mm) to evaluate.
    /// Standard modules: 609.6 mm (24"), 406.4 mm (16"), 304.8 mm (12"), 203.2 mm (8").
    /// </summary>
    public List<double> AllowedSpacings { get; set; } = new() { 406.0, 305.0 };

    /// <summary>
    /// Database IDs of the wood species and grades to evaluate.
    /// If empty, evaluates all wood materials defined in the project.
    /// </summary>
    public List<int> AllowedMaterialIds { get; set; } = new();

    /// <summary>
    /// Allowed ply counts for built-up compression members (e.g., 1, 2, 3 plys per CSA O86 Clause 6.5.6.3).
    /// </summary>
    public List<int> AllowedPlys { get; set; } = new() { 1, 2 };

    /// <summary>
    /// Maximum target Demand-to-Capacity (D/C) ratio threshold for passing designs.
    /// Standard code compliance requires Pf / Pr &lt;= 1.00 per CSA O86-20 Clause 6.5.6.2.
    /// </summary>
    public double MaxTargetDcRatio { get; set; } = 1.00;

    /// <summary>
    /// Creates a deep clone of the criteria.
    /// </summary>
    public SizingCriteria Clone() => new()
    {
        AllowedSections = new List<string>(AllowedSections),
        AllowedSpacings = new List<double>(AllowedSpacings),
        AllowedMaterialIds = new List<int>(AllowedMaterialIds),
        AllowedPlys = new List<int>(AllowedPlys),
        MaxTargetDcRatio = MaxTargetDcRatio
    };
}
