using StudWalls.Core.Enums;
using StudWalls.Core.Models;

namespace StudWalls.Core.Engineering;

/// <summary>
/// Result container holding the calculated factored compressive resistance and intermediate design factors
/// determined in accordance with CSA O86-20 Clause 6.5.6.2.3.
/// </summary>
public record CompressiveResistanceOutput(
    double Pr,    // Factored compressive resistance parallel to grain (N)
    double Fc,    // Modified compressive strength parallel to grain (MPa)
    double Kzc,   // Compressive size factor (Clause 6.5.6.2.5)
    double Kc,    // Column stability factor (Clause 6.5.6.2.4)
    double Cc     // Slenderness ratio (Clause 6.5.6.2.2)
);

/// <summary>
/// Implements engineering design clauses and equations from the Canadian wood design standard
/// CSA O86-20 ("Engineering Design in Wood").
/// 
/// Every calculation in this class is written with exhaustive documentation and plain English
/// explanations, allowing any structural engineer to verify the code against the printed standard.
/// </summary>
public static class CsaO86_20
{
    /// <summary>
    /// Calculates the load duration factor (Kd) in accordance with CSA O86-20 Clause 5.3.2.2.
    /// 
    /// Engineering Background:
    /// Wood exhibits a rheological time-dependent strength behavior known as the duration-of-load effect.
    /// Under short-term transient loads (wind, earthquake), wood resists higher stresses before failure
    /// than under permanent sustained loads (dead load creep rupture).
    /// </summary>
    /// <param name="duration">The dominant load duration category (Short, Standard, Long).</param>
    /// <param name="pl">Long-term permanent load component (kN or N).</param>
    /// <param name="ps">Short-term transient load component (kN or N).</param>
    /// <returns>The load duration factor Kd (typically between 0.65 and 1.15).</returns>
    public static double CalculateKd(DurationCategory duration = DurationCategory.Standard, double pl = 0.0, double ps = 0.0)
    {
        // Clause 5.3.2.3: For a combination of loads of different durations (e.g. permanent dead + transient live/snow),
        // if permanent load Pl exceeds transient load Ps > 0, Kd is determined by logarithmic interpolation.
        if (pl > ps && ps > 0)
        {
            return CalculateKdCombined(pl, ps);
        }

        // Permanent dead load acting alone without any transient companion loads
        if (pl > ps && ps == 0)
        {
            return 0.65; // Clause 5.3.2.2 Table 5.3.2.2 for Long-term duration
        }

        // Discrete standard duration categories per Table 5.3.2.2:
        return duration switch
        {
            DurationCategory.Short => 1.15,    // Wind, earthquake, impact
            DurationCategory.Standard => 1.00, // Standard occupancy live load, snow load
            DurationCategory.Long => 0.65,     // Continuous permanent dead load
            _ => 1.00
        };
    }

    /// <summary>
    /// Calculates the load duration factor Kd for combined long-term and short-term loads
    /// in accordance with CSA O86-20 Clause 5.3.2.3.
    /// 
    /// Formula:
    ///   Kd = min(1.0, max(1.0 - 0.5 * log10(Pl / Ps), 0.65))
    /// </summary>
    /// <param name="pl">Long-term load component.</param>
    /// <param name="ps">Short-term load component.</param>
    /// <returns>Interpolated Kd factor between 0.65 and 1.00.</returns>
    public static double CalculateKdCombined(double pl, double ps)
    {
        if (pl <= 0 || ps <= 0)
        {
            return 1.00;
        }

        // Clause 5.3.2.3 Equation: Kd shall not be taken as less than 0.65 or greater than 1.00
        double kd = 1.0 - 0.5 * Math.Log10(pl / ps);
        return Math.Min(1.00, Math.Max(0.65, kd));
    }

    /// <summary>
    /// Calculates the slenderness ratio (Cc) of a compression member
    /// in accordance with CSA O86-20 Clause 6.5.6.2.2.
    /// 
    /// Formula:
    ///   Cc = Lu / d
    /// Where:
    ///   Lu = Unsupported length between lateral supports in the buckling plane (mm)
    ///   d  = Cross-sectional dimension in the buckling plane (mm)
    /// </summary>
    /// <param name="lu">Effective unsupported length (mm).</param>
    /// <param name="dimension">Member dimension in plane of buckling (mm).</param>
    /// <returns>Slenderness ratio Cc (dimensionless). Must not exceed 50.</returns>
    public static double CalculateSlendernessRatio(double lu, double dimension)
    {
        if (dimension <= 0.0) return 0.0;
        return lu / dimension;
    }

    /// <summary>
    /// Calculates the factored compressive resistance parallel to grain (Pr) of a wood stud
    /// in accordance with CSA O86-20 Clause 6.5.6.2.3.
    /// 
    /// Formula:
    ///   Pr = phi * Fc * Ag * Kc * Kzc
    /// Where:
    ///   - phi = 0.80 (Resistance factor for sawn lumber in compression per Clause 6.5.6.2.1)
    ///   - Fc  = Factored compressive strength parallel to grain = fc * (Kd * Kh * Ksc * Kt) (MPa)
    ///   - Ag  = Gross cross-sectional area (mm²)
    ///   - Kc  = Column stability factor accounting for lateral-torsional or flexural buckling (Clause 6.5.6.2.4)
    ///   - Kzc = Size factor for compressive resistance (Clause 6.5.6.2.5)
    /// </summary>
    /// <param name="section">The cross-section geometry of the stud member.</param>
    /// <param name="material">The wood lumber material properties.</param>
    /// <param name="lu">Unsupported buckling length for the axis being analyzed (mm).</param>
    /// <param name="bucklingDimension">The cross-sectional dimension in the plane of buckling (depth for strong axis, thickness for weak axis).</param>
    /// <param name="kd">Load duration factor (Clause 5.3.2.2).</param>
    /// <param name="kh">System factor (Clause 6.4.4, default = 1.0).</param>
    /// <param name="kse">Service condition factor for modulus of elasticity (Clause 6.4.2, default = 1.0 for dry).</param>
    /// <param name="ksc">Service condition factor for compression parallel to grain (Clause 6.4.2, default = 1.0 for dry).</param>
    /// <param name="kt">Treatment factor for preservative/fire-retardant treatments (Clause 6.4.3, default = 1.0).</param>
    /// <returns>CompressiveResistanceOutput containing Pr (in Newtons), Fc, Kzc, Kc, and Cc.</returns>
    public static CompressiveResistanceOutput CalculateCompressiveResistance(
        Section section,
        WoodMaterial material,
        double lu,
        double bucklingDimension,
        double kd = 1.0,
        double kh = 1.0,
        double kse = 1.0,
        double ksc = 1.0,
        double kt = 1.0)
    {
        // Clause 6.5.6.2.1: Resistance factor for compression parallel to grain in sawn lumber
        const double phi = 0.80;

        // Gross cross-sectional area Ag (mm²)
        double ag = section.Ag;

        // Clause 6.5.6.2.3: Modulus of elasticity for column design
        // E05 is the fifth percentile modulus of elasticity.
        // For MSR lumber: E05 is taken as 0.85 * specified E05.
        // For MEL lumber: E05 is taken as 0.75 * specified E05.
        // For visually graded sawn lumber: E05 is taken as specified E05.
        double e05 = material.MaterialType.ToUpperInvariant() switch
        {
            "MSR" => 0.85 * material.E05,
            "MEL" => 0.75 * material.E05,
            _ => material.E05
        };

        // Clause 6.5.6.2.2: Slenderness ratio Cc = Lu / d
        double cc = CalculateSlendernessRatio(lu, bucklingDimension);

        // Clause 6.5.6.2.3: Factored compressive strength parallel to grain Fc
        // Fc = fc * (Kd * Kh * Ksc * Kt)
        double fc = material.Fc * (kd * kh * ksc * kt);

        // Clause 6.5.6.2.5: Size factor for compression parallel to grain Kzc
        // For sawn lumber: Kzc = min(6.3 * (d * Lu)^(-0.13), 1.30)
        double kzc = 1.30;
        if (bucklingDimension > 0 && lu > 0)
        {
            double dimensionTimesLength = bucklingDimension * lu;
            kzc = Math.Min(6.3 * Math.Pow(dimensionTimesLength, -0.13), 1.30);
        }

        // Clause 6.5.6.2.4: Column stability factor Kc
        // Formula: Kc = [1.0 + (Fc * Kzc * Cc^3) / (35 * E05 * Kse * Kt)]^(-1)
        double kc = 0.0;
        double denominator = 35.0 * e05 * kse * kt;
        if (denominator > 0.0)
        {
            double numerator = fc * kzc * Math.Pow(cc, 3);
            kc = Math.Pow(1.0 + (numerator / denominator), -1.0);
        }

        // Clause 6.5.6.2.2 Code Check:
        // "The slenderness ratio, Cc, shall not exceed 50 for compression members."
        // If slenderness ratio exceeds 50, member fails code limit and resistance is zero.
        double pr;
        if (cc > 50.0 || ag <= 0.0)
        {
            pr = 0.0;
        }
        else
        {
            // Clause 6.5.6.2.3: Pr = phi * Fc * Ag * Kc * Kzc (Result in Newtons)
            pr = phi * fc * ag * kc * kzc;
        }

        return new CompressiveResistanceOutput(pr, fc, kzc, kc, cc);
    }

    /// <summary>
    /// Computes the governing compressive resistance (Pr) for a stud cross-section,
    /// evaluating buckling about both the strong axis (X-X) and weak axis (Y-Y),
    /// and returning the minimum governing capacity in kilonewtons (kN).
    /// </summary>
    /// <param name="section">The stud cross-section geometry.</param>
    /// <param name="material">The wood lumber material properties.</param>
    /// <param name="luStrongAxis">Unsupported buckling length for strong axis X-X in mm (typically clear wall height).</param>
    /// <param name="luWeakAxis">Unsupported buckling length for weak axis Y-Y in mm (typically sheathing fastener spacing or nogging).</param>
    /// <param name="kd">Load duration factor.</param>
    /// <param name="kh">System factor.</param>
    /// <param name="kse">Service condition factor for E.</param>
    /// <param name="ksc">Service condition factor for Fc.</param>
    /// <param name="kt">Treatment factor.</param>
    /// <returns>A tuple with governing Pr (in kN) and the detailed results for the governing axis.</returns>
    public static (double Pr_kN, CompressiveResistanceOutput GoverningOutput, string GoverningAxis) EvaluateGoverningResistance(
        Section section,
        WoodMaterial material,
        double luStrongAxis,
        double luWeakAxis,
        double kd = 1.0,
        double kh = 1.0,
        double kse = 1.0,
        double ksc = 1.0,
        double kt = 1.0)
    {
        // 1. Strong axis buckling check (buckles in depth direction about X-X axis)
        var strongAxis = CalculateCompressiveResistance(
            section, material, luStrongAxis, section.Depth, kd, kh, kse, ksc, kt);

        // 2. Weak axis buckling check (buckles in width direction about Y-Y axis)
        // For a multi-ply stud (e.g. 2-ply or 3-ply), total thickness = Width * Plys
        double weakAxisDimension = section.TotalWidth;
        var weakAxis = CalculateCompressiveResistance(
            section, material, luWeakAxis, weakAxisDimension, kd, kh, kse, ksc, kt);

        // Strong axis Pr (kN) vs Weak axis Pr (kN)
        double strongPr_kN = strongAxis.Pr / 1000.0;
        double weakPr_kN = weakAxis.Pr / 1000.0;

        if (weakPr_kN <= strongPr_kN)
        {
            return (weakPr_kN, weakAxis, "Weak Axis (Y-Y)");
        }
        else
        {
            return (strongPr_kN, strongAxis, "Strong Axis (X-X)");
        }
    }
}
