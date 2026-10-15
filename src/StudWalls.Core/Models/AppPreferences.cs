using StudWalls.Core.Enums;

namespace StudWalls.Core.Models;

/// <summary>
/// Represents global application and design preferences for the StudWalls engineering software.
/// 
/// These defaults govern:
/// 1. Measurement system (Metric vs Imperial) per Canadian building practice.
/// 2. Structural engineering design criteria (maximum slenderness Cc limit of 50 per CSA O86-20 Cl 6.5.6.2.2).
/// 3. Default geometric properties for new wall stories (typical story height, default framing spacing).
/// 4. Default wood material species and grade selection for automated stud sizing.
/// </summary>
public class AppPreferences
{
    /// <summary>
    /// Preferred unit system for dimensional input, display, and exported calculation sheets.
    /// Default is Metric (dimensions in mm, loads in kN/m, stresses in MPa).
    /// </summary>
    public UnitSystem UnitSystem { get; set; } = UnitSystem.Metric;

    /// <summary>
    /// Default structural engineer name or title to populate into new project title blocks.
    /// </summary>
    public string DefaultEngineer { get; set; } = "Engineer, P.Eng.";

    /// <summary>
    /// Default firm or organization name for calculation report headers.
    /// </summary>
    public string DefaultCompany { get; set; } = "Structural Consulting Engineers";

    /// <summary>
    /// Default floor-to-floor story height in millimeters (mm) for new stories.
    /// Standard residential and light commercial story height is commonly 2743 mm (9 ft) or 2438 mm (8 ft).
    /// </summary>
    public double DefaultStoryHeight { get; set; } = 2700.0;

    /// <summary>
    /// Default wall dead load self-weight in kilonewtons per linear meter (kN/m).
    /// Typically 0.35 to 0.50 kN/m for 2x4 / 2x6 drywall and wood sheathed interior/exterior partitions.
    /// </summary>
    public double DefaultWallSelfWeight { get; set; } = 0.40;

    /// <summary>
    /// Default on-center stud spacing in millimeters (mm).
    /// Standard North American framing modules: 406.4 mm (16 in o.c.) or 609.6 mm (24 in o.c.).
    /// </summary>
    public double DefaultStudSpacing { get; set; } = 406.4;

    /// <summary>
    /// Maximum allowable column slenderness ratio (Cc = Lu / d).
    /// CSA O86-20 Clause 6.5.6.2.2 strictly mandates that Cc shall not exceed 50 for compression members.
    /// </summary>
    public double MaxAllowableCc { get; set; } = 50.0;

    /// <summary>
    /// Target demand-to-capacity (D/C) ratio threshold for passing designs.
    /// Standard code compliance requires Pf / Pr &lt;= 1.00.
    /// Engineers may specify a more conservative threshold (e.g., 0.90 or 0.95) if desired.
    /// </summary>
    public double MaxTargetDcRatio { get; set; } = 1.00;

    /// <summary>
    /// Default wood species and grade name to prioritize when creating new stud sections.
    /// </summary>
    public string DefaultMaterialName { get; set; } = "SPF No.1/No.2";

    /// <summary>
    /// Default untreated service condition factor for moisture (Ks = 1.0 for dry service).
    /// CSA O86-20 Clause 6.4.2.
    /// </summary>
    public double DefaultServiceConditionFactor { get; set; } = 1.00;

    /// <summary>
    /// Creates a deep clone of the preferences object.
    /// </summary>
    public AppPreferences Clone()
    {
        return new AppPreferences
        {
            UnitSystem = this.UnitSystem,
            DefaultEngineer = this.DefaultEngineer,
            DefaultCompany = this.DefaultCompany,
            DefaultStoryHeight = this.DefaultStoryHeight,
            DefaultWallSelfWeight = this.DefaultWallSelfWeight,
            DefaultStudSpacing = this.DefaultStudSpacing,
            MaxAllowableCc = this.MaxAllowableCc,
            MaxTargetDcRatio = this.MaxTargetDcRatio,
            DefaultMaterialName = this.DefaultMaterialName,
            DefaultServiceConditionFactor = this.DefaultServiceConditionFactor
        };
    }
}
