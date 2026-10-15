using SkiaSharp;
using StudWalls.Core.Engineering;
using StudWalls.Core.Models;

namespace StudWalls.Core.Reporting;

/// <summary>
/// Professional, publication-ready PDF Engineering Calculation Exporter.
/// Fully permissively licensed for commercial distribution (uses 100% free MIT SkiaSharp vector graphics).
/// 
/// Produces a multi-page structural calculation package adhering to CSA O86-20 format:
/// Page 1: Project Metadata, Governing Design Results Summary, Cumulative Gravity Loads, Specified Loads.
/// Page 2+: Detailed CSA O86-20 design equations, code clause references, and line-by-line candidate
/// stud axial capacity tables for the governing load combination at each level.
/// </summary>
public static class PdfReportExporter
{
    private const float PageWidth = 612f;   // Standard Letter width in points (8.5 inches * 72 pt/in)
    private const float PageHeight = 792f;  // Standard Letter height in points (11.0 inches * 72 pt/in)
    private const float Margin = 36f;       // 0.5 inch margins
    private const float ContentWidth = PageWidth - (2 * Margin);

    public static void ExportToPdf(
        string filePath,
        ProjectInfo project,
        Wall wall,
        IReadOnlyList<Load> loads,
        IReadOnlyList<LoadCombination> combos,
        IReadOnlyList<Stud> studs,
        IReadOnlyList<WoodMaterial> materials)
    {
        using var stream = new SKFileWStream(filePath);
        using var document = SKDocument.CreatePdf(stream);

        // Modern SkiaSharp 3.x decoupled fonts and paints
        var titleTypeface = SKTypeface.FromFamilyName("Arial", SKFontStyle.Bold);
        var normalTypeface = SKTypeface.FromFamilyName("Arial", SKFontStyle.Normal);
        var boldTypeface = SKTypeface.FromFamilyName("Arial", SKFontStyle.Bold);

        using var titleFont = new SKFont(titleTypeface, 15f);
        using var headerFont = new SKFont(boldTypeface, 11f);
        using var subHeaderFont = new SKFont(boldTypeface, 9.5f);
        using var bodyFont = new SKFont(normalTypeface, 8.5f);
        using var boldBodyFont = new SKFont(boldTypeface, 8.5f);
        using var smallFont = new SKFont(normalTypeface, 7.5f);
        using var boldSmallFont = new SKFont(boldTypeface, 7.5f);

        using var titlePaint = new SKPaint { Color = new SKColor(20, 40, 80), IsAntialias = true };
        using var headerPaint = new SKPaint { Color = new SKColor(40, 40, 40), IsAntialias = true };
        using var bodyPaint = new SKPaint { Color = SKColors.Black, IsAntialias = true };
        using var passPaint = new SKPaint { Color = new SKColor(0, 120, 0), IsAntialias = true };
        using var failPaint = new SKPaint { Color = new SKColor(180, 0, 0), IsAntialias = true };
        using var linePaint = new SKPaint { Color = new SKColor(200, 200, 200), StrokeWidth = 0.8f, IsAntialias = true };
        using var boxPaint = new SKPaint { Color = new SKColor(245, 247, 250), Style = SKPaintStyle.Fill };
        using var tableHeaderBgPaint = new SKPaint { Color = new SKColor(230, 235, 245), Style = SKPaintStyle.Fill };
        using var subHeaderBgPaint = new SKPaint { Color = new SKColor(238, 242, 250), Style = SKPaintStyle.Fill };
        using var selectedRowBgPaint = new SKPaint { Color = new SKColor(232, 245, 233), Style = SKPaintStyle.Fill };
        using var strokeBorderPaint = new SKPaint { Color = new SKColor(210, 215, 225), Style = SKPaintStyle.Stroke };

        float y = Margin;
        int pageNumber = 1;

        void DrawHeaderBlock(SKCanvas canvas)
        {
            canvas.DrawText("STUDWALLS - STRUCTURAL DESIGN REPORT", Margin, y, SKTextAlign.Left, titleFont, titlePaint);
            y += 16f;
            canvas.DrawText("Design Standards: CSA O86-20 (Engineering Design in Wood) / NBCC 2020", Margin, y, SKTextAlign.Left, bodyFont, bodyPaint);
            y += 10f;
            canvas.DrawLine(Margin, y, Margin + ContentWidth, y, linePaint);
            y += 14f;

            // Project metadata box
            canvas.DrawRect(Margin, y, ContentWidth, 56f, boxPaint);
            canvas.DrawRect(Margin, y, ContentWidth, 56f, strokeBorderPaint);

            float infoY = y + 14f;
            canvas.DrawText($"Project Name: {project.ProjectName}", Margin + 10f, infoY, SKTextAlign.Left, headerFont, headerPaint);
            canvas.DrawText($"Date: {project.Date:yyyy-MM-dd}", Margin + 350f, infoY, SKTextAlign.Left, bodyFont, bodyPaint);
            infoY += 15f;
            canvas.DrawText($"Project Number: {project.ProjectNumber}", Margin + 10f, infoY, SKTextAlign.Left, bodyFont, bodyPaint);
            canvas.DrawText($"Engineer: {project.Engineer}", Margin + 350f, infoY, SKTextAlign.Left, bodyFont, bodyPaint);
            infoY += 15f;
            canvas.DrawText($"Wall Design: {wall.Name} (Length: {wall.Length:F0} mm, Self-Weight: {wall.SelfWeight:F2} kPa)", Margin + 10f, infoY, SKTextAlign.Left, bodyFont, bodyPaint);

            y += 70f;
        }

        // ================= PAGE 1: Project Overview & Results Summary =================
        var currentPage = document.BeginPage(PageWidth, PageHeight);
        DrawHeaderBlock(currentPage);

        // Section 1: Final Results Summary
        currentPage.DrawText("1. GOVERNING RESULTS SUMMARY", Margin, y, SKTextAlign.Left, headerFont, headerPaint);
        y += 13f;

        // Table header
        float[] sumCols = [60f, 150f, 90f, 80f, 80f, 80f];
        string[] sumHeaders = ["Level", "Governing Stud", "Material", "Spacing", "Pf / Pr (kN)", "D/C Ratio"];
        float curX = Margin;

        currentPage.DrawRect(Margin, y, ContentWidth, 15f, tableHeaderBgPaint);
        for (int c = 0; c < sumHeaders.Length; c++)
        {
            currentPage.DrawText(sumHeaders[c], curX + 4f, y + 11f, SKTextAlign.Left, boldBodyFont, bodyPaint);
            curX += sumCols[c];
        }
        y += 16f;

        foreach (var ws in wall.Stories)
        {
            var finalRes = ws.Results.FirstOrDefault(r => r.IsFinal)
                           ?? ws.Results.Where(r => r.DcRatio <= 1.0001).OrderBy(r => r.WoodVolume).FirstOrDefault()
                           ?? ws.Results.FirstOrDefault();

            curX = Margin;
            currentPage.DrawLine(Margin, y, Margin + ContentWidth, y, linePaint);
            y += 2f;

            if (finalRes != null)
            {
                currentPage.DrawText(ws.Story?.Name ?? "Level", curX + 4f, y + 11f, SKTextAlign.Left, bodyFont, bodyPaint); curX += sumCols[0];
                currentPage.DrawText(finalRes.FormattedMember, curX + 4f, y + 11f, SKTextAlign.Left, bodyFont, bodyPaint); curX += sumCols[1];
                currentPage.DrawText(finalRes.Stud?.Material.Name ?? "SPF", curX + 4f, y + 11f, SKTextAlign.Left, bodyFont, bodyPaint); curX += sumCols[2];
                currentPage.DrawText($"{finalRes.Spacing:F0} mm", curX + 4f, y + 11f, SKTextAlign.Left, bodyFont, bodyPaint); curX += sumCols[3];
                currentPage.DrawText($"{finalRes.Pf:F1} / {finalRes.Pr:F1}", curX + 4f, y + 11f, SKTextAlign.Left, bodyFont, bodyPaint); curX += sumCols[4];

                var stPaint = finalRes.DcRatio <= 1.0001 ? passPaint : failPaint;
                currentPage.DrawText($"{finalRes.DcRatio:F2} ({finalRes.Status})", curX + 4f, y + 11f, SKTextAlign.Left, boldBodyFont, stPaint);
            }
            y += 15f;
        }

        y += 14f;

        // Section 2: Unfactored & Factored Cumulative Loads
        currentPage.DrawText("2. CUMULATIVE FLOOR LOADS (kN/m)", Margin, y, SKTextAlign.Left, headerFont, headerPaint);
        y += 13f;

        var cumulativeLoads = StudWallEngine.CalculateCumulativeLoads(wall);
        float[] loadCols = [80f, 110f, 110f, 110f, 130f];
        string[] loadHeaders = ["Level", "Dead Load (DL)", "Live Load (LL)", "Snow Load (SL)", "Trib Width (mm)"];
        curX = Margin;

        currentPage.DrawRect(Margin, y, ContentWidth, 15f, tableHeaderBgPaint);
        for (int c = 0; c < loadHeaders.Length; c++)
        {
            currentPage.DrawText(loadHeaders[c], curX + 4f, y + 11f, SKTextAlign.Left, boldBodyFont, bodyPaint);
            curX += loadCols[c];
        }
        y += 16f;

        for (int i = 0; i < cumulativeLoads.Count; i++)
        {
            var cl = cumulativeLoads[i];
            var ws = wall.Stories[i];
            curX = Margin;

            currentPage.DrawLine(Margin, y, Margin + ContentWidth, y, linePaint);
            y += 2f;
            currentPage.DrawText(cl.StoryName, curX + 4f, y + 11f, SKTextAlign.Left, bodyFont, bodyPaint); curX += loadCols[0];
            currentPage.DrawText($"{cl.DeadLoad_kNm:F2}", curX + 4f, y + 11f, SKTextAlign.Left, bodyFont, bodyPaint); curX += loadCols[1];
            currentPage.DrawText($"{cl.LiveLoad_kNm:F2}", curX + 4f, y + 11f, SKTextAlign.Left, bodyFont, bodyPaint); curX += loadCols[2];
            currentPage.DrawText($"{cl.SnowLoad_kNm:F2}", curX + 4f, y + 11f, SKTextAlign.Left, bodyFont, bodyPaint); curX += loadCols[3];
            currentPage.DrawText($"{ws.TotalTribWidth:F0} (L:{ws.TribWidthLeft:F0}, R:{ws.TribWidthRight:F0})", curX + 4f, y + 11f, SKTextAlign.Left, bodyFont, bodyPaint);
            y += 15f;
        }

        y += 14f;

        // Section 3: Specified Load Cases
        currentPage.DrawText("3. SPECIFIED LOAD CASES & COMBINATIONS", Margin, y, SKTextAlign.Left, headerFont, headerPaint);
        y += 13f;

        foreach (var l in loads)
        {
            currentPage.DrawText($"• {l.Name}: {l.Value:F2} kPa ({l.Case})", Margin + 10f, y + 9f, SKTextAlign.Left, bodyFont, bodyPaint);
            y += 13f;
        }

        document.EndPage();

        // ================= PAGE 2+: CSA O86-20 Equations & Governing Checks =================
        pageNumber = 2;
        currentPage = document.BeginPage(PageWidth, PageHeight);
        y = Margin;

        void CheckPageBreak(float neededHeight)
        {
            if (y + neededHeight > PageHeight - Margin)
            {
                document.EndPage();
                pageNumber++;
                currentPage = document.BeginPage(PageWidth, PageHeight);
                y = Margin;
                currentPage.DrawText($"4. DETAILED STRUCTURAL CODE CHECKS (CSA O86-20) - CONTINUED (Page {pageNumber})", Margin, y + 10f, SKTextAlign.Left, headerFont, headerPaint);
                y += 24f;
            }
        }

        // Section 4: CSA O86-20 Code Check Equations Box
        currentPage.DrawText("4. CSA O86-20 CODE CHECK EQUATIONS & RELEVANT CLAUSES", Margin, y + 10f, SKTextAlign.Left, headerFont, headerPaint);
        y += 18f;

        float eqBoxHeight = 84f;
        currentPage.DrawRect(Margin, y, ContentWidth, eqBoxHeight, boxPaint);
        currentPage.DrawRect(Margin, y, ContentWidth, eqBoxHeight, strokeBorderPaint);

        float eqY = y + 12f;
        currentPage.DrawText("• Slenderness Ratio (Clause 6.5.6.2.2):  Cc = Lu / d  <= 50", Margin + 8f, eqY, SKTextAlign.Left, smallFont, bodyPaint);
        eqY += 12f;
        currentPage.DrawText("• Factored Compressive Strength (Clause 6.5.6.2.3):  Fc = fc * (Kd * Kh * Ksc * Kt)  [MPa]", Margin + 8f, eqY, SKTextAlign.Left, smallFont, bodyPaint);
        eqY += 12f;
        currentPage.DrawText("• Size Factor for Compression (Clause 6.5.6.2.5):  Kzc = min(6.3 * (d * Lu)^(-0.13), 1.30)", Margin + 8f, eqY, SKTextAlign.Left, smallFont, bodyPaint);
        eqY += 12f;
        currentPage.DrawText("• Column Stability Factor (Clause 6.5.6.2.4):  Kc = [1.0 + (Fc * Kzc * Cc^3) / (35 * E05 * Kse * Kt)]^(-1)", Margin + 8f, eqY, SKTextAlign.Left, smallFont, bodyPaint);
        eqY += 12f;
        currentPage.DrawText("• Factored Compressive Resistance (Clause 6.5.6.2.3):  Pr = phi * Fc * Ag * Kc * Kzc  [N]   (phi = 0.80, Cl 6.5.6.2.1)", Margin + 8f, eqY, SKTextAlign.Left, smallFont, bodyPaint);
        eqY += 12f;
        currentPage.DrawText("• Demand-to-Capacity Verification (Clause 6.5.6.2):  D/C = Pf / Pr <= 1.00   (Pf = wf * Spacing)", Margin + 8f, eqY, SKTextAlign.Left, boldSmallFont, bodyPaint);

        y += eqBoxHeight + 14f;

        // Section 5: Stud Axial Capacities Table (Governing Combination Only)
        currentPage.DrawText("5. STUD AXIAL CAPACITIES & CODE CHECKS (GOVERNING COMBINATION ONLY)", Margin, y + 10f, SKTextAlign.Left, headerFont, headerPaint);
        y += 18f;

        // Column widths totaling ContentWidth (540 pt)
        float[] detCols = [90f, 50f, 45f, 35f, 30f, 30f, 30f, 50f, 50f, 70f, 60f];
        string[] detHeaders = ["Member", "Spacing", "Ag mm²", "Cc", "Kd", "Kzc", "Kc", "Pf (kN)", "Pr (kN)", "D/C Ratio", "Status"];

        foreach (var ws in wall.Stories)
        {
            CheckPageBreak(60f);

            var finalRes = ws.Results.FirstOrDefault(r => r.IsFinal)
                           ?? ws.Results.Where(r => r.DcRatio <= 1.0001).OrderBy(r => r.WoodVolume).FirstOrDefault()
                           ?? ws.Results.FirstOrDefault();

            string govCombo = finalRes?.GoverningCombo ?? "Governing Combination";

            // Level subheader banner
            currentPage.DrawRect(Margin, y, ContentWidth, 16f, subHeaderBgPaint);
            currentPage.DrawText($"Level: {ws.Story?.Name ?? "Story"}  |  Lu_strong = {ws.LuDepth:F0} mm, Lu_weak = {ws.LuWidth:F0} mm  |  Gov Combo: {govCombo}",
                Margin + 6f, y + 12f, SKTextAlign.Left, subHeaderFont, headerPaint);
            y += 18f;

            // Table Column Headers
            currentPage.DrawRect(Margin, y, ContentWidth, 14f, tableHeaderBgPaint);
            curX = Margin;
            for (int c = 0; c < detHeaders.Length; c++)
            {
                currentPage.DrawText(detHeaders[c], curX + 3f, y + 10f, SKTextAlign.Left, boldSmallFont, bodyPaint);
                curX += detCols[c];
            }
            y += 15f;

            // Ordered candidate list
            var candidates = ws.Results.OrderBy(r => r.Stud?.Section.Depth ?? 0)
                                       .ThenBy(r => r.Plys)
                                       .ThenByDescending(r => r.Spacing)
                                       .ToList();

            if (candidates.Count == 0)
            {
                currentPage.DrawText("No design results calculated for this story.", Margin + 6f, y + 10f, SKTextAlign.Left, smallFont, bodyPaint);
                y += 14f;
            }
            else
            {
                foreach (var r in candidates)
                {
                    CheckPageBreak(16f);

                    curX = Margin;
                    if (r.IsFinal)
                    {
                        currentPage.DrawRect(Margin, y, ContentWidth, 13f, selectedRowBgPaint);
                    }
                    currentPage.DrawLine(Margin, y, Margin + ContentWidth, y, linePaint);
                    y += 2f;

                    string memberName = r.FormattedMember;
                    double ag = (r.Stud?.Section.Ag ?? 0) * r.Plys;

                    var activeFont = r.IsFinal ? boldSmallFont : smallFont;
                    var stp = r.DcRatio <= 1.0001 ? passPaint : failPaint;
                    string statusStr = r.IsFinal ? $"{r.Status} *" : r.Status;

                    currentPage.DrawText(memberName, curX + 3f, y + 9f, SKTextAlign.Left, activeFont, bodyPaint); curX += detCols[0];
                    currentPage.DrawText($"{r.Spacing:F0} mm", curX + 3f, y + 9f, SKTextAlign.Left, activeFont, bodyPaint); curX += detCols[1];
                    currentPage.DrawText($"{ag:F0}", curX + 3f, y + 9f, SKTextAlign.Left, activeFont, bodyPaint); curX += detCols[2];
                    currentPage.DrawText($"{r.Cc:F1}", curX + 3f, y + 9f, SKTextAlign.Left, activeFont, bodyPaint); curX += detCols[3];
                    currentPage.DrawText($"{r.Kd:F2}", curX + 3f, y + 9f, SKTextAlign.Left, activeFont, bodyPaint); curX += detCols[4];
                    currentPage.DrawText($"{r.Kzc:F2}", curX + 3f, y + 9f, SKTextAlign.Left, activeFont, bodyPaint); curX += detCols[5];
                    currentPage.DrawText($"{r.Kc:F2}", curX + 3f, y + 9f, SKTextAlign.Left, activeFont, bodyPaint); curX += detCols[6];
                    currentPage.DrawText($"{r.Pf:F1}", curX + 3f, y + 9f, SKTextAlign.Left, activeFont, bodyPaint); curX += detCols[7];
                    currentPage.DrawText($"{r.Pr:F1}", curX + 3f, y + 9f, SKTextAlign.Left, activeFont, bodyPaint); curX += detCols[8];
                    currentPage.DrawText($"{r.DcRatio:F2}", curX + 3f, y + 9f, SKTextAlign.Left, boldSmallFont, stp); curX += detCols[9];
                    currentPage.DrawText(statusStr, curX + 3f, y + 9f, SKTextAlign.Left, boldSmallFont, stp);

                    y += 12f;
                }
            }

            y += 8f;
        }

        document.EndPage();
        document.Close();
    }
}
