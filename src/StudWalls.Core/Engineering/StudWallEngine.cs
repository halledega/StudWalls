
using StudWalls.Core.Enums;
using StudWalls.Core.Models;

namespace StudWalls.Core.Engineering;

/// <summary>
/// Intermediate data structure holding cumulative unfactored vertical loads at a specific floor level.
/// </summary>
public record CumulativeFloorLoads(
    int StoryIndex,          // 0-based index from top (0 = roof)
    string StoryName,        // Level designation (e.g. "Roof", "3rd", "2nd")
    double DeadLoad_kNm,     // Cumulative dead load line load (kN/m)
    double LiveLoad_kNm,     // Cumulative live load line load (kN/m)
    double SnowLoad_kNm,     // Cumulative snow load line load (kN/m)
    double PartitionLoad_kNm // Cumulative partition load line load (kN/m)
);

/// <summary>
/// Core structural analysis and design engine for wood stud walls according to CSA O86-20.
/// 
/// Responsibilities:
/// 1. Top-down tributary load accumulation (dead, live, snow, partitions, wall self-weight)
/// 2. Generation of factored Ultimate Limit State (ULS) load combinations per floor
/// 3. Permutation solver iterating across lumber sections, on-center spacings (16", 12", 8"), and plys (1, 2, 3)
/// 4. Governing capacity checks against both strong-axis and weak-axis buckling
/// 5. Optimization finding the most economical section (lowest wood volume proxy) per floor level
/// </summary>
public class StudWallEngine
{
    private static readonly double[] StandardSpacingsMm = [406.0, 305.0, 203.0]; // 16", 12", 8" on-center
    private static readonly int[] StandardPlys = [1, 2, 3];

    /// <summary>
    /// Executes the full structural design calculation for all stories of the specified wall.
    /// Clears prior results and populates each WallStory with all analyzed design options,
    /// automatically flagging the most economical valid option (lowest wood volume) as IsFinal.
    /// </summary>
    /// <param name="wall">The wall model containing multi-story configuration, lengths, and load assignments.</param>
    /// <param name="availableStuds">Catalog of available stud sizes and wood materials.</param>
    /// <param name="loadCombinations">Catalog of factored ULS load combinations.</param>
    /// <returns>A tuple containing (SummaryReportText, DetailedReportText).</returns>
    public (string SummaryOutput, string DetailedOutput) Calculate(
        Wall wall,
        IReadOnlyList<Stud> availableStuds,
        IReadOnlyList<LoadCombination> loadCombinations,
        SizingCriteria? criteria = null)
    {
        if (wall.Stories.Count == 0)
        {
            return ("No stories defined for this wall.", "No stories defined for this wall.");
        }

        // 1. Calculate cumulative unfactored loads from roof down to foundation
        var cumulativeLoads = CalculateCumulativeLoads(wall);

        // 2. Calculate factored line load combinations for each story
        var factoredLoadsPerStory = CalculateFactoredLoads(cumulativeLoads, loadCombinations);

        var summaryWriter = new StringWriter();
        var detailedWriter = new StringWriter();

        summaryWriter.WriteLine($"=== STRUCTURAL SIZING SUMMARY: {wall.Name} ===");
        summaryWriter.WriteLine($"Total Height: {wall.TotalHeight / 1000.0:F2} m | Wall Length: {wall.Length / 1000.0:F2} m | Self-Weight: {wall.SelfWeight:F2} kPa\n");

        detailedWriter.WriteLine($"=== DETAILED STRUCTURAL CALCULATION REPORT: {wall.Name} ===");
        detailedWriter.WriteLine("Standards Reference: CSA O86-20 (Engineering Design in Wood) / NBCC 2020\n");

        detailedWriter.WriteLine("--- UNFACTORED CUMULATIVE LOADS PER LEVEL (kN/m) ---");
        detailedWriter.WriteLine($"{"Level",-12} {"Dead (DL)",12} {"Live (LL)",12} {"Snow (SL)",12}");
        detailedWriter.WriteLine(new string('-', 52));
        foreach (var cl in cumulativeLoads)
        {
            detailedWriter.WriteLine($"{cl.StoryName,-12} {cl.DeadLoad_kNm,12:F2} {cl.LiveLoad_kNm,12:F2} {cl.SnowLoad_kNm,12:F2}");
        }
        detailedWriter.WriteLine();

        // 3. Iterate through each story level to size studs
        for (int i = 0; i < wall.Stories.Count; i++)
        {
            var wallStory = wall.Stories[i];
            var storyName = wallStory.Story?.Name ?? $"Level {i + 1}";
            var cumLoad = cumulativeLoads[i];
            var factoredCombos = factoredLoadsPerStory[i];

            // Clear previous results for this level
            wallStory.Results.Clear();

            var solutionsForLevel = new List<DesignResult>();

            // Filter candidate studs based on engineer sizing criteria
            var studsToEvaluate = availableStuds.Where(s =>
            {
                if (criteria == null) return true;

                // 1. Material filter
                if (criteria.AllowedMaterialIds.Count > 0 && !criteria.AllowedMaterialIds.Contains(s.MaterialId))
                {
                    return false;
                }

                // 2. Nominal section filter
                if (criteria.AllowedSections.Count > 0)
                {
                    string nominal = GetNominalSectionName(s);
                    if (!criteria.AllowedSections.Contains(nominal))
                    {
                        return false;
                    }
                }

                return true;
            }).ToList();

            if (studsToEvaluate.Count == 0)
            {
                studsToEvaluate = availableStuds.ToList();
            }

            var spacingsToEvaluate = (criteria != null && criteria.AllowedSpacings.Count > 0)
                ? (IReadOnlyList<double>)criteria.AllowedSpacings
                : (IReadOnlyList<double>)StandardSpacingsMm;

            int[] allowedPlys = (criteria != null && criteria.AllowedPlys.Count > 0)
                ? criteria.AllowedPlys.ToArray()
                : StandardPlys;

            // Determine if the stud catalog contains explicit multi-ply definitions (e.g. "2-2x4")
            bool hasExplicitPlys = studsToEvaluate.Any(s => s.Section.Plys > 1 || (s.Name.Length >= 2 && char.IsDigit(s.Name[0]) && s.Name[1] == '-'));

            // Permutation loops: Stud Template x Spacing
            foreach (var studTemplate in studsToEvaluate)
            {
                int studPly = studTemplate.Section.Plys > 0 ? studTemplate.Section.Plys : 1;
                if (hasExplicitPlys && !allowedPlys.Contains(studPly))
                {
                    continue; // Skip if explicit ply count is not permitted by criteria
                }

                var plysToEvaluate = hasExplicitPlys
                    ? new[] { studPly }
                    : allowedPlys;

                foreach (var spacing in spacingsToEvaluate)
                {
                    foreach (var plys in plysToEvaluate)
                    {
                        // Construct the cross-section for this candidate design
                        var candidateSection = new Section
                        {
                            Width = studTemplate.Section.Width,
                            Depth = studTemplate.Section.Depth,
                            Plys = plys,
                            LuWidth = wallStory.LuWidth,
                            LuDepth = wallStory.LuDepth
                        };

                        double maxDcRatio = 0.0;
                        string governingComboName = string.Empty;
                        double governingPf = 0.0;
                        double governingPr = 0.0;
                        CompressiveResistanceOutput? governingOutput = null;
                        double governingKd = 1.0;

                        // Check candidate stud against every factored load combination
                        foreach (var (comboName, factoredLineLoad_kNm) in factoredCombos)
                        {
                            // Determine load duration Kd per CSA O86 Clause 5.3.2.2 / 5.3.2.3
                            bool hasLive = comboName.Contains('L', StringComparison.OrdinalIgnoreCase);
                            bool hasSnow = comboName.Contains('S', StringComparison.OrdinalIgnoreCase);

                            DurationCategory duration;
                            double pl_kN = 0.0;
                            double ps_kN = 0.0;

                            if (!hasLive && !hasSnow)
                            {
                                // Permanent dead load alone
                                duration = DurationCategory.Long;
                            }
                            else
                            {
                                duration = DurationCategory.Standard;
                                pl_kN = cumLoad.DeadLoad_kNm * (spacing / 1000.0);
                                if (hasLive) ps_kN += cumLoad.LiveLoad_kNm * (spacing / 1000.0);
                                if (hasSnow) ps_kN += cumLoad.SnowLoad_kNm * (spacing / 1000.0);
                            }

                            double kd = CsaO86_20.CalculateKd(duration, pl_kN, ps_kN);

                            // Factored axial compressive demand per stud (kN):
                            // Pf = Factored Line Load (kN/m) * Stud Spacing (m)
                            double pf = factoredLineLoad_kNm * (spacing / 1000.0);

                            // Factored compressive resistance Pr per CSA O86 Clause 6.5.6.2.3:
                            var (pr_kN, axisOutput, _) = CsaO86_20.EvaluateGoverningResistance(
                                candidateSection,
                                studTemplate.Material,
                                wallStory.LuDepth,
                                wallStory.LuWidth,
                                kd: kd,
                                kh: 1.0,
                                kse: 1.0,
                                ksc: 1.0,
                                kt: 1.0);

                            // Demand/Capacity Ratio = Pf / Pr
                            double dc = pr_kN > 0.0 ? pf / pr_kN : double.PositiveInfinity;

                            if (dc > maxDcRatio)
                            {
                                maxDcRatio = dc;
                                governingComboName = comboName;
                                governingPf = pf;
                                governingPr = pr_kN;
                                governingOutput = axisOutput;
                                governingKd = kd;
                            }
                        }

                        // Wood volume proxy: Gross Area (mm²) / Spacing (mm)
                        double woodVolume = candidateSection.Ag / spacing;

                        var result = new DesignResult
                        {
                            WallStoryId = wallStory.Id,
                            WallStory = wallStory,
                            StudId = studTemplate.Id,
                            Stud = studTemplate,
                            Spacing = spacing,
                            Plys = plys,
                            DcRatio = maxDcRatio,
                            GoverningCombo = governingComboName,
                            Pf = governingPf,
                            Pr = governingPr,
                            Kd = governingKd,
                            Kh = 1.0,
                            Kse = 1.0,
                            Ksc = 1.0,
                            Kt = 1.0,
                            Kzc = governingOutput?.Kzc ?? 1.0,
                            Kc = governingOutput?.Kc ?? 1.0,
                            Cc = governingOutput?.Cc ?? 0.0,
                            Fc = governingOutput?.Fc ?? 0.0,
                            WoodVolume = woodVolume,
                            IsFinal = false
                        };

                        solutionsForLevel.Add(result);
                        wallStory.Results.Add(result);
                    }
                }
            }

            // Sort solutions for inspection (by Depth, then Plys, then Spacing)
            solutionsForLevel.Sort((a, b) =>
            {
                int c1 = (a.Stud?.Section.Depth ?? 0).CompareTo(b.Stud?.Section.Depth ?? 0);
                if (c1 != 0) return c1;
                int c2 = a.Plys.CompareTo(b.Plys);
                if (c2 != 0) return c2;
                return b.Spacing.CompareTo(a.Spacing);
            });

            // Filter for passing solutions (D/C <= 1.0)
            var passingSolutions = solutionsForLevel.Where(s => s.DcRatio <= 1.0001).ToList();

            // -------------------------------------------------------------------------
            // PASS 2: Multi-Combination Detailed Re-Run
            // For each section/spacing combo that works (passingSolutions),
            // re-run the code checks across every defined load combination to compute
            // and record the final D/C ratio, Pf, Pr, Kd, and Kc for each load combo.
            // -------------------------------------------------------------------------
            var candidatesToEvaluate = passingSolutions.Count > 0 ? passingSolutions : solutionsForLevel;

            foreach (var workingResult in candidatesToEvaluate)
            {
                var candidateSection = new Section
                {
                    Width = workingResult.Stud!.Section.Width,
                    Depth = workingResult.Stud!.Section.Depth,
                    Plys = workingResult.Plys,
                    LuWidth = wallStory.LuWidth,
                    LuDepth = wallStory.LuDepth
                };

                workingResult.ComboChecks.Clear();

                foreach (var (comboName, factoredLineLoad_kNm) in factoredCombos)
                {
                    bool hasLive = comboName.Contains('L', StringComparison.OrdinalIgnoreCase);
                    bool hasSnow = comboName.Contains('S', StringComparison.OrdinalIgnoreCase);

                    DurationCategory duration = (!hasLive && !hasSnow) ? DurationCategory.Long : DurationCategory.Standard;
                    double pl_kN = cumLoad.DeadLoad_kNm * (workingResult.Spacing / 1000.0);
                    double ps_kN = 0.0;
                    if (hasLive) ps_kN += cumLoad.LiveLoad_kNm * (workingResult.Spacing / 1000.0);
                    if (hasSnow) ps_kN += cumLoad.SnowLoad_kNm * (workingResult.Spacing / 1000.0);

                    double kd = CsaO86_20.CalculateKd(duration, pl_kN, ps_kN);
                    double pf = factoredLineLoad_kNm * (workingResult.Spacing / 1000.0);

                    var (pr_kN, axisOutput, _) = CsaO86_20.EvaluateGoverningResistance(
                        candidateSection,
                        workingResult.Stud.Material,
                        wallStory.LuDepth,
                        wallStory.LuWidth,
                        kd: kd,
                        kh: 1.0,
                        kse: 1.0,
                        ksc: 1.0,
                        kt: 1.0);

                    double dc = pr_kN > 0.0 ? pf / pr_kN : double.PositiveInfinity;

                    var check = new LoadCombinationCheck
                    {
                        ComboName = comboName,
                        Duration = duration,
                        Kd = kd,
                        Pf = pf,
                        Pr = pr_kN,
                        Kc = axisOutput?.Kc ?? 1.0,
                        Kzc = axisOutput?.Kzc ?? 1.0,
                        Cc = axisOutput?.Cc ?? 0.0,
                        DcRatio = dc,
                        IsGoverning = (comboName == workingResult.GoverningCombo)
                    };

                    workingResult.ComboChecks.Add(check);
                }
            }

            detailedWriter.WriteLine($"--------------------------------------------------------------------------------");
            detailedWriter.WriteLine($"LEVEL: {storyName.ToUpper()} (Unsupported Height: {wallStory.LuDepth:F0} mm)");
            detailedWriter.WriteLine($"--------------------------------------------------------------------------------");
            detailedWriter.WriteLine($"{"Stud Option",-25} {"Spacing",-12} {"Gov. Combo",-18} {"Pf (kN)",10} {"Pr (kN)",10} {"D/C",8} {"Status",8}");
            detailedWriter.WriteLine(new string('-', 95));

            foreach (var sol in solutionsForLevel)
            {
                detailedWriter.WriteLine($"{sol.FormattedDescription,-25} {sol.Spacing + " mm",-12} {sol.GoverningCombo,-18} {sol.Pf,10:F2} {sol.Pr,10:F2} {sol.DcRatio,8:F2} {sol.Status,8}");
            }
            detailedWriter.WriteLine();

            if (passingSolutions.Count == 0)
            {
                summaryWriter.WriteLine($"Level: {storyName} -> NO ADEQUATE DESIGN FOUND (All stud options exceed D/C 1.0)");
                detailedWriter.WriteLine($"*** WARNING: No adequate design found for {storyName} ***\n");
            }
            else
            {
                // Optimal design = Passing option with the lowest wood volume proxy (Ag / Spacing)
                var optimalSolution = passingSolutions.OrderBy(s => s.WoodVolume).First();
                optimalSolution.IsFinal = true;

                summaryWriter.WriteLine($"Level: {storyName}");
                summaryWriter.WriteLine($"  Optimal Stud:     {optimalSolution.FormattedMember}");
                summaryWriter.WriteLine($"  Spacing:          {optimalSolution.Spacing:F0} mm o/c");
                summaryWriter.WriteLine($"  Governing Combo:  {optimalSolution.GoverningCombo}");
                summaryWriter.WriteLine($"  Factored Load Pf: {optimalSolution.Pf:F2} kN | Resistance Pr: {optimalSolution.Pr:F2} kN");
                summaryWriter.WriteLine($"  D/C Ratio:        {optimalSolution.DcRatio:F2} ({optimalSolution.Status})");
                summaryWriter.WriteLine($"  Wood Volume:      {optimalSolution.WoodVolume:F2} mm");

                // Output the complete load combination breakdown table for the optimal design
                summaryWriter.WriteLine("  Load Combination Breakdown:");
                foreach (var check in optimalSolution.ComboChecks)
                {
                    string govFlag = check.IsGoverning ? " [GOVERNS]" : "";
                    summaryWriter.WriteLine($"    {check.ComboName,-22} Pf={check.Pf,6:F2} kN | Pr={check.Pr,6:F2} kN | D/C={check.DcRatio,5:F2} ({check.Status}){govFlag}");
                }
                summaryWriter.WriteLine();

                detailedWriter.WriteLine($">> FINAL (OPTIMAL) SELECTION FOR {storyName}:");
                detailedWriter.WriteLine($"   Member: {optimalSolution.FormattedDescription}");
                detailedWriter.WriteLine($"   Material: {optimalSolution.Stud?.Material.Name} ({optimalSolution.Stud?.Material.Species} {optimalSolution.Stud?.Material.Grade})");
                detailedWriter.WriteLine($"   Kd: {optimalSolution.Kd:F2} | Kh: {optimalSolution.Kh:F2} | Kzc: {optimalSolution.Kzc:F2} | Kc: {optimalSolution.Kc:F2} | Cc: {optimalSolution.Cc:F1}");
                detailedWriter.WriteLine($"   Pf: {optimalSolution.Pf:F2} kN | Pr: {optimalSolution.Pr:F2} kN | D/C: {optimalSolution.DcRatio:F2}\n");

                detailedWriter.WriteLine($"   >> LOAD COMBINATION BREAKDOWN FOR {optimalSolution.FormattedDescription}:");
                detailedWriter.WriteLine($"   {"Load Combination",-24} {"Duration (Kd)",14} {"Pf (kN)",10} {"Pr (kN)",10} {"D/C Ratio",10} {"Status",8}");
                detailedWriter.WriteLine($"   {new string('-', 80)}");
                foreach (var check in optimalSolution.ComboChecks)
                {
                    string govFlag = check.IsGoverning ? " [GOVERNS]" : "";
                    detailedWriter.WriteLine($"   {check.ComboName,-24} {check.Kd,14:F2} {check.Pf,10:F2} {check.Pr,10:F2} {check.DcRatio,10:F2} {check.Status,8}{govFlag}");
                }
                detailedWriter.WriteLine();
            }
        }

        return (summaryWriter.ToString(), detailedWriter.ToString());
    }

    /// <summary>
    /// Calculates cumulative unfactored vertical loads (DL, LL, SL) from the top level (roof) down to the bottom.
    /// Accumulates tributary area loads times tributary widths plus wall self-weight per story.
    /// </summary>
    public static List<CumulativeFloorLoads> CalculateCumulativeLoads(Wall wall)
    {
        var result = new List<CumulativeFloorLoads>();
        double accumulatedDL = 0.0;
        double accumulatedLL = 0.0;
        double accumulatedSL = 0.0;
        double accumulatedPartition = 0.0;

        // Iterate from top of wall (index 0) down to the bottom
        for (int i = 0; i < wall.Stories.Count; i++)
        {
            var wallStory = wall.Stories[i];
            var storyName = wallStory.Story?.Name ?? $"Story {i + 1}";

            // Sum all applied loads tributary to this story level
            var allLoads = wallStory.LoadsLeft.Concat(wallStory.LoadsRight).ToList();

            double deadKpa = allLoads.Where(l => l.Case == LoadCase.Dead).Sum(l => l.Value);
            double liveKpa = allLoads.Where(l => l.Case == LoadCase.Live).Sum(l => l.Value);
            double snowKpa = allLoads.Where(l => l.Case == LoadCase.Snow).Sum(l => l.Value);
            double partitionKpa = allLoads.Where(l => l.Case == LoadCase.Partition).Sum(l => l.Value);

            // Total tributary width in meters (W_trib = Left + Right)
            double totalTribMeters = wallStory.TotalTribWidth / 1000.0;

            // Story Dead Line Load (kN/m):
            // Roof has no interior partitions; lower floors include partition allowance.
            double storyDL;
            if (i == 0) // Roof level
            {
                storyDL = (deadKpa * totalTribMeters) + wall.SelfWeight;
            }
            else // Suspended floor levels
            {
                storyDL = ((deadKpa + partitionKpa) * totalTribMeters) + wall.SelfWeight;
            }

            double storyLL = liveKpa * totalTribMeters;
            double storySL = snowKpa * totalTribMeters;
            double storyPartition = partitionKpa * totalTribMeters;

            // Top-down accumulation: cumulative load = sum of all stories above plus current story
            accumulatedDL += storyDL;
            accumulatedLL += storyLL;
            accumulatedSL += storySL;
            accumulatedPartition += storyPartition;

            result.Add(new CumulativeFloorLoads(
                StoryIndex: i,
                StoryName: storyName,
                DeadLoad_kNm: accumulatedDL,
                LiveLoad_kNm: accumulatedLL,
                SnowLoad_kNm: accumulatedSL,
                PartitionLoad_kNm: accumulatedPartition
            ));
        }

        return result;
    }

    /// <summary>
    /// Computes factored Ultimate Limit State (ULS) line loads (kN/m) for each story
    /// across all defined load combinations.
    /// </summary>
    public static List<Dictionary<string, double>> CalculateFactoredLoads(
        List<CumulativeFloorLoads> cumulativeLoads,
        IReadOnlyList<LoadCombination> combinations)
    {
        var result = new List<Dictionary<string, double>>();

        foreach (var cl in cumulativeLoads)
        {
            var comboDict = new Dictionary<string, double>();

            foreach (var combo in combinations)
            {
                double factoredLoad = 0.0;

                foreach (var item in combo.Items)
                {
                    if (item.Load == null) continue;

                    switch (item.Load.Case)
                    {
                        case LoadCase.Dead:
                        case LoadCase.Partition:
                            factoredLoad += cl.DeadLoad_kNm * item.Factor;
                            break;
                        case LoadCase.Live:
                            factoredLoad += cl.LiveLoad_kNm * item.Factor;
                            break;
                        case LoadCase.Snow:
                            factoredLoad += cl.SnowLoad_kNm * item.Factor;
                            break;
                        default:
                            break;
                    }
                }

                // If combination has no items, apply default NBCC combination: 1.25D + 1.5L
                if (combo.Items.Count == 0)
                {
                    factoredLoad = (1.25 * cl.DeadLoad_kNm) + (1.50 * cl.LiveLoad_kNm);
                }

                comboDict[combo.Name] = factoredLoad;
            }

            result.Add(comboDict);
        }

        return result;
    }

    /// <summary>
    /// Extracts the nominal lumber section designation (e.g. "2x4", "2x6", "2x8", "2x10")
    /// from a Stud model based on depth geometry or name convention.
    /// </summary>
    public static string GetNominalSectionName(Stud stud)
    {
        if (stud.Section != null)
        {
            double d = stud.Section.Depth;
            if (Math.Abs(d - 88.9) < 6.0) return "2x4";
            if (Math.Abs(d - 139.7) < 6.0) return "2x6";
            if (Math.Abs(d - 184.15) < 6.0) return "2x8";
            if (Math.Abs(d - 235.0) < 6.0) return "2x10";
            if (Math.Abs(d - 285.75) < 6.0) return "2x12";
        }
        string name = stud.Name.Trim();
        if (name.StartsWith("(") && name.Contains(")"))
        {
            int closeIdx = name.IndexOf(')');
            if (closeIdx > 0 && closeIdx < name.Length - 1)
                name = name.Substring(closeIdx + 1).TrimStart();
        }
        string token = name.Split(' ', '\t')[0];
        if (token.Length >= 2 && char.IsDigit(token[0]) && token[1] == '-')
            token = token.Substring(2);
        return token;
    }
}
