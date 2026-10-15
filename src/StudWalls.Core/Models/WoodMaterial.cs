using StudWalls.Core.Enums;

namespace StudWalls.Core.Models;

/// <summary>
/// Represents the structural engineering properties of wood lumber species and grades
/// in accordance with CSA O86-20 Table 6.3.1A/B/C (Specified Strengths and Moduli for Sawn Lumber).
/// </summary>
public class WoodMaterial
{
    /// <summary>
    /// Unique database identifier for this wood material record.
    /// </summary>
    public int Id { get; set; }

    /// <summary>
    /// Descriptive name of the material (e.g. "SPF No.1/No.2", "DFL SS").
    /// </summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// Commercial lumber category (e.g., "Joist and Plank", "Light Framing", "Stud").
    /// </summary>
    public string Category { get; set; } = "Joist and Plank";

    /// <summary>
    /// Commercial species combination (e.g., "Spruce-Pine-Fir (SPF)", "Douglas Fir-Larch (DFL)", "Hem-Fir (HF)").
    /// </summary>
    public string Species { get; set; } = "Spruce-Pine-Fir";

    /// <summary>
    /// Structural lumber grade (e.g., "Select Structural", "No.1/No.2", "Stud").
    /// </summary>
    public string Grade { get; set; } = "No1/No2";

    /// <summary>
    /// Specified bending strength parallel to grain (Fb) in megapascals (MPa).
    /// Used for transverse wind and eccentric flexural checks per CSA O86 Clause 6.5.4.
    /// </summary>
    public double Fb { get; set; }

    /// <summary>
    /// Specified shear strength parallel to grain (Fv) in megapascals (MPa).
    /// Used for horizontal shear resistance per CSA O86 Clause 6.5.5.
    /// </summary>
    public double Fv { get; set; }

    /// <summary>
    /// Specified compressive strength parallel to grain (Fc) in megapascals (MPa).
    /// Fundamental property used to calculate factored compressive resistance (Pr)
    /// of axial column studs per CSA O86 Clause 6.5.6.2.3.
    /// </summary>
    public double Fc { get; set; }

    /// <summary>
    /// Specified compressive strength perpendicular to grain (Fcp) in megapascals (MPa).
    /// Used for bearing resistance of studs on bottom and top wall plates per CSA O86 Clause 6.5.7.
    /// </summary>
    public double Fcp { get; set; }

    /// <summary>
    /// Specified tensile strength parallel to grain (Ft) in megapascals (MPa).
    /// Used for tension resistance per CSA O86 Clause 6.5.9.
    /// </summary>
    public double Ft { get; set; }

    /// <summary>
    /// Mean modulus of elasticity (E) in megapascals (MPa).
    /// Used for elastic deflection and serviceability limit state (SLS) calculations.
    /// </summary>
    public double E { get; set; }

    /// <summary>
    /// Fifth percentile modulus of elasticity (E05) in megapascals (MPa).
    /// Critical design parameter used in column buckling and stability calculations (Kc)
    /// per CSA O86 Clause 6.5.6.2.4.
    /// </summary>
    public double E05 { get; set; }

    /// <summary>
    /// Lumber manufacturing and grading classification ("Sawn", "MSR", "MEL").
    /// Per CSA O86 Clause 6.5.6.2.3, this determines modification factor applied to E05.
    /// </summary>
    public string MaterialType { get; set; } = "Sawn";

    /// <summary>
    /// Returns a plain text representation of the wood material.
    /// </summary>
    public override string ToString() => $"{Name} ({Species} {Grade})";
}
