namespace StudWalls.Core.Enums;

/// <summary>
/// Defines the unit system for structural inputs, calculations, and reporting.
/// </summary>
public enum UnitSystem
{
    /// <summary>
    /// Metric System: Dimensions in millimeters (mm) or meters (m),
    /// forces in kilonewtons (kN), pressures in kilopascals (kPa),
    /// uniformly distributed loads in kN/m.
    /// Internal calculation engine executes strictly in metric units.
    /// </summary>
    Metric = 0,

    /// <summary>
    /// Imperial System: Dimensions in inches (in) or feet (ft),
    /// forces in pounds (lb), pressures in pounds per square foot (psf),
    /// uniformly distributed loads in pounds per linear foot (plf).
    /// </summary>
    Imperial = 1
}

/// <summary>
/// Standard structural load cases in accordance with the National Building Code of Canada (NBCC).
/// Used to categorize specified loads for ultimate limit state (ULS) load combinations.
/// </summary>
public enum LoadCase
{
    /// <summary>
    /// Dead load (D): Permanent gravitational forces including structural framing, finishes, and self-weight.
    /// </summary>
    Dead = 0,

    /// <summary>
    /// Live load (L): Transient occupancy and movable equipment loads.
    /// </summary>
    Live = 1,

    /// <summary>
    /// Snow load (S): Meteorological roof snow and ice accumulation loads.
    /// </summary>
    Snow = 2,

    /// <summary>
    /// Wind load (W): Environmental lateral and uplift/overturning wind pressures.
    /// </summary>
    Wind = 3,

    /// <summary>
    /// Earthquake/Seismic load (E): Inertial seismic forces from ground acceleration.
    /// </summary>
    Seismic = 4,

    /// <summary>
    /// Partition load: Architectural internal partition allowances, treated as dead load in accumulation.
    /// </summary>
    Partition = 5
}

/// <summary>
/// Physical distribution type of an applied load.
/// </summary>
public enum LoadType
{
    /// <summary>
    /// Area surface pressure (kPa or psf) acting over tributary floor/roof width.
    /// </summary>
    Area = 0,

    /// <summary>
    /// Uniformly distributed line load (kN/m or plf) applied along the wall length.
    /// </summary>
    Line = 1,

    /// <summary>
    /// Concentrated point load (kN or lb) applied at discrete stud locations.
    /// </summary>
    Point = 2
}

/// <summary>
/// Classification of lumber manufacturing and grading method per CSA O86 Clause 6.2.
/// </summary>
public enum MaterialType
{
    /// <summary>
    /// Visually graded sawn lumber (e.g., No. 1/No. 2, Select Structural).
    /// </summary>
    Sawn = 0,

    /// <summary>
    /// Machine Stress-Rated (MSR) lumber, non-destructively tested for stiffness and bending strength.
    /// In CSA O86 Clause 6.5.6.2.3, E05 = 0.85 * E05_specified.
    /// </summary>
    MSR = 1,

    /// <summary>
    /// Machine Evaluated Lumber (MEL).
    /// In CSA O86 Clause 6.5.6.2.3, E05 = 0.75 * E05_specified.
    /// </summary>
    MEL = 2
}

/// <summary>
/// Load duration classification per CSA O86 Clause 5.3.2.2.
/// </summary>
public enum DurationCategory
{
    /// <summary>
    /// Short-term duration (Kd = 1.15): Wind and earthquake loadings.
    /// </summary>
    Short = 0,

    /// <summary>
    /// Standard duration (Kd = 1.00): Standard occupancy, live loads, snow loads.
    /// </summary>
    Standard = 1,

    /// <summary>
    /// Long-term/Permanent duration (Kd = 0.65): Dead loads acting alone without companion live/snow loads.
    /// </summary>
    Long = 2
}
