using System.Text.Json.Serialization;

namespace StudWalls.Core.Models;

/// <summary>
/// Represents a Factored Ultimate Limit State (ULS) Load Combination
/// in accordance with the National Building Code of Canada (NBCC) Table 4.1.3.2.A.
/// Combines specified loads multiplied by safety factors (e.g. 1.25D + 1.5L + 0.5S).
/// </summary>
public class LoadCombination
{
    /// <summary>
    /// Unique database identifier for this load combination.
    /// </summary>
    public int Id { get; set; }

    /// <summary>
    /// Descriptive equation name of the combination (e.g. "1.4D", "1.25D + 1.5L", "1.25D + 1.5S").
    /// </summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// Individual factored load items comprising this combination.
    /// </summary>
    public List<LoadCombinationItem> Items { get; set; } = new();

    /// <summary>
    /// Helper method to append a load and factor to the combination.
    /// </summary>
    public void AddItem(Load load, double factor)
    {
        Items.Add(new LoadCombinationItem
        {
            LoadId = load.Id,
            Load = load,
            Factor = factor
        });
    }

    /// <summary>
    /// Returns the descriptive name of the load combination.
    /// </summary>
    public override string ToString() => Name;
}

/// <summary>
/// Represents an individual factored component within a LoadCombination.
/// Links a specified Load case to its load multiplier factor.
/// </summary>
public class LoadCombinationItem
{
    /// <summary>
    /// Unique database identifier for this combination item.
    /// </summary>
    public int Id { get; set; }

    /// <summary>
    /// Foreign key ID referencing the parent LoadCombination.
    /// </summary>
    public int LoadCombinationId { get; set; }

    /// <summary>
    /// Navigation reference to the parent LoadCombination.
    /// </summary>
    [JsonIgnore]
    public LoadCombination? LoadCombination { get; set; }

    /// <summary>
    /// Foreign key ID referencing the specific Load case.
    /// </summary>
    public int LoadId { get; set; }

    /// <summary>
    /// Navigation reference to the specified Load case.
    /// </summary>
    public Load? Load { get; set; }

    /// <summary>
    /// Factoring multiplier applied to this load (e.g. 1.40 for dead load alone, 1.25 for dead with companion live, 1.50 for principal live).
    /// </summary>
    public double Factor { get; set; } = 1.0;

    /// <summary>
    /// Returns a text representation of the factored term (e.g. "1.25 * Roof Dead").
    /// </summary>
    public override string ToString() => $"{Factor:F2} * {Load?.Name ?? "Load"}";
}
