using System.Text.Json.Serialization;

namespace StudWalls.Core.Models;

/// <summary>
/// Associates a Wall with a specific building Story.
/// Stores tributary floor/roof widths, unsupported stud buckling lengths,
/// and collections of specified loads tributary to the left and right sides of the wall.
/// </summary>
public class WallStory
{
    /// <summary>
    /// Unique database identifier for this wall-story segment.
    /// </summary>
    public int Id { get; set; }

    /// <summary>
    /// Foreign key ID referencing the parent Wall.
    /// </summary>
    public int WallId { get; set; }

    /// <summary>
    /// Navigation reference back to the parent Wall.
    /// </summary>
    [JsonIgnore]
    public Wall? Wall { get; set; }

    /// <summary>
    /// Foreign key ID referencing the associated building Story.
    /// </summary>
    public int StoryId { get; set; }

    /// <summary>
    /// Navigation reference to the associated building Story.
    /// </summary>
    public Story? Story { get; set; }

    /// <summary>
    /// Tributary width on the left side of the wall in millimeters (mm).
    /// Used to calculate tributary area load applied to the wall: W_left * TribWidthLeft.
    /// </summary>
    public double TribWidthLeft { get; set; } = 1000.0;

    /// <summary>
    /// Tributary width on the right side of the wall in millimeters (mm).
    /// Used to calculate tributary area load applied to the wall: W_right * TribWidthRight.
    /// </summary>
    public double TribWidthRight { get; set; } = 1500.0;

    /// <summary>
    /// Total tributary width supporting gravity loads: TribWidthLeft + TribWidthRight.
    /// </summary>
    public double TotalTribWidth => TribWidthLeft + TribWidthRight;

    /// <summary>
    /// Unsupported length for stud weak-axis (Y-Y) buckling at this level in millimeters (mm).
    /// Defaults to 152 mm (6 inches) when continuous sheathing/gypsum board is fastened.
    /// </summary>
    public double LuWidth { get; set; } = 152.0;

    /// <summary>
    /// Unsupported length for stud strong-axis (X-X) buckling at this level in millimeters (mm).
    /// Defaults to clear wall height (typically 3000 mm).
    /// </summary>
    public double LuDepth { get; set; } = 3000.0;

    /// <summary>
    /// Collection of specified loads applied to the left tributary side at this level.
    /// </summary>
    public List<Load> LoadsLeft { get; set; } = new();

    /// <summary>
    /// Collection of specified loads applied to the right tributary side at this level.
    /// </summary>
    public List<Load> LoadsRight { get; set; } = new();

    /// <summary>
    /// Computed structural design results for all stud size permutations analyzed for this floor.
    /// </summary>
    public List<DesignResult> Results { get; set; } = new();

    /// <summary>
    /// Returns a text summary of the wall story segment.
    /// </summary>
    public override string ToString() => $"{Story?.Name ?? "Story"} (Trib: {TotalTribWidth:F0} mm)";
}
