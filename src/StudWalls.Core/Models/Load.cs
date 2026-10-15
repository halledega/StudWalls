using StudWalls.Core.Enums;

namespace StudWalls.Core.Models;

/// <summary>
/// Represents an unfactored specified load case acting upon building stories and walls
/// in accordance with the National Building Code of Canada (NBCC).
/// </summary>
public class Load
{
    /// <summary>
    /// Unique database identifier for this load definition.
    /// </summary>
    public int Id { get; set; }

    /// <summary>
    /// User-friendly label for the load (e.g. "Roof Dead", "Suite Live", "Snow").
    /// </summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// Structural load case classification (Dead, Live, Snow, Wind, Seismic, Partition).
    /// Used by load combination equations to apply appropriate NBCC load factors.
    /// </summary>
    public LoadCase Case { get; set; } = LoadCase.Dead;

    /// <summary>
    /// Nominal unfactored magnitude of the load in kilopascals (kPa for area load)
    /// or kilonewtons per meter (kN/m for line load).
    /// </summary>
    public double Value { get; set; }

    /// <summary>
    /// Distribution type (Area load, Line load, Point load).
    /// </summary>
    public LoadType LoadType { get; set; } = LoadType.Area;

    /// <summary>
    /// Returns the descriptive name and value of the load.
    /// </summary>
    public override string ToString() => $"{Name} ({Value:F2} kPa - {Case})";
}
