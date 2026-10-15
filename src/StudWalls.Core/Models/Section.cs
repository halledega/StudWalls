namespace StudWalls.Core.Models;

/// <summary>
/// Represents the geometric cross-section of a structural wood stud member,
/// containing standard dimensions and calculated mechanical section properties
/// (Gross Area, Moments of Inertia, Section Moduli).
/// </summary>
public class Section
{
    /// <summary>
    /// Unique database identifier for this cross-section.
    /// </summary>
    public int Id { get; set; }

    /// <summary>
    /// Nominal or actual width of a single ply of the member in millimeters (mm).
    /// Standard dressed dimensional lumber width: 38.1 mm (1.5 inches).
    /// </summary>
    public double Width { get; set; } = 38.1;

    /// <summary>
    /// Actual dressed depth of the member in millimeters (mm).
    /// Standard sizes: 88.9 mm (2x4 / 3.5 in), 139.7 mm (2x6 / 5.5 in), 184.15 mm (2x8 / 7.25 in).
    /// </summary>
    public double Depth { get; set; } = 88.9;

    /// <summary>
    /// Number of laminated/fastened plys forming the built-up compression column (1, 2, 3 plys).
    /// Built-up columns act together per CSA O86 Clause 6.5.6.3.
    /// </summary>
    public int Plys { get; set; } = 1;

    /// <summary>
    /// Unsupported length for buckling about the weak axis (Y-Y) in millimeters (mm).
    /// Typically braced by wall sheathing (e.g. 152 mm / 6 inches if sheathed with gypsum or OSB).
    /// </summary>
    public double LuWidth { get; set; } = 152.0;

    /// <summary>
    /// Unsupported length for buckling about the strong axis (X-X) in millimeters (mm).
    /// Typically the clear story height between top and bottom wall plates (e.g. 3000 mm).
    /// </summary>
    public double LuDepth { get; set; } = 3000.0;

    /// <summary>
    /// Total combined width of all plys in millimeters: Width * Plys.
    /// </summary>
    public double TotalWidth => Width * Plys;

    /// <summary>
    /// Gross cross-sectional area (Ag) in square millimeters (mm²):
    /// Ag = Width * Depth * Plys.
    /// Used directly in axial resistance equation Pr per CSA O86 Clause 6.5.6.2.3.
    /// </summary>
    public double Ag => Width * Depth * Plys;

    /// <summary>
    /// Moment of Inertia about the strong axis (X-X) in mm⁴:
    /// Ix = (TotalWidth * Depth³) / 12.
    /// </summary>
    public double Ix => (TotalWidth * Math.Pow(Depth, 3)) / 12.0;

    /// <summary>
    /// Moment of Inertia about the weak axis (Y-Y) in mm⁴:
    /// Iy = (Depth * TotalWidth³) / 12.0.
    /// </summary>
    public double Iy => (Depth * Math.Pow(TotalWidth, 3)) / 12.0;

    /// <summary>
    /// Elastic Section Modulus about the strong axis (X-X) in mm³:
    /// Sx = Ix / (Depth / 2).
    /// Used for out-of-plane wind bending checks.
    /// </summary>
    public double Sx => Depth > 0 ? Ix / (Depth / 2.0) : 0;

    /// <summary>
    /// Elastic Section Modulus about the weak axis (Y-Y) in mm³:
    /// Sy = Iy / (TotalWidth / 2).
    /// </summary>
    public double Sy => TotalWidth > 0 ? Iy / (TotalWidth / 2.0) : 0;

    /// <summary>
    /// Radius of gyration about strong axis (rx = sqrt(Ix / Ag)) in mm.
    /// </summary>
    public double Rx => Ag > 0 ? Math.Sqrt(Ix / Ag) : 0;

    /// <summary>
    /// Radius of gyration about weak axis (ry = sqrt(Iy / Ag)) in mm.
    /// </summary>
    public double Ry => Ag > 0 ? Math.Sqrt(Iy / Ag) : 0;

    /// <summary>
    /// Formatted name for the cross section (e.g., "(2) 38x140").
    /// </summary>
    public string FormattedName => Plys > 1 
        ? $"({Plys})-{Width:F0}x{Depth:F0}" 
        : $"{Width:F0}x{Depth:F0}";

    public override string ToString() => FormattedName;
}
