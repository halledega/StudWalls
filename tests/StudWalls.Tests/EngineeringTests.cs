using StudWalls.Core.Data;
using StudWalls.Core.Engineering;
using StudWalls.Core.Enums;
using StudWalls.Core.Models;
using StudWalls.Core.Reporting;
using Xunit;

namespace StudWalls.Tests;

public class EngineeringTests
{
    [Fact]
    public void Test_LoadDurationFactor_Kd()
    {
        // Standard duration
        double kdStd = CsaO86_20.CalculateKd(DurationCategory.Standard);
        Assert.Equal(1.00, kdStd, 3);

        // Short duration (wind/seismic)
        double kdShort = CsaO86_20.CalculateKd(DurationCategory.Short);
        Assert.Equal(1.15, kdShort, 3);

        // Long duration (dead load permanent)
        double kdLong = CsaO86_20.CalculateKd(DurationCategory.Long);
        Assert.Equal(0.65, kdLong, 3);

        // Combined duration when Pl > Ps
        double kdCombined = CsaO86_20.CalculateKd(DurationCategory.Standard, pl: 20.0, ps: 10.0);
        Assert.True(kdCombined >= 0.65 && kdCombined <= 1.00);
    }

    [Fact]
    public void Test_SlendernessRatio_Cc_CalculationAndLimit()
    {
        // Lu = 3000 mm, depth = 88.9 mm (2x4)
        double cc = CsaO86_20.CalculateSlendernessRatio(3000.0, 88.9);
        Assert.Equal(3000.0 / 88.9, cc, 2);
        Assert.True(cc <= 50.0); // Under code limit

        // Lu = 5000 mm, depth = 88.9 mm => Cc = 56.24 > 50 (Exceeds code limit)
        double ccExcessive = CsaO86_20.CalculateSlendernessRatio(5000.0, 88.9);
        Assert.True(ccExcessive > 50.0);

        var section = new Section { Width = 38.1, Depth = 88.9, Plys = 1 };
        var material = new WoodMaterial { Fc = 11.5, E05 = 6500.0 };

        // Compressive resistance must be 0 when Cc > 50
        var result = CsaO86_20.CalculateCompressiveResistance(section, material, 5000.0, 88.9);
        Assert.Equal(0.0, result.Pr);
    }

    [Fact]
    public void Test_CompressiveResistance_Pr_PositiveUnderValidConditions()
    {
        var section = new Section { Width = 38.1, Depth = 139.7, Plys = 1 }; // 2x6
        var material = new WoodMaterial
        {
            Name = "SPF No.1/No.2",
            Fc = 11.5,
            E05 = 6500.0,
            MaterialType = "Sawn"
        };

        var result = CsaO86_20.CalculateCompressiveResistance(section, material, lu: 2700.0, bucklingDimension: 139.7);

        Assert.True(result.Pr > 0.0);
        Assert.True(result.Kc > 0.0 && result.Kc <= 1.0);
        Assert.True(result.Kzc > 0.0 && result.Kzc <= 1.30);
    }

    [Fact]
    public void Test_MultiStoryCumulativeLoadAccumulation()
    {
        var (_, walls, _, _, _, _, _) = SeedData.CreateStarterProject();
        var wall1 = walls.First();

        var cumulative = StudWallEngine.CalculateCumulativeLoads(wall1);

        Assert.Equal(wall1.Stories.Count, cumulative.Count);

        // Top level (index 0) has dead load from roof
        Assert.True(cumulative[0].DeadLoad_kNm > 0);

        // Lower level (index 1) must have higher cumulative dead load than roof
        Assert.True(cumulative[1].DeadLoad_kNm > cumulative[0].DeadLoad_kNm);

        // Level 2 (index 2) must accumulate even more dead load
        Assert.True(cumulative[2].DeadLoad_kNm > cumulative[1].DeadLoad_kNm);
    }

    [Fact]
    public void Test_StudWallEngine_FullCalculationProducesResults()
    {
        var (_, walls, _, _, materials, studs, combos) = SeedData.CreateStarterProject();
        var wall1 = walls.First();

        var engine = new StudWallEngine();
        var (summary, detailed) = engine.Calculate(wall1, studs, combos);

        Assert.False(string.IsNullOrWhiteSpace(summary));
        Assert.False(string.IsNullOrWhiteSpace(detailed));

        foreach (var ws in wall1.Stories)
        {
            Assert.NotEmpty(ws.Results);
            // Verify optimal result was selected
            var finalRes = ws.Results.FirstOrDefault(r => r.IsFinal);
            Assert.NotNull(finalRes);
            Assert.True(finalRes.DcRatio > 0.0);
            Assert.NotEmpty(finalRes.ComboChecks);
            Assert.Equal(combos.Count, finalRes.ComboChecks.Count);
            Assert.Contains(finalRes.ComboChecks, c => c.IsGoverning);
        }
    }

    [Fact]
    public void Test_StudWallEngine_MultiComboChecks_Pass2()
    {
        var (_, walls, _, _, _, studs, combos) = SeedData.CreateStarterProject();
        var wall1 = walls.First();

        var engine = new StudWallEngine();
        engine.Calculate(wall1, studs, combos);

        foreach (var ws in wall1.Stories)
        {
            var passingResults = ws.Results.Where(r => r.DcRatio <= 1.0001).ToList();
            foreach (var r in passingResults)
            {
                Assert.NotEmpty(r.ComboChecks);
                Assert.Equal(combos.Count, r.ComboChecks.Count);
                Assert.Contains(r.ComboChecks, c => c.IsGoverning);
                // Verify governing combo in check matches result's governing combo
                var govCheck = r.ComboChecks.First(c => c.IsGoverning);
                Assert.Equal(r.GoverningCombo, govCheck.ComboName);
                Assert.Equal(r.DcRatio, govCheck.DcRatio, 3);
            }
        }
    }

    [Fact]
    public void Test_ProjectManager_SaveAndLoadSqlite()
    {
        var tempDb = Path.Combine(Path.GetTempPath(), $"test_studwalls_{Guid.NewGuid()}.swproj");

        try
        {
            var pm = new ProjectManager();
            pm.Project.ProjectName = "Unit Test Project";
            pm.Preferences.DefaultStoryHeight = 3000.0;
            pm.Preferences.DefaultEngineer = "Senior Structural Engineer, P.Eng.";
            pm.Preferences.MaxAllowableCc = 45.0;
            pm.SaveToSqlite(tempDb);

            var pmReloaded = new ProjectManager();
            pmReloaded.LoadFromSqlite(tempDb);

            Assert.Equal("Unit Test Project", pmReloaded.Project.ProjectName);
            Assert.Equal(pm.Walls.Count, pmReloaded.Walls.Count);
            Assert.Equal(pm.Stories.Count, pmReloaded.Stories.Count);
            Assert.Equal(pm.Materials.Count, pmReloaded.Materials.Count);
            Assert.Equal(3000.0, pmReloaded.Preferences.DefaultStoryHeight);
            Assert.Equal("Senior Structural Engineer, P.Eng.", pmReloaded.Preferences.DefaultEngineer);
            Assert.Equal(45.0, pmReloaded.Preferences.MaxAllowableCc);
        }
        finally
        {
            if (File.Exists(tempDb)) File.Delete(tempDb);
        }
    }

    [Fact]
    public void Test_ProjectManager_PreferencesJsonExportImport()
    {
        var tempJson = Path.Combine(Path.GetTempPath(), $"test_studwalls_{Guid.NewGuid()}.json");

        try
        {
            var pm = new ProjectManager();
            pm.Preferences.DefaultWallSelfWeight = 0.55;
            pm.Preferences.MaxTargetDcRatio = 0.95;
            pm.ExportToJson(tempJson);

            var pmReloaded = new ProjectManager();
            pmReloaded.ImportFromJson(tempJson);

            Assert.Equal(0.55, pmReloaded.Preferences.DefaultWallSelfWeight);
            Assert.Equal(0.95, pmReloaded.Preferences.MaxTargetDcRatio);
        }
        finally
        {
            if (File.Exists(tempJson)) File.Delete(tempJson);
        }
    }

    [Fact]
    public void Test_UnitConverter_AccurateMetricImperialConversions()
    {
        // 1 inch = 25.4 mm
        double mm = UnitConverter.SmallLengthToMetric(1.0, UnitSystem.Imperial);
        Assert.Equal(25.4, mm, 4);

        double inch = UnitConverter.SmallLengthFromMetric(25.4, UnitSystem.Imperial);
        Assert.Equal(1.0, inch, 4);

        // 100 plf to kN/m
        double knm = UnitConverter.LineLoadToMetric(100.0, UnitSystem.Imperial);
        Assert.Equal(1.45939, knm, 3);

        double plf = UnitConverter.LineLoadFromMetric(knm, UnitSystem.Imperial);
        Assert.Equal(100.0, plf, 2);

        // In Metric mode, values pass through untouched
        Assert.Equal(25.0, UnitConverter.SmallLengthToMetric(25.0, UnitSystem.Metric));
        Assert.Equal(5.0, UnitConverter.LineLoadToMetric(5.0, UnitSystem.Metric));
    }

    [Fact]
    public void Test_Wall_ObservablePropertiesNotify()
    {
        var wall = new Wall { Id = 1, Name = "W1", Length = 4000.0, SelfWeight = 0.5 };
        var changedProps = new List<string>();
        wall.PropertyChanged += (s, e) => { if (e.PropertyName != null) changedProps.Add(e.PropertyName); };

        wall.Name = "W1_Renamed";
        wall.Length = 6000.0;
        wall.SelfWeight = 0.65;

        Assert.Contains(nameof(Wall.Name), changedProps);
        Assert.Contains(nameof(Wall.Length), changedProps);
        Assert.Contains(nameof(Wall.SelfWeight), changedProps);
        Assert.Equal("W1_Renamed", wall.Name);
        Assert.Equal(6000.0, wall.Length);
        Assert.Equal(0.65, wall.SelfWeight);
    }

    [Fact]
    public void Test_DesignReportGenerator_IncludesEquationsAndClauses()
    {
        var pm = new ProjectManager();
        var engine = new StudWallEngine();
        var wall = pm.Walls.First();

        // Run calculation so wall has results
        engine.Calculate(wall, pm.Studs, pm.LoadCombinations);

        string report = DesignReportGenerator.GenerateReport(
            pm.Project, wall, pm.Loads, pm.LoadCombinations, pm.Studs, pm.Materials);

        // Verify equations and clause references exist in report
        Assert.Contains("CSA O86-20 Governing Design Equations", report);
        Assert.Contains("Clause 6.5.6.2.2", report); // Slenderness Cc
        Assert.Contains("Clause 6.5.6.2.3", report); // Factored compressive strength Fc & Pr
        Assert.Contains("Clause 6.5.6.2.4", report); // Column stability Kc
        Assert.Contains("Clause 6.5.6.2.5", report); // Size factor Kzc
        Assert.Contains("Stud Axial Capacities & Code Checks (Governing Combination Only)", report);
        Assert.Contains("Pf", report);
        Assert.Contains("Pr", report);
        Assert.Contains("D/C", report);
    }

    [Fact]
    public void Test_PdfReportExporter_GeneratesValidPdfFile()
    {
        var pm = new ProjectManager();
        var engine = new StudWallEngine();
        var wall = pm.Walls.First();

        engine.Calculate(wall, pm.Studs, pm.LoadCombinations);

        var tempPdf = Path.Combine(Path.GetTempPath(), $"test_report_{Guid.NewGuid()}.pdf");
        try
        {
            PdfReportExporter.ExportToPdf(
                tempPdf, pm.Project, wall, pm.Loads, pm.LoadCombinations, pm.Studs, pm.Materials);

            Assert.True(File.Exists(tempPdf));
            var fileInfo = new FileInfo(tempPdf);
            Assert.True(fileInfo.Length > 1000); // Verify non-empty PDF content
        }
        finally
        {
            if (File.Exists(tempPdf)) File.Delete(tempPdf);
        }
    }

    [Fact]
    public void Test_DesignResult_FormattedMember_NoDuplicatePlys()
    {
        // 1. Multi-ply stud whose name already contains "2-2x4"
        var multiPlyStud = new Stud { Id = 4, Name = "2-2x4 SPF No.1/No.2" };
        var res1 = new DesignResult { Stud = multiPlyStud, Plys = 2, Spacing = 406.0 };
        Assert.Equal("2-2x4 SPF No.1/No.2", res1.FormattedMember);
        Assert.Equal("2-2x4 SPF No.1/No.2 @ 406 mm o/c", res1.FormattedDescription);

        // Even if Plys is set to 1, it should never prepend "(1) 2-2x4" or "1-2-2x4"
        var res1b = new DesignResult { Stud = multiPlyStud, Plys = 1, Spacing = 406.0 };
        Assert.Equal("2-2x4 SPF No.1/No.2", res1b.FormattedMember);

        // 2. Single-ply stud "2x4 SPF" with Plys = 1
        var singleStud = new Stud { Id = 1, Name = "2x4 SPF No.1/No.2" };
        var res2 = new DesignResult { Stud = singleStud, Plys = 1, Spacing = 406.0 };
        Assert.Equal("2x4 SPF No.1/No.2", res2.FormattedMember);

        // 3. Single-ply stud "2x4 SPF" evaluated with Plys = 2
        var res3 = new DesignResult { Stud = singleStud, Plys = 2, Spacing = 406.0 };
        Assert.Equal("2-2x4 SPF No.1/No.2", res3.FormattedMember);

        // 4. Verify in generated report that "(1) 2-2x4" does not appear
        var pm = new ProjectManager();
        var engine = new StudWallEngine();
        var wall = pm.Walls.First();
        engine.Calculate(wall, pm.Studs, pm.LoadCombinations);
        string report = DesignReportGenerator.GenerateReport(pm.Project, wall, pm.Loads, pm.LoadCombinations, pm.Studs, pm.Materials);
        Assert.DoesNotContain("(1) 2-", report);
        Assert.DoesNotContain("(1) 3-", report);
    }

    [Fact]
    public void Test_DesignResult_PlysSection_FormattedSpacing_AndSelection()
    {
        var stud2x4 = new Stud { Id = 1, Name = "2x4 SPF No.1/No.2" };
        var stud2x6 = new Stud { Id = 2, Name = "2x6 SPF No.1/No.2" };
        var multi2x4 = new Stud { Id = 4, Name = "2-2x4 SPF No.1/No.2" };

        var ws = new WallStory { Id = 10 };

        var r1 = new DesignResult { WallStory = ws, Stud = stud2x4, Plys = 1, Spacing = 406.0, DcRatio = 0.98, WoodVolume = 1.135 };
        var r2 = new DesignResult { WallStory = ws, Stud = multi2x4, Plys = 2, Spacing = 406.0, DcRatio = 0.52, WoodVolume = 2.270 };
        var r3 = new DesignResult { WallStory = ws, Stud = stud2x6, Plys = 1, Spacing = 305.0, DcRatio = 0.65, WoodVolume = 1.830 };
        var r4 = new DesignResult { WallStory = ws, Stud = stud2x4, Plys = 1, Spacing = 610.0, DcRatio = 1.20, WoodVolume = 0.756 };

        ws.Results.AddRange(new[] { r1, r2, r3, r4 });

        // Verify PlysSection format (plys-section)
        Assert.Equal("1-2x4", r1.PlysSection);
        Assert.Equal("2-2x4", r2.PlysSection);
        Assert.Equal("1-2x6", r3.PlysSection);

        // Verify Spacing formatting
        Assert.Equal("16\"", r1.FormattedSpacing);
        Assert.Equal("16\"", r2.FormattedSpacing);
        Assert.Equal("12\"", r3.FormattedSpacing);
        Assert.Equal("24\"", r4.FormattedSpacing);

        // Verify initial final selection
        r1.IsFinal = true;
        Assert.True(r1.IsFinal);
        Assert.False(r2.IsFinal);

        // Changing final selection to r2 should automatically uncheck r1 for the same story
        r2.IsFinal = true;
        Assert.True(r2.IsFinal);
        Assert.False(r1.IsFinal);
    }

    [Fact]
    public void Test_ResultsViewModel_LevelFiltering_And_PassingOnlyFilter()
    {
        var wall = new Wall { Id = 1, Name = "Test Wall" };
        var s1 = new Story { Id = 1, Name = "Level 1" };
        var s2 = new Story { Id = 2, Name = "Level 2" };

        var ws1 = new WallStory { Id = 10, WallId = 1, StoryId = 1, Story = s1 };
        var ws2 = new WallStory { Id = 20, WallId = 1, StoryId = 2, Story = s2 };

        var stud = new Stud { Id = 1, Name = "2x4 SPF No.1/No.2" };

        // Level 1: 1 passing, 1 failing
        var r1_pass = new DesignResult { WallStoryId = 10, WallStory = ws1, Stud = stud, DcRatio = 0.85, WoodVolume = 1.0 };
        var r1_fail = new DesignResult { WallStoryId = 10, WallStory = ws1, Stud = stud, DcRatio = 1.25, WoodVolume = 0.5 };
        ws1.Results.AddRange(new[] { r1_pass, r1_fail });

        // Level 2: 2 passing
        var r2_pass1 = new DesignResult { WallStoryId = 20, WallStory = ws2, Stud = stud, DcRatio = 0.45, WoodVolume = 1.2 };
        var r2_pass2 = new DesignResult { WallStoryId = 20, WallStory = ws2, Stud = stud, DcRatio = 0.60, WoodVolume = 1.5 };
        ws2.Results.AddRange(new[] { r2_pass1, r2_pass2 });

        wall.Stories.AddRange(new[] { ws1, ws2 });

        bool reportInvoked = false;
        bool finalizedInvoked = false;

        var vm = new StudWalls.Desktop.ViewModels.ResultsViewModel(
            wall,
            new[] { s1, s2 },
            () => reportInvoked = true,
            () => finalizedInvoked = true);

        // 1. Initial state: All Levels, Passing Only = true
        // Total passing: r1_pass, r2_pass1, r2_pass2 = 3 results
        Assert.Equal(3, vm.FilteredResults.Count);
        Assert.Contains(r1_pass, vm.FilteredResults);
        Assert.Contains(r2_pass1, vm.FilteredResults);
        Assert.Contains(r2_pass2, vm.FilteredResults);
        Assert.DoesNotContain(r1_fail, vm.FilteredResults);

        // 2. Filter to Level 1 only
        var level1Option = vm.LevelFilterOptions.First(o => o.StoryId == 1);
        vm.SelectedLevelFilter = level1Option;
        Assert.Single(vm.FilteredResults);
        Assert.Contains(r1_pass, vm.FilteredResults);

        // 3. Filter to Level 1 with Passing Only = false (show all)
        vm.ShowPassingOnly = false;
        Assert.Equal(2, vm.FilteredResults.Count);
        Assert.Contains(r1_pass, vm.FilteredResults);
        Assert.Contains(r1_fail, vm.FilteredResults);

        // 4. Filter to Level 2
        var level2Option = vm.LevelFilterOptions.First(o => o.StoryId == 2);
        vm.SelectedLevelFilter = level2Option;
        Assert.Equal(2, vm.FilteredResults.Count);
        Assert.Contains(r2_pass1, vm.FilteredResults);
        Assert.Contains(r2_pass2, vm.FilteredResults);

        // 5. Test commands
        vm.GenerateReport();
        Assert.True(reportInvoked);

        vm.FinalizeResults();
        Assert.True(finalizedInvoked);
    }

    [Fact]
    public void Test_StudWallEngine_WithSizingCriteria_FiltersCorrectly()
    {
        var (_, walls, _, _, _, studs, combos) = SeedData.CreateStarterProject();
        var wall1 = walls.First();

        var engine = new StudWallEngine();

        // Constrain criteria strictly to 2x6, 16" spacing (406.4 mm), 1 ply only
        var criteria = new SizingCriteria
        {
            AllowedSections = new List<string> { "2x6" },
            AllowedSpacings = new List<double> { 406.0 },
            AllowedPlys = new List<int> { 1 },
            MaxTargetDcRatio = 0.95
        };

        engine.Calculate(wall1, studs, combos, criteria);

        foreach (var ws in wall1.Stories)
        {
            Assert.NotEmpty(ws.Results);
            foreach (var r in ws.Results)
            {
                // All evaluated results must be 2x6, 1-ply, ~406 mm spacing
                Assert.Contains("2x6", r.Stud?.Name);
                Assert.Equal(1, r.Plys);
                Assert.True(Math.Abs(r.Spacing - 406.0) < 5.0);
            }
        }
    }

    [Fact]
    public void Test_ProjectManager_SizingCriteria_SaveAndLoadSqlite()
    {
        var tempDb = Path.Combine(Path.GetTempPath(), $"test_criteria_{Guid.NewGuid()}.swproj");

        try
        {
            var pm = new ProjectManager();
            pm.SizingCriteria.AllowedSections = new List<string> { "2x8", "2x10" };
            pm.SizingCriteria.AllowedSpacings = new List<double> { 305.0 };
            pm.SizingCriteria.AllowedPlys = new List<int> { 2, 3 };
            pm.SizingCriteria.MaxTargetDcRatio = 0.85;

            pm.SaveToSqlite(tempDb);

            var pmReloaded = new ProjectManager();
            pmReloaded.LoadFromSqlite(tempDb);

            Assert.Equal(new[] { "2x8", "2x10" }, pmReloaded.SizingCriteria.AllowedSections);
            Assert.Equal(new[] { 305.0 }, pmReloaded.SizingCriteria.AllowedSpacings);
            Assert.Equal(new[] { 2, 3 }, pmReloaded.SizingCriteria.AllowedPlys);
            Assert.Equal(0.85, pmReloaded.SizingCriteria.MaxTargetDcRatio);
        }
        finally
        {
            if (File.Exists(tempDb)) File.Delete(tempDb);
        }
    }
}

