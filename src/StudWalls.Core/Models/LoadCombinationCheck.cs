using StudWalls.Core.Enums;

namespace StudWalls.Core.Models;

/// <summary>
/// Represents the structural code check result of a specific stud configuration (section, spacing, plys)
/// under an individual factored load combination in accordance with CSA O86-20 and NBCC 2020.
/// 
/// Enables engineers to review the complete load combination envelope for a viable stud section,
/// identifying which combinations govern and verifying demand-to-capacity (D/C) performance across all cases.
/// </summary>
public class LoadCombinationCheck
{
    /// <summary>
    /// Name or formula of the factored load combination (e.g., "1.4D", "1.25D + 1.5L", "1.25D + 1.5S").
    /// </summary>
    public string ComboName { get; set; } = string.Empty;

    /// <summary>
    /// Load duration category (Standard, Long, Short) applied per CSA O86 Clause 5.3.2.2.
    /// </summary>
    public DurationCategory Duration { get; set; } = DurationCategory.Standard;

    /// <summary>
    /// Load duration factor (Kd) per CSA O86 Clause 5.3.2.2 / 5.3.2.3.
    /// Typically 0.65 for permanent dead load alone, 1.00 for standard occupancy/snow, 1.15 for short-term wind/seismic.
    /// </summary>
    public double Kd { get; set; } = 1.0;

    /// <summary>
    /// Factored compressive axial demand (Pf) acting on the stud in kilonewtons (kN).
    /// Pf = Factored Line Load (kN/m) * (Spacing / 1000).
    /// </summary>
    public double Pf { get; set; }

    /// <summary>
    /// Factored compressive resistance parallel to grain (Pr) in kilonewtons (kN)
    /// calculated according to CSA O86-20 Clause 6.5.6.2.3.
    /// </summary>
    public double Pr { get; set; }

    /// <summary>
    /// Column stability factor (Kc) per CSA O86-20 Clause 6.5.6.2.4.
    /// </summary>
    public double Kc { get; set; } = 1.0;

    /// <summary>
    /// Size factor for compression (Kzc) per CSA O86-20 Clause 6.5.6.2.5.
    /// </summary>
    public double Kzc { get; set; } = 1.0;

    /// <summary>
    /// Maximum slenderness ratio (Cc = Lu / d) per CSA O86-20 Clause 6.5.6.2.2.
    /// </summary>
    public double Cc { get; set; }

    /// <summary>
    /// Demand-Capacity ratio: Pf / Pr.
    /// D/C &lt;= 1.0 indicates adequate compressive strength (Pass).
    /// D/C &gt; 1.0 indicates overstressed condition (Fail).
    /// </summary>
    public double DcRatio { get; set; }

    /// <summary>
    /// Indicates whether this combination is the governing (highest D/C ratio) combination for the stud member.
    /// </summary>
    public bool IsGoverning { get; set; }

    /// <summary>
    /// Code compliance status for this individual load combination ("Pass" or "Fail").
    /// </summary>
    public string Status => DcRatio <= 1.0001 ? "Pass" : "Fail";

    public override string ToString() =>
        $"{ComboName} -> Pf: {Pf:F2} kN, Pr: {Pr:F2} kN, D/C: {DcRatio:F2} ({Status}){(IsGoverning ? " [GOVERNS]" : "")}";
}
