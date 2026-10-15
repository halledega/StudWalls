using CommunityToolkit.Mvvm.ComponentModel;
using System.Text.Json.Serialization;

namespace StudWalls.Core.Models;

/// <summary>
/// Represents the calculated structural design check and performance metrics
/// for a specific stud configuration (stud size, spacing, plys) under axial compression.
/// Directly stores all modification factors (k-factors), factored loads, factored resistances,
/// and governing Demand-Capacity (D/C) ratios according to CSA O86-20.
/// </summary>
public partial class DesignResult : ObservableObject
{
    /// <summary>
    /// Unique database identifier for this result.
    /// </summary>
    public int Id { get; set; }

    /// <summary>
    /// Foreign key ID referencing the associated WallStory level.
    /// </summary>
    public int WallStoryId { get; set; }

    /// <summary>
    /// Navigation reference to the WallStory level.
    /// </summary>
    [JsonIgnore]
    public WallStory? WallStory { get; set; }

    /// <summary>
    /// Foreign key ID referencing the Stud member evaluated.
    /// </summary>
    public int StudId { get; set; }

    /// <summary>
    /// Navigation reference to the Stud member evaluated.
    /// </summary>
    public Stud? Stud { get; set; }

    /// <summary>
    /// Center-to-center spacing of the studs in millimeters (mm).
    /// Standard spacings: 406 mm (16" o/c), 305 mm (12" o/c), 203 mm (8" o/c).
    /// </summary>
    public double Spacing { get; set; } = 406.0;

    /// <summary>
    /// Number of laminated plys forming the compression member (1, 2, or 3).
    /// </summary>
    public int Plys { get; set; } = 1;

    /// <summary>
    /// Demand-Capacity (D/C) ratio: Pf / Pr.
    /// D/C &lt;= 1.0 indicates adequate compressive strength (Pass).
    /// D/C &gt; 1.0 indicates overstressed condition (Fail).
    /// </summary>
    public double DcRatio { get; set; }

    /// <summary>
    /// Name of the governing ULS load combination producing the maximum D/C ratio.
    /// </summary>
    public string GoverningCombo { get; set; } = string.Empty;

    /// <summary>
    /// Factored compressive axial demand (Pf) acting on a single stud in kilonewtons (kN).
    /// Calculated as total factored line load (kN/m) * (Spacing / 1000).
    /// </summary>
    public double Pf { get; set; }

    /// <summary>
    /// Factored compressive resistance parallel to grain (Pr) in kilonewtons (kN).
    /// Calculated in accordance with CSA O86-20 Clause 6.5.6.2.3.
    /// </summary>
    public double Pr { get; set; }

    /// <summary>
    /// Load duration factor (Kd) per CSA O86 Clause 5.3.2.2.
    /// 0.65 for long-term dead, 1.00 for standard occupancy/live, 1.15 for short-term wind/seismic.
    /// </summary>
    public double Kd { get; set; } = 1.0;

    /// <summary>
    /// System factor (Kh) per CSA O86 Clause 6.4.4.
    /// Accounts for load-sharing in repetitive framing systems (typically 1.0 to 1.10).
    /// </summary>
    public double Kh { get; set; } = 1.0;

    /// <summary>
    /// Service condition factor for modulus of elasticity (Kse) per CSA O86 Clause 6.4.2.
    /// 1.0 for dry service conditions (equilibrium moisture content &lt;= 19%).
    /// </summary>
    public double Kse { get; set; } = 1.0;

    /// <summary>
    /// Service condition factor for compression parallel to grain (Ksc) per CSA O86 Clause 6.4.2.
    /// 1.0 for dry service conditions.
    /// </summary>
    public double Ksc { get; set; } = 1.0;

    /// <summary>
    /// Treatment factor (Kt) per CSA O86 Clause 6.4.3.
    /// Accounts for strength reduction caused by preservative or fire-retardant treatment.
    /// </summary>
    public double Kt { get; set; } = 1.0;

    /// <summary>
    /// Size factor for compression (Kzc) per CSA O86 Clause 6.5.6.2.5:
    /// Kzc = min(6.3 * (d * Lu)^(-0.13), 1.3).
    /// </summary>
    public double Kzc { get; set; } = 1.0;

    /// <summary>
    /// Column stability factor (Kc) per CSA O86 Clause 6.5.6.2.4:
    /// Accounts for elastic and inelastic column buckling.
    /// </summary>
    public double Kc { get; set; } = 1.0;

    /// <summary>
    /// Slenderness ratio (Cc = Lu / d) per CSA O86 Clause 6.5.6.2.2.
    /// Must not exceed 50 for compression members.
    /// </summary>
    public double Cc { get; set; }

    /// <summary>
    /// Factored compressive strength parallel to grain (Fc) in megapascals (MPa):
    /// Fc = fc * (Kd * Kh * Ksc * Kt).
    /// </summary>
    public double Fc { get; set; }

    /// <summary>
    /// Wood volume proxy per millimeter of wall length in mm: Ag / Spacing.
    /// Used as the objective function for optimization (lowest volume per floor = most economical).
    /// </summary>
    public double WoodVolume { get; set; }

    /// <summary>
    /// Indicates whether this design option was chosen as the finalized specification for the floor level.
    /// Marked true by default for the optimal (lowest wood volume) passing design, or chosen by engineer override.
    /// </summary>
    [ObservableProperty]
    private bool _isFinal;

    partial void OnIsFinalChanged(bool value)
    {
        if (value && WallStory != null)
        {
            foreach (var other in WallStory.Results)
            {
                if (!ReferenceEquals(other, this) && other.IsFinal)
                {
                    other.IsFinal = false;
                }
            }
        }
    }

    /// <summary>
    /// Complete breakdown of code checks across every individual factored load combination.
    /// </summary>
    public List<LoadCombinationCheck> ComboChecks { get; set; } = new();

    /// <summary>
    /// Design status: "Pass" if DcRatio &lt;= 1.0, otherwise "Fail".
    /// </summary>
    public string Status => DcRatio <= 1.0001 ? "Pass" : "Fail";

    /// <summary>
    /// Formatted member designation adhering to wood engineering standards (e.g. "2x4", "2-2x4", "3-2x6").
    /// Avoids duplicate ply prefixes such as "(1) 2-2x4".
    /// </summary>
    public string FormattedMember
    {
        get
        {
            string name = Stud?.Name ?? "Stud";

            // If name already starts with a parenthesized prefix like "(1) ", strip it
            if (name.StartsWith("(") && name.Contains(")"))
            {
                int closeIdx = name.IndexOf(')');
                if (closeIdx > 0 && closeIdx < name.Length - 1)
                {
                    name = name.Substring(closeIdx + 1).TrimStart();
                }
            }

            // If name already starts with "N-" (e.g. "2-2x4", "3-2x6"), return directly
            if (name.Length >= 2 && char.IsDigit(name[0]) && name[1] == '-')
            {
                return name;
            }

            // If name does not have a ply prefix and Plys > 1, prepend "{Plys}-" (e.g. "2-2x4")
            if (Plys > 1 && !name.StartsWith($"{Plys}-"))
            {
                return $"{Plys}-{name}";
            }

            return name;
        }
    }

    /// <summary>
    /// Compact stud designation in plys-section format (e.g. "1-2x4", "2-2x4", "1-2x6").
    /// </summary>
    public string PlysSection
    {
        get
        {
            string sectionName = "";

            if (Stud != null && !string.IsNullOrWhiteSpace(Stud.Name))
            {
                string raw = Stud.Name.Trim();
                // Strip any parenthesized prefix like "(1) "
                if (raw.StartsWith("(") && raw.Contains(")"))
                {
                    int closeIdx = raw.IndexOf(')');
                    if (closeIdx > 0 && closeIdx < raw.Length - 1)
                    {
                        raw = raw.Substring(closeIdx + 1).TrimStart();
                    }
                }

                // Extract first token before space (e.g. "2x4", "2-2x4", "2x6")
                string token = raw.Split(' ', '\t')[0];

                // If token has a ply prefix (e.g. "2-2x4", "3-2x6"), strip the digit and hyphen
                if (token.Length >= 2 && char.IsDigit(token[0]) && token[1] == '-')
                {
                    sectionName = token.Substring(2);
                }
                else
                {
                    sectionName = token;
                }
            }

            // Fallback from geometric section dimensions if sectionName is empty
            if (string.IsNullOrWhiteSpace(sectionName) && Stud?.Section != null)
            {
                double d = Stud.Section.Depth;
                if (Math.Abs(d - 88.9) < 5.0) sectionName = "2x4";
                else if (Math.Abs(d - 139.7) < 5.0) sectionName = "2x6";
                else if (Math.Abs(d - 184.15) < 5.0) sectionName = "2x8";
                else if (Math.Abs(d - 235.0) < 5.0) sectionName = "2x10";
                else if (Math.Abs(d - 285.75) < 5.0) sectionName = "2x12";
                else sectionName = $"{Stud.Section.Width:F0}x{Stud.Section.Depth:F0}";
            }

            if (string.IsNullOrWhiteSpace(sectionName))
            {
                sectionName = "Stud";
            }

            return $"{Plys}-{sectionName}";
        }
    }

    /// <summary>
    /// Formatted stud spacing designation (e.g. 16", 12", 24", 8").
    /// </summary>
    public string FormattedSpacing
    {
        get
        {
            double inches = Spacing / 25.4;
            double rounded = Math.Round(inches);
            if (Math.Abs(inches - rounded) < 0.2)
            {
                return $"{rounded:F0}\"";
            }
            return $"{Spacing:F0} mm";
        }
    }

    /// <summary>
    /// Formatted member description with spacing (e.g. "2-2x4 SPF No.1/No.2 @ 406 mm o/c").
    /// </summary>
    public string FormattedDescription => $"{FormattedMember} @ {Spacing:F0} mm o/c";

    /// <summary>
    /// Returns formatted design summary.
    /// </summary>
    public override string ToString() => $"{FormattedDescription} -> D/C: {DcRatio:F2} ({Status}) [{GoverningCombo}]";
}
