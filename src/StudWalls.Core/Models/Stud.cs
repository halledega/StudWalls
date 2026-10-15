namespace StudWalls.Core.Models;

/// <summary>
/// Represents a discrete structural stud member type available for wall framing.
/// Pairs a geometric cross-section (Section) with a wood species/grade material (WoodMaterial).
/// </summary>
public class Stud
{
    /// <summary>
    /// Unique database identifier for this stud type.
    /// </summary>
    public int Id { get; set; }

    /// <summary>
    /// Descriptive name of the stud type (e.g. "2x4 SPF No.1/No.2", "2x6 SPF No.1/No.2").
    /// </summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// Foreign key ID referencing the cross-sectional geometry record.
    /// </summary>
    public int SectionId { get; set; }

    /// <summary>
    /// Cross-sectional geometry (width, depth, default plys, moments of inertia).
    /// </summary>
    public Section Section { get; set; } = new();

    /// <summary>
    /// Foreign key ID referencing the assigned wood material record.
    /// </summary>
    public int MaterialId { get; set; }

    /// <summary>
    /// Material properties of the wood lumber (Fb, Fc, E, E05).
    /// </summary>
    public WoodMaterial Material { get; set; } = new();

    /// <summary>
    /// Returns the descriptive name of the stud.
    /// </summary>
    public override string ToString() => Name;
}
