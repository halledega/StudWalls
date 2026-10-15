using StudWalls.Core.Enums;
using StudWalls.Core.Models;

namespace StudWalls.Core.Data;

/// <summary>
/// Provides default structural seed data matching CSA O86-20 tables, standard Canadian lumber catalogs,
/// and default project templates (wood materials, stud sections, load cases, load combinations, and stories).
/// </summary>
public static class SeedData
{
    /// <summary>
    /// Gets the standard catalog of visually graded sawn lumber materials per CSA O86-20 Table 6.3.1A.
    /// </summary>
    public static List<WoodMaterial> GetDefaultWoodMaterials()
    {
        return
        [
            new WoodMaterial { Id = 1, Name = "DFL SS", Category = "Joist and Plank", Species = "Douglas Fir-Larch", Grade = "SS", Fb = 16.5, Fv = 1.9, Fc = 19.0, Fcp = 7.0, Ft = 10.6, E = 12500, E05 = 8500, MaterialType = "Sawn" },
            new WoodMaterial { Id = 2, Name = "DFL No1/No2", Category = "Joist and Plank", Species = "Douglas Fir-Larch", Grade = "No1/No2", Fb = 10.0, Fv = 1.9, Fc = 14.0, Fcp = 7.0, Ft = 5.8, E = 11000, E05 = 7000, MaterialType = "Sawn" },
            new WoodMaterial { Id = 3, Name = "DFL Stud", Category = "Joist and Plank", Species = "Douglas Fir-Larch", Grade = "No2/Stud", Fb = 4.6, Fv = 1.6, Fc = 7.3, Fcp = 7.0, Ft = 2.1, E = 10000, E05 = 5500, MaterialType = "Sawn" },

            new WoodMaterial { Id = 4, Name = "HF SS", Category = "Joist and Plank", Species = "Hem-Fir", Grade = "SS", Fb = 16.0, Fv = 1.6, Fc = 17.6, Fcp = 4.6, Ft = 9.7, E = 12000, E05 = 8500, MaterialType = "Sawn" },
            new WoodMaterial { Id = 5, Name = "HF No1/No2", Category = "Joist and Plank", Species = "Hem-Fir", Grade = "No1/No2", Fb = 11.0, Fv = 1.6, Fc = 14.8, Fcp = 4.6, Ft = 6.2, E = 11000, E05 = 7500, MaterialType = "Sawn" },
            new WoodMaterial { Id = 6, Name = "HF Stud", Category = "Joist and Plank", Species = "Hem-Fir", Grade = "No2/Stud", Fb = 7.0, Fv = 1.6, Fc = 9.2, Fcp = 4.6, Ft = 3.2, E = 10000, E05 = 6000, MaterialType = "Sawn" },

            new WoodMaterial { Id = 7, Name = "SPF SS", Category = "Joist and Plank", Species = "Spruce-Pine-Fir", Grade = "SS", Fb = 16.5, Fv = 1.5, Fc = 14.5, Fcp = 5.3, Ft = 8.6, E = 10500, E05 = 7500, MaterialType = "Sawn" },
            new WoodMaterial { Id = 8, Name = "SPF No1/No2", Category = "Joist and Plank", Species = "Spruce-Pine-Fir", Grade = "No1/No2", Fb = 11.8, Fv = 1.5, Fc = 11.5, Fcp = 5.3, Ft = 5.5, E = 9500, E05 = 6500, MaterialType = "Sawn" },
            new WoodMaterial { Id = 9, Name = "SPF Stud", Category = "Joist and Plank", Species = "Spruce-Pine-Fir", Grade = "No2/Stud", Fb = 7.0, Fv = 1.5, Fc = 9.0, Fcp = 5.3, Ft = 3.2, E = 9000, E05 = 5500, MaterialType = "Sawn" },

            new WoodMaterial { Id = 10, Name = "Northern SS", Category = "Joist and Plank", Species = "Northern Species", Grade = "SS", Fb = 10.6, Fv = 1.3, Fc = 13.0, Fcp = 3.5, Ft = 6.2, E = 7500, E05 = 5500, MaterialType = "Sawn" },
            new WoodMaterial { Id = 11, Name = "Northern No1/No2", Category = "Joist and Plank", Species = "Northern Species", Grade = "No1/No2", Fb = 7.6, Fv = 1.3, Fc = 10.4, Fcp = 3.5, Ft = 4.0, E = 7000, E05 = 5000, MaterialType = "Sawn" },
            new WoodMaterial { Id = 12, Name = "Northern Stud", Category = "Joist and Plank", Species = "Northern Species", Grade = "No2/Stud", Fb = 4.5, Fv = 1.3, Fc = 5.2, Fcp = 3.5, Ft = 2.0, E = 6500, E05 = 4000, MaterialType = "Sawn" },
        ];
    }

    /// <summary>
    /// Gets default standard stud definitions for Canadian light-frame construction.
    /// </summary>
    public static List<Stud> GetDefaultStuds(List<WoodMaterial> materials)
    {
        var spf = materials.FirstOrDefault(m => m.Name == "SPF No1/No2") ?? materials.First();

        var studs = new List<Stud>
        {
            new() { Id = 1, Name = "2x4 SPF No.1/No.2", MaterialId = spf.Id, Material = spf, SectionId = 1, Section = new Section { Id = 1, Width = 38.1, Depth = 88.9, Plys = 1 } },
            new() { Id = 2, Name = "2x6 SPF No.1/No.2", MaterialId = spf.Id, Material = spf, SectionId = 2, Section = new Section { Id = 2, Width = 38.1, Depth = 139.7, Plys = 1 } },
            new() { Id = 3, Name = "2x8 SPF No.1/No.2", MaterialId = spf.Id, Material = spf, SectionId = 3, Section = new Section { Id = 3, Width = 38.1, Depth = 184.15, Plys = 1 } },
            new() { Id = 4, Name = "2-2x4 SPF No.1/No.2", MaterialId = spf.Id, Material = spf, SectionId = 4, Section = new Section { Id = 4, Width = 38.1, Depth = 88.9, Plys = 2 } },
            new() { Id = 5, Name = "2-2x6 SPF No.1/No.2", MaterialId = spf.Id, Material = spf, SectionId = 5, Section = new Section { Id = 5, Width = 38.1, Depth = 139.7, Plys = 2 } },
            new() { Id = 6, Name = "2-2x8 SPF No.1/No.2", MaterialId = spf.Id, Material = spf, SectionId = 6, Section = new Section { Id = 6, Width = 38.1, Depth = 184.15, Plys = 2 } },
        };

        return studs;
    }

    /// <summary>
    /// Gets default specified building loads per NBCC.
    /// </summary>
    public static List<Load> GetDefaultLoads()
    {
        return
        [
            new Load { Id = 1, Name = "Roof Dead", Case = LoadCase.Dead, Value = 0.75, LoadType = LoadType.Area },
            new Load { Id = 2, Name = "Roof Live", Case = LoadCase.Live, Value = 1.00, LoadType = LoadType.Area },
            new Load { Id = 3, Name = "Snow", Case = LoadCase.Snow, Value = 2.00, LoadType = LoadType.Area },
            new Load { Id = 4, Name = "Suite Dead", Case = LoadCase.Dead, Value = 1.70, LoadType = LoadType.Area },
            new Load { Id = 5, Name = "Suite Live", Case = LoadCase.Live, Value = 2.40, LoadType = LoadType.Area },
            new Load { Id = 6, Name = "Corridor Live", Case = LoadCase.Live, Value = 4.80, LoadType = LoadType.Area },
            new Load { Id = 7, Name = "Partitions", Case = LoadCase.Partition, Value = 1.00, LoadType = LoadType.Area },
        ];
    }

    /// <summary>
    /// Gets default building stories/levels.
    /// </summary>
    public static List<Story> GetDefaultStories()
    {
        return
        [
            new Story { Id = 1, Name = "Roof", Height = 3000.0, FloorThickness = 346.0 },
            new Story { Id = 2, Name = "6th", Height = 3000.0, FloorThickness = 359.0 },
            new Story { Id = 3, Name = "5th", Height = 3000.0, FloorThickness = 359.0 },
            new Story { Id = 4, Name = "4th", Height = 3000.0, FloorThickness = 359.0 },
            new Story { Id = 5, Name = "3rd", Height = 3000.0, FloorThickness = 359.0 },
            new Story { Id = 6, Name = "2nd", Height = 3000.0, FloorThickness = 359.0 },
        ];
    }

    /// <summary>
    /// Gets default factored Ultimate Limit State (ULS) load combinations per NBCC Table 4.1.3.2.A.
    /// </summary>
    public static List<LoadCombination> GetDefaultLoadCombinations(List<Load> loads)
    {
        var loadMap = loads.ToDictionary(l => l.Name);

        var combos = new List<LoadCombination>();

        // 1.4D (Dead load alone - Case 1)
        if (loadMap.TryGetValue("Roof Dead", out var roofDead))
        {
            var combo1 = new LoadCombination { Id = 1, Name = "1.4D (Roof)" };
            combo1.AddItem(roofDead, 1.40);
            combos.Add(combo1);
        }

        if (loadMap.TryGetValue("Suite Dead", out var suiteDead))
        {
            var combo2 = new LoadCombination { Id = 2, Name = "1.4D (Suite)" };
            combo2.AddItem(suiteDead, 1.40);
            combos.Add(combo2);
        }

        if (loadMap.TryGetValue("Partitions", out var partitions))
        {
            var combo3 = new LoadCombination { Id = 3, Name = "1.4D (Partitions)" };
            combo3.AddItem(partitions, 1.40);
            combos.Add(combo3);
        }

        // 1.25D + 1.5L (Live load principal - Case 2)
        if (roofDead != null && loadMap.TryGetValue("Roof Live", out var roofLive))
        {
            var combo4 = new LoadCombination { Id = 4, Name = "1.25D + 1.5L (Roof)" };
            combo4.AddItem(roofDead, 1.25);
            combo4.AddItem(roofLive, 1.50);
            combos.Add(combo4);
        }

        if (suiteDead != null && loadMap.TryGetValue("Suite Live", out var suiteLive))
        {
            var combo5 = new LoadCombination { Id = 5, Name = "1.25D + 1.5L (Suite)" };
            combo5.AddItem(suiteDead, 1.25);
            combo5.AddItem(suiteLive, 1.50);
            combos.Add(combo5);
        }

        // 1.25D + 1.5S (Snow load principal - Case 3)
        if (roofDead != null && loadMap.TryGetValue("Snow", out var snow))
        {
            var combo6 = new LoadCombination { Id = 6, Name = "1.25D + 1.5S" };
            combo6.AddItem(roofDead, 1.25);
            combo6.AddItem(snow, 1.50);
            combos.Add(combo6);

            var combo7 = new LoadCombination { Id = 7, Name = "0.9D + 1.5S" };
            combo7.AddItem(roofDead, 0.90);
            combo7.AddItem(snow, 1.50);
            combos.Add(combo7);
        }

        return combos;
    }

    /// <summary>
    /// Creates a complete starter project dataset with walls, stories, and assigned loads.
    /// </summary>
    public static (ProjectInfo Project, List<Wall> Walls, List<Story> Stories, List<Load> Loads, List<WoodMaterial> Materials, List<Stud> Studs, List<LoadCombination> Combos) CreateStarterProject()
    {
        var project = new ProjectInfo
        {
            ProjectNumber = "PRJ-2026-001",
            ProjectName = "Residential Stud Wall Design",
            ProjectAddress1 = "100 Pine Street",
            ProjectAddress2 = "Vancouver, BC",
            Engineer = "Structural Engineer, P.Eng.",
            Date = DateTime.Today,
            UnitSystem = UnitSystem.Metric
        };

        var materials = GetDefaultWoodMaterials();
        var studs = GetDefaultStuds(materials);
        var loads = GetDefaultLoads();
        var stories = GetDefaultStories(); // Roof, 6th, 5th, 4th, 3rd, 2nd
        var combos = GetDefaultLoadCombinations(loads);

        // Wall 1: 3 stories (Roof, 6th, 5th)
        var wall1 = new Wall
        {
            Id = 1,
            Name = "Wall 1",
            Length = 5000.0,
            SelfWeight = 0.50,
            PlanX = 1000.0,
            PlanY = 1500.0,
            RotationDegrees = 0.0
        };

        var wall1Stories = stories.Take(3).ToList();
        for (int i = 0; i < wall1Stories.Count; i++)
        {
            var ws = new WallStory
            {
                Id = i + 1,
                WallId = wall1.Id,
                Wall = wall1,
                StoryId = wall1Stories[i].Id,
                Story = wall1Stories[i],
                TribWidthLeft = 1000.0,
                TribWidthRight = 1500.0,
                LuDepth = wall1Stories[i].Height,
                LuWidth = 152.0
            };

            if (wall1Stories[i].Name == "Roof")
            {
                ws.LoadsLeft = loads.Where(l => l.Name is "Roof Dead" or "Roof Live" or "Snow").ToList();
                ws.LoadsRight = loads.Where(l => l.Name is "Roof Dead" or "Roof Live" or "Snow").ToList();
            }
            else
            {
                ws.LoadsLeft = loads.Where(l => l.Name is "Suite Dead" or "Suite Live" or "Partitions").ToList();
                ws.LoadsRight = loads.Where(l => l.Name is "Suite Dead" or "Suite Live" or "Partitions").ToList();
            }

            wall1.Stories.Add(ws);
        }

        // Wall 2: All 6 stories
        var wall2 = new Wall
        {
            Id = 2,
            Name = "Wall 2",
            Length = 6000.0,
            SelfWeight = 0.50,
            PlanX = 1000.0,
            PlanY = 4000.0,
            RotationDegrees = 0.0
        };

        for (int i = 0; i < stories.Count; i++)
        {
            var ws = new WallStory
            {
                Id = i + 10,
                WallId = wall2.Id,
                Wall = wall2,
                StoryId = stories[i].Id,
                Story = stories[i],
                TribWidthLeft = 1200.0,
                TribWidthRight = 1800.0,
                LuDepth = stories[i].Height,
                LuWidth = 152.0
            };

            if (stories[i].Name == "Roof")
            {
                ws.LoadsLeft = loads.Where(l => l.Name is "Roof Dead" or "Roof Live" or "Snow").ToList();
                ws.LoadsRight = loads.Where(l => l.Name is "Roof Dead" or "Roof Live" or "Snow").ToList();
            }
            else
            {
                ws.LoadsLeft = loads.Where(l => l.Name is "Suite Dead" or "Suite Live" or "Partitions").ToList();
                ws.LoadsRight = loads.Where(l => l.Name is "Suite Dead" or "Suite Live" or "Partitions").ToList();
            }

            wall2.Stories.Add(ws);
        }

        return (project, [wall1, wall2], stories, loads, materials, studs, combos);
    }
}
