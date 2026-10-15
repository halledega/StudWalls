using StudWalls.Core.Enums;

namespace StudWalls.Core.Engineering;

/// <summary>
/// Provides high-precision structural engineering unit conversions between
/// internal Metric units (mm, m, kN, kPa, kN/m) and user-facing Imperial units (in, ft, lb, psf, plf).
/// </summary>
public static class UnitConverter
{
    // Exact physical conversion constants
    public const double MmPerInch = 25.4;
    public const double MmPerFoot = 304.8;
    public const double MetersPerFoot = 0.3048;
    public const double KPaPerPsf = 0.04788026;       // 1 lbf/ft² = 47.88026 Pa = 0.04788026 kPa
    public const double KnPerPound = 0.0044482216;     // 1 lbf = 4.4482216 N = 0.0044482216 kN
    public const double KnPerMeterPerPlf = 0.014593903;// 1 lbf/ft = 14.5939 N/m = 0.014593903 kN/m

    /// <summary>
    /// Converts a pressure/stress value to internal Metric (kPa).
    /// </summary>
    public static double PressureToMetric(double value, UnitSystem system) =>
        system == UnitSystem.Imperial ? value * KPaPerPsf : value;

    /// <summary>
    /// Converts a pressure/stress value from internal Metric (kPa) to display units (kPa or psf).
    /// </summary>
    public static double PressureFromMetric(double value, UnitSystem system) =>
        system == UnitSystem.Imperial ? value / KPaPerPsf : value;

    /// <summary>
    /// Symbol for pressure: "kPa" or "psf".
    /// </summary>
    public static string PressureUnit(UnitSystem system) =>
        system == UnitSystem.Imperial ? "psf" : "kPa";

    /// <summary>
    /// Converts a uniformly distributed line load to internal Metric (kN/m).
    /// </summary>
    public static double LineLoadToMetric(double value, UnitSystem system) =>
        system == UnitSystem.Imperial ? value * KnPerMeterPerPlf : value;

    /// <summary>
    /// Converts a uniformly distributed line load from internal Metric (kN/m) to display units (kN/m or plf).
    /// </summary>
    public static double LineLoadFromMetric(double value, UnitSystem system) =>
        system == UnitSystem.Imperial ? value / KnPerMeterPerPlf : value;

    /// <summary>
    /// Symbol for line load: "kN/m" or "plf".
    /// </summary>
    public static string LineLoadUnit(UnitSystem system) =>
        system == UnitSystem.Imperial ? "plf" : "kN/m";

    /// <summary>
    /// Converts a force/point load to internal Metric (kN).
    /// </summary>
    public static double ForceToMetric(double value, UnitSystem system) =>
        system == UnitSystem.Imperial ? value * KnPerPound : value;

    /// <summary>
    /// Converts a force/point load from internal Metric (kN) to display units (kN or lb).
    /// </summary>
    public static double ForceFromMetric(double value, UnitSystem system) =>
        system == UnitSystem.Imperial ? value / KnPerPound : value;

    /// <summary>
    /// Symbol for force: "kN" or "lb".
    /// </summary>
    public static string ForceUnit(UnitSystem system) =>
        system == UnitSystem.Imperial ? "lb" : "kN";

    /// <summary>
    /// Converts a small dimension (stud spacing, cross-section size) to internal Metric (mm).
    /// </summary>
    public static double SmallLengthToMetric(double value, UnitSystem system) =>
        system == UnitSystem.Imperial ? value * MmPerInch : value;

    /// <summary>
    /// Converts a small dimension from internal Metric (mm) to display units (mm or inches).
    /// </summary>
    public static double SmallLengthFromMetric(double value, UnitSystem system) =>
        system == UnitSystem.Imperial ? value / MmPerInch : value;

    /// <summary>
    /// Symbol for small length: "mm" or "in".
    /// </summary>
    public static string SmallLengthUnit(UnitSystem system) =>
        system == UnitSystem.Imperial ? "in" : "mm";

    /// <summary>
    /// Converts a large dimension (wall length, story height, tributary width) to internal Metric (mm).
    /// If Imperial, input is in feet; if Metric, input is in meters or millimeters.
    /// </summary>
    public static double LargeLengthFeetOrMetersToMetricMm(double value, UnitSystem system) =>
        system == UnitSystem.Imperial ? value * MmPerFoot : value * 1000.0;

    /// <summary>
    /// Converts internal Metric (mm) to display units (meters or feet).
    /// </summary>
    public static double LargeLengthToFeetOrMeters(double valueMm, UnitSystem system) =>
        system == UnitSystem.Imperial ? valueMm / MmPerFoot : valueMm / 1000.0;

    /// <summary>
    /// Symbol for large length: "m" or "ft".
    /// </summary>
    public static string LargeLengthUnit(UnitSystem system) =>
        system == UnitSystem.Imperial ? "ft" : "m";
}
