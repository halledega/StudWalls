using StudWalls.Core.Engineering;
using StudWalls.Core.Models;

namespace StudWalls.Core.Reporting;

/// <summary>
/// Generates standardized structural engineering calculation sheets and summary reports
/// adhering to the format specified in OutPutExample.txt and CSA O86-20 ("Engineering Design in Wood").
/// Exhaustively includes all governing design equations, relevant CSA O86-20 code clauses,
/// and line-by-line parameter evaluations for the governing load combination at each level.
/// </summary>
public static class DesignReportGenerator
{
    /// <summary>
    /// Generates a comprehensive text calculation report including design equations,
    /// clause citations, and individual candidate stud check evaluations for governing combinations.
    /// </summary>
    public static string GenerateReport(
        ProjectInfo project,
        Wall wall,
        IReadOnlyList<Load> loads,
        IReadOnlyList<LoadCombination> combos,
        IReadOnlyList<Stud> studs,
        IReadOnlyList<WoodMaterial> materials)
    {
        var writer = new StringWriter();

        // 1. Project Title Block
        writer.WriteLine($"Date: {project.Date:yyyy-MM-dd}");
        writer.WriteLine($"Project Number: {project.ProjectNumber}");
        writer.WriteLine($"Project Name: {project.ProjectName}");
        writer.WriteLine($"Engineer: {project.Engineer}");
        writer.WriteLine();
        writer.WriteLine($"Wall Number: {wall.Name} (Length: {wall.Length:F0} mm, Self-Weight: {wall.SelfWeight:F2} kPa)");
        writer.WriteLine();

        // 2. Load Cases Table
        writer.WriteLine("Load Cases");
        writer.WriteLine($"{"Name",-25} {"Case",-15} {"Value",10} {"Type",-10}");
        writer.WriteLine(new string('-', 62));
        foreach (var l in loads)
        {
            writer.WriteLine($"{l.Name,-25} {l.Case,-15} {l.Value,10:F2} {l.LoadType,-10}");
        }
        writer.WriteLine();

        // 3. Load Combinations Table
        writer.WriteLine("Load Combinations");
        writer.WriteLine($"{"Combination Name",-25} {"Factored Equation",-45}");
        writer.WriteLine(new string('-', 72));
        foreach (var c in combos)
        {
            var eq = string.Join(" + ", c.Items.Select(i => $"{i.Factor:F2}*{i.Load?.Name}"));
            writer.WriteLine($"{c.Name,-25} {eq,-45}");
        }
        writer.WriteLine();

        // 4. Stud Sections Table
        writer.WriteLine("Stud Sections");
        writer.WriteLine($"{"Stud Name",-25} {"Width (mm)",12} {"Depth (mm)",12} {"Plys",6} {"Area (mm²)",12}");
        writer.WriteLine(new string('-', 70));
        foreach (var s in studs)
        {
            writer.WriteLine($"{s.Name,-25} {s.Section.Width,12:F1} {s.Section.Depth,12:F1} {s.Section.Plys,6} {s.Section.Ag,12:F0}");
        }
        writer.WriteLine();

        // 5. Materials Table
        writer.WriteLine("Materials");
        writer.WriteLine($"{"Name",-18} {"Species",-20} {"Grade",-10} {"Fb",6} {"Fv",6} {"Fc",6} {"E",8} {"E05",8}");
        writer.WriteLine(new string('-', 86));
        foreach (var m in materials)
        {
            writer.WriteLine($"{m.Name,-18} {m.Species,-20} {m.Grade,-10} {m.Fb,6:F1} {m.Fv,6:F1} {m.Fc,6:F1} {m.E,8:F0} {m.E05,8:F0}");
        }
        writer.WriteLine();

        // 6. Levels Table
        writer.WriteLine("Levels");
        writer.WriteLine($"{"Level Name",-15} {"Height (mm)",12} {"Floor Thickness (mm)",22} {"Left Trib (mm)",16} {"Right Trib (mm)",16}");
        writer.WriteLine(new string('-', 85));
        foreach (var ws in wall.Stories)
        {
            writer.WriteLine($"{ws.Story?.Name ?? "Story",-15} {ws.Story?.Height ?? 0,12:F0} {ws.Story?.FloorThickness ?? 0,22:F0} {ws.TribWidthLeft,16:F0} {ws.TribWidthRight,16:F0}");
        }
        writer.WriteLine();

        // 7. Unfactored Cumulative Loads per Floor (kN/m)
        var cumulativeLoads = StudWallEngine.CalculateCumulativeLoads(wall);
        writer.WriteLine("Unfactored Total Loads Per Floor (kN/m)");
        writer.WriteLine($"{"Level",-15} {"Dead (DL)",12} {"Live (LL)",12} {"Snow (SL)",12} {"Partition",12}");
        writer.WriteLine(new string('-', 65));
        foreach (var cl in cumulativeLoads)
        {
            writer.WriteLine($"{cl.StoryName,-15} {cl.DeadLoad_kNm,12:F2} {cl.LiveLoad_kNm,12:F2} {cl.SnowLoad_kNm,12:F2} {cl.PartitionLoad_kNm,12:F2}");
        }
        writer.WriteLine();

        // 8. Factored Total Loads Per Floor (kN/m)
        var factoredLoads = StudWallEngine.CalculateFactoredLoads(cumulativeLoads, combos);
        writer.WriteLine("Factored Total Loads Per Floor (kN/m)");
        if (combos.Count > 0)
        {
            writer.Write($"{"Level",-15}");
            foreach (var c in combos)
            {
                writer.Write($" {c.Name,15}");
            }
            writer.WriteLine();
            writer.WriteLine(new string('-', 15 + (combos.Count * 16)));

            for (int i = 0; i < cumulativeLoads.Count; i++)
            {
                writer.Write($"{cumulativeLoads[i].StoryName,-15}");
                foreach (var c in combos)
                {
                    double val = factoredLoads[i].GetValueOrDefault(c.Name, 0.0);
                    writer.Write($" {val,15:F2}");
                }
                writer.WriteLine();
            }
        }
        writer.WriteLine();

        // 9. Results Summary (Governing Final Selection per Floor)
        writer.WriteLine("Results Summary");
        writer.WriteLine($"{"Level",-12} {"Member",-25} {"Material",-15} {"Spacing",-12} {"Gov. Combo",-18} {"Pf (kN)",10} {"Pr (kN)",10} {"D/C",8}");
        writer.WriteLine(new string('-', 115));
        foreach (var ws in wall.Stories)
        {
            var finalRes = ws.Results.FirstOrDefault(r => r.IsFinal)
                           ?? ws.Results.Where(r => r.DcRatio <= 1.0001).OrderBy(r => r.WoodVolume).FirstOrDefault()
                           ?? ws.Results.FirstOrDefault();

            if (finalRes != null)
            {
                writer.WriteLine($"{ws.Story?.Name ?? "Level",-12} {finalRes.FormattedDescription,-25} {finalRes.Stud?.Material.Name ?? "SPF",-15} {finalRes.Spacing + " mm",-12} {finalRes.GoverningCombo,-18} {finalRes.Pf,10:F2} {finalRes.Pr,10:F2} {finalRes.DcRatio,8:F2}");
            }
            else
            {
                writer.WriteLine($"{ws.Story?.Name ?? "Level",-12} {"NO DESIGN CALCULATED",-25}");
            }
        }
        writer.WriteLine();

        // 10. CSA O86-20 Code Check Equations & Clause References
        writer.WriteLine("CSA O86-20 Governing Design Equations & Relevant Code Clauses");
        writer.WriteLine(new string('=', 78));
        writer.WriteLine("1. Slenderness Ratio (CSA O86-20 Clause 6.5.6.2.2):");
        writer.WriteLine("   Cc = Lu / d <= 50");
        writer.WriteLine("   Where:");
        writer.WriteLine("     Lu = Effective unsupported buckling length in plane of bending (mm)");
        writer.WriteLine("     d  = Stud dimension in plane of bending (mm)");
        writer.WriteLine();
        writer.WriteLine("2. Factored Compressive Strength Parallel to Grain (CSA O86-20 Clause 6.5.6.2.3):");
        writer.WriteLine("   Fc = fc * (Kd * Kh * Ksc * Kt)  [MPa]");
        writer.WriteLine("   Where:");
        writer.WriteLine("     fc  = Specified compressive strength parallel to grain (Table 6.3.1A)");
        writer.WriteLine("     Kd  = Load duration factor (Clause 5.3.2.2 / Clause 5.3.2.3)");
        writer.WriteLine("     Kh  = System factor for load sharing (Clause 6.4.4, Kh = 1.0)");
        writer.WriteLine("     Ksc = Service condition factor for compression (Clause 6.4.2, Ksc = 1.0 for dry)");
        writer.WriteLine("     Kt  = Treatment factor for preservative or fire retardant (Clause 6.4.3, Kt = 1.0)");
        writer.WriteLine();
        writer.WriteLine("3. Size Factor for Compression Parallel to Grain (CSA O86-20 Clause 6.5.6.2.5):");
        writer.WriteLine("   Kzc = min(6.3 * (d * Lu)^(-0.13), 1.30)");
        writer.WriteLine();
        writer.WriteLine("4. Column Stability Factor (CSA O86-20 Clause 6.5.6.2.4):");
        writer.WriteLine("   Kc = [1.0 + (Fc * Kzc * Cc^3) / (35 * E05 * Kse * Kt)]^(-1)");
        writer.WriteLine("   Where:");
        writer.WriteLine("     E05 = 5th percentile modulus of elasticity (Clause 6.5.6.2.3, MPa)");
        writer.WriteLine("     Kse = Service condition factor for modulus of elasticity (Clause 6.4.2)");
        writer.WriteLine();
        writer.WriteLine("5. Factored Compressive Resistance Parallel to Grain (CSA O86-20 Clause 6.5.6.2.3):");
        writer.WriteLine("   Pr = phi * Fc * Ag * Kc * Kzc  [N]  (reported in kN)");
        writer.WriteLine("   Where:");
        writer.WriteLine("     phi = 0.80 (Resistance factor for compression, Clause 6.5.6.2.1)");
        writer.WriteLine("     Ag  = Gross cross-sectional area of member (mm²)");
        writer.WriteLine();
        writer.WriteLine("6. Compressive Demand-to-Capacity Verification (CSA O86-20 Clause 6.5.6.2):");
        writer.WriteLine("   D/C = Pf / Pr <= 1.00");
        writer.WriteLine("   Where:");
        writer.WriteLine("     Pf  = Factored compressive load per stud = Total Factored Line Load (kN/m) * Spacing (m)");
        writer.WriteLine("     Pr  = Factored compressive resistance parallel to grain (kN)");
        writer.WriteLine(new string('=', 78));
        writer.WriteLine();

        // 11. Stud Axial Capacities Table (Governing Combination Only per Level)
        writer.WriteLine("Stud Axial Capacities & Code Checks (Governing Combination Only)");
        writer.WriteLine(new string('-', 124));

        for (int i = 0; i < wall.Stories.Count; i++)
        {
            var ws = wall.Stories[i];
            var finalRes = ws.Results.FirstOrDefault(r => r.IsFinal)
                           ?? ws.Results.Where(r => r.DcRatio <= 1.0001).OrderBy(r => r.WoodVolume).FirstOrDefault()
                           ?? ws.Results.FirstOrDefault();

            string govCombo = finalRes?.GoverningCombo ?? "N/A";
            double wf = 0.0;
            if (i < factoredLoads.Count && !string.IsNullOrEmpty(govCombo))
            {
                wf = factoredLoads[i].GetValueOrDefault(govCombo, 0.0);
            }

            writer.WriteLine($"Floor: {ws.Story?.Name ?? "Story"} | Clear Height: {ws.LuDepth:F0} mm | Sheathing Lu: {ws.LuWidth:F0} mm | Gov Combo: {govCombo} (wf = {wf:F2} kN/m)");
            writer.WriteLine($"{"Member",-22} {"Spacing",-10} {"Ag (mm²)",9} {"Cc",6} {"Kd",6} {"Kzc",6} {"Kc",6} {"Fc(MPa)",8} {"Pf(kN)",9} {"Pr(kN)",9} {"D/C",7} {"Status",-14}");
            writer.WriteLine(new string('-', 124));

            if (ws.Results.Count == 0)
            {
                writer.WriteLine("No calculations available for this story. Run analysis sizing to generate checks.");
            }
            else
            {
                // Order candidates by stud depth, plys, spacing
                var candidates = ws.Results.OrderBy(r => r.Stud?.Section.Depth ?? 0)
                                           .ThenBy(r => r.Plys)
                                           .ThenByDescending(r => r.Spacing)
                                           .ToList();

                foreach (var r in candidates)
                {
                    string memberName = r.FormattedMember;
                    string statusStr = r.IsFinal ? $"{r.Status} [Selected]" : r.Status;
                    double ag = (r.Stud?.Section.Ag ?? 0) * r.Plys;
                    writer.WriteLine($"{memberName,-22} {$"{r.Spacing:F0} mm",-10} {ag,9:F0} {r.Cc,6:F1} {r.Kd,6:F2} {r.Kzc,6:F2} {r.Kc,6:F2} {r.Fc,8:F2} {r.Pf,9:F2} {r.Pr,9:F2} {r.DcRatio,7:F2} {statusStr,-14}");
                }
            }
            writer.WriteLine();
        }

        return writer.ToString();
    }
}
