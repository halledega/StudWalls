namespace StudWalls.Core.Models;

/// <summary>
/// Represents a building level or story in the structural project model.
/// Stores vertical elevations, clear stud wall heights, and floor system thicknesses.
/// </summary>
public class Story
{
    /// <summary>
    /// Unique database identifier for this story.
    /// </summary>
    public int Id { get; set; }

    /// <summary>
    /// Descriptive name of the level (e.g. "1st Floor", "2nd", "3rd", "Roof").
    /// </summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// Clear vertical wall height in millimeters (mm).
    /// Used directly as unsupported buckling length (Lu) for strong-axis stud column checks.
    /// </summary>
    public double Height { get; set; } = 3000.0;

    /// <summary>
    /// Depth/thickness of the floor joist or truss system supported above in millimeters (mm).
    /// Used for total building height and architectural elevation detailing.
    /// </summary>
    public double FloorThickness { get; set; } = 359.0;

    /// <summary>
    /// Returns the name and height of the story.
    /// </summary>
    public override string ToString() => $"{Name} (h={Height:F0} mm)";
}
