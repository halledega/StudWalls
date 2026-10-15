using CommunityToolkit.Mvvm.ComponentModel;

namespace StudWalls.Core.Models;

/// <summary>
/// Represents a multi-story load-bearing wood stud wall in the building model.
/// Contains overall geometric dimensions, self-weight, and associations to each constituent story.
/// Inherits from ObservableObject to support reactive UI property notification across dialogs.
/// </summary>
public partial class Wall : ObservableObject
{
    /// <summary>
    /// Unique database identifier for this wall.
    /// </summary>
    [ObservableProperty] private int _id;

    /// <summary>
    /// User-defined designation or tag for the wall (e.g. "W1", "Grid A Wall").
    /// </summary>
    [ObservableProperty] private string _name = "W1";

    /// <summary>
    /// Total horizontal length of the wall in millimeters (mm).
    /// Used for plan view graphics and total wall weight accumulation.
    /// </summary>
    [ObservableProperty] private double _length = 5000.0;

    /// <summary>
    /// Wall self-weight (SW) allowance in kilopascals (kPa).
    /// Represents weight of studs, plates, gypsum board, insulation, and exterior siding.
    /// Standard default: 0.50 kPa (approx. 10-12 psf).
    /// </summary>
    [ObservableProperty] private double _selfWeight = 0.50;

    /// <summary>
    /// Plan coordinate X (start point in millimeters) for Building Plan View visualization.
    /// </summary>
    [ObservableProperty] private double _planX = 0.0;

    /// <summary>
    /// Plan coordinate Y (start point in millimeters) for Building Plan View visualization.
    /// </summary>
    [ObservableProperty] private double _planY = 0.0;

    /// <summary>
    /// Wall orientation angle in degrees (0 = horizontal, 90 = vertical).
    /// </summary>
    [ObservableProperty] private double _rotationDegrees = 0.0;

    /// <summary>
    /// Multi-story segments comprising this wall from bottom story to roof.
    /// </summary>
    public List<WallStory> Stories { get; set; } = new();

    /// <summary>
    /// Total cumulative height of the wall across all active stories in millimeters.
    /// </summary>
    public double TotalHeight => Stories.Sum(s => (s.Story?.Height ?? 0) + (s.Story?.FloorThickness ?? 0));

    /// <summary>
    /// Returns the wall name and length.
    /// </summary>
    public override string ToString() => $"{Name} (L={Length:F0} mm, {Stories.Count} stories)";
}
