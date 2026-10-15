using System.Text.Json;
using Microsoft.Data.Sqlite;
using StudWalls.Core.Enums;
using StudWalls.Core.Models;

namespace StudWalls.Core.Data;

/// <summary>
/// Manages the dual-database architecture, project lifecycle (New, Open, Save, Save As),
/// and file persistence for the StudWalls structural engineering application.
/// 
/// Supported storage formats:
/// 1. Native SQLite Database (.swproj): Full transactional integrity, relational tables, ACID safe.
/// 2. Human-Readable JSON (.json): Plain text export/import for git-based version control diffing.
/// </summary>
public class ProjectManager
{
    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        WriteIndented = true,
        PropertyNameCaseInsensitive = true,
        ReferenceHandler = System.Text.Json.Serialization.ReferenceHandler.IgnoreCycles
    };

    public ProjectInfo Project { get; set; } = new();
    public List<Wall> Walls { get; set; } = new();
    public List<Story> Stories { get; set; } = new();
    public List<Load> Loads { get; set; } = new();
    public List<WoodMaterial> Materials { get; set; } = new();
    public List<Stud> Studs { get; set; } = new();
    public List<LoadCombination> LoadCombinations { get; set; } = new();

    /// <summary>
    /// User and design preferences governing defaults, design constraints, and units.
    /// </summary>
    public AppPreferences Preferences { get; set; } = new();

    /// <summary>
    /// Framing criteria and candidate search space for automated stud sizing.
    /// </summary>
    public SizingCriteria SizingCriteria { get; set; } = new();

    /// <summary>
    /// File path of the currently opened or saved project file (.swproj or .json).
    /// </summary>
    public string? CurrentFilePath { get; set; }

    /// <summary>
    /// Indicates whether the active project has unsaved modifications.
    /// </summary>
    public bool IsDirty { get; set; }

    public ProjectManager()
    {
        CreateNewProject();
    }

    /// <summary>
    /// Creates a clean, fresh project seeded with default materials, studs, stories, and sample walls.
    /// </summary>
    public void CreateNewProject()
    {
        var (project, walls, stories, loads, materials, studs, combos) = SeedData.CreateStarterProject();

        Project = project;
        Walls = walls;
        Stories = stories;
        Loads = loads;
        Materials = materials;
        Studs = studs;
        LoadCombinations = combos;
        Preferences = new AppPreferences();
        SizingCriteria = new SizingCriteria();
        CurrentFilePath = null;
        IsDirty = false;
    }

    /// <summary>
    /// Saves the current project to disk. If filePath is omitted, overwrites CurrentFilePath.
    /// Supports .swproj (SQLite) and .json formats.
    /// </summary>
    public void SaveProject(string? filePath = null)
    {
        var targetPath = filePath ?? CurrentFilePath;
        if (string.IsNullOrWhiteSpace(targetPath))
        {
            throw new InvalidOperationException("No file path specified for saving project.");
        }

        if (targetPath.EndsWith(".json", StringComparison.OrdinalIgnoreCase))
        {
            ExportToJson(targetPath);
        }
        else
        {
            SaveToSqlite(targetPath);
        }

        CurrentFilePath = targetPath;
        IsDirty = false;
    }

    /// <summary>
    /// Opens and loads a project from disk (.swproj SQLite database or .json file).
    /// </summary>
    public void OpenProject(string filePath)
    {
        if (!File.Exists(filePath))
        {
            throw new FileNotFoundException($"Project file not found: {filePath}");
        }

        if (filePath.EndsWith(".json", StringComparison.OrdinalIgnoreCase))
        {
            ImportFromJson(filePath);
        }
        else
        {
            LoadFromSqlite(filePath);
        }

        CurrentFilePath = filePath;
        IsDirty = false;
    }

    /// <summary>
    /// Saves the complete project state into a standalone SQLite database file (.swproj).
    /// </summary>
    public void SaveToSqlite(string filePath)
    {
        // If file exists, delete or overwrite atomically
        if (File.Exists(filePath))
        {
            File.Delete(filePath);
        }

        var connectionString = new SqliteConnectionStringBuilder
        {
            DataSource = filePath,
            Mode = SqliteOpenMode.ReadWriteCreate
        }.ToString();

        using var connection = new SqliteConnection(connectionString);
        connection.Open();

        using var transaction = connection.BeginTransaction();

        // 1. Create database schema
        CreateSqliteSchema(connection);

        // 2. Insert ProjectInfo
        using (var cmd = connection.CreateCommand())
        {
            cmd.CommandText = @"
                INSERT INTO project_info (project_number, project_name, address1, address2, engineer, date, unit_system)
                VALUES (@num, @name, @a1, @a2, @eng, @dt, @unit);";
            cmd.Parameters.AddWithValue("@num", Project.ProjectNumber);
            cmd.Parameters.AddWithValue("@name", Project.ProjectName);
            cmd.Parameters.AddWithValue("@a1", Project.ProjectAddress1);
            cmd.Parameters.AddWithValue("@a2", Project.ProjectAddress2);
            cmd.Parameters.AddWithValue("@eng", Project.Engineer);
            cmd.Parameters.AddWithValue("@dt", Project.Date.ToString("yyyy-MM-dd"));
            cmd.Parameters.AddWithValue("@unit", (int)Project.UnitSystem);
            cmd.ExecuteNonQuery();
        }

        // 2b. Insert Preferences
        using (var cmd = connection.CreateCommand())
        {
            cmd.CommandText = @"
                INSERT INTO preferences (id, unit_system, default_engineer, default_company, default_story_height, default_wall_self_weight, default_stud_spacing, max_allowable_cc, max_target_dc_ratio, default_material_name, service_condition_factor)
                VALUES (1, @unit, @eng, @comp, @ht, @sw, @spc, @cc, @dc, @mat, @ks);";
            cmd.Parameters.AddWithValue("@unit", (int)Preferences.UnitSystem);
            cmd.Parameters.AddWithValue("@eng", Preferences.DefaultEngineer);
            cmd.Parameters.AddWithValue("@comp", Preferences.DefaultCompany);
            cmd.Parameters.AddWithValue("@ht", Preferences.DefaultStoryHeight);
            cmd.Parameters.AddWithValue("@sw", Preferences.DefaultWallSelfWeight);
            cmd.Parameters.AddWithValue("@spc", Preferences.DefaultStudSpacing);
            cmd.Parameters.AddWithValue("@cc", Preferences.MaxAllowableCc);
            cmd.Parameters.AddWithValue("@dc", Preferences.MaxTargetDcRatio);
            cmd.Parameters.AddWithValue("@mat", Preferences.DefaultMaterialName);
            cmd.Parameters.AddWithValue("@ks", Preferences.DefaultServiceConditionFactor);
            cmd.ExecuteNonQuery();
        }

        // 2c. Insert SizingCriteria
        using (var cmd = connection.CreateCommand())
        {
            cmd.CommandText = @"
                INSERT INTO sizing_criteria (id, sections, spacings, material_ids, plys, max_target_dc)
                VALUES (1, @sec, @spc, @mat, @ply, @dc);";
            cmd.Parameters.AddWithValue("@sec", string.Join(",", SizingCriteria.AllowedSections));
            cmd.Parameters.AddWithValue("@spc", string.Join(",", SizingCriteria.AllowedSpacings));
            cmd.Parameters.AddWithValue("@mat", string.Join(",", SizingCriteria.AllowedMaterialIds));
            cmd.Parameters.AddWithValue("@ply", string.Join(",", SizingCriteria.AllowedPlys));
            cmd.Parameters.AddWithValue("@dc", SizingCriteria.MaxTargetDcRatio);
            cmd.ExecuteNonQuery();
        }

        // 3. Insert Materials
        foreach (var mat in Materials)
        {
            using var cmd = connection.CreateCommand();
            cmd.CommandText = @"
                INSERT INTO wood_materials (id, name, category, species, grade, fb, fv, fc, fcp, ft, e, e05, material_type)
                VALUES (@id, @name, @cat, @spc, @grd, @fb, @fv, @fc, @fcp, @ft, @e, @e05, @type);";
            cmd.Parameters.AddWithValue("@id", mat.Id);
            cmd.Parameters.AddWithValue("@name", mat.Name);
            cmd.Parameters.AddWithValue("@cat", mat.Category);
            cmd.Parameters.AddWithValue("@spc", mat.Species);
            cmd.Parameters.AddWithValue("@grd", mat.Grade);
            cmd.Parameters.AddWithValue("@fb", mat.Fb);
            cmd.Parameters.AddWithValue("@fv", mat.Fv);
            cmd.Parameters.AddWithValue("@fc", mat.Fc);
            cmd.Parameters.AddWithValue("@fcp", mat.Fcp);
            cmd.Parameters.AddWithValue("@ft", mat.Ft);
            cmd.Parameters.AddWithValue("@e", mat.E);
            cmd.Parameters.AddWithValue("@e05", mat.E05);
            cmd.Parameters.AddWithValue("@type", mat.MaterialType);
            cmd.ExecuteNonQuery();
        }

        // 4. Insert Studs & Sections
        foreach (var stud in Studs)
        {
            using var cmd = connection.CreateCommand();
            cmd.CommandText = @"
                INSERT INTO studs (id, name, section_width, section_depth, section_plys, material_id)
                VALUES (@id, @name, @w, @d, @plys, @matId);";
            cmd.Parameters.AddWithValue("@id", stud.Id);
            cmd.Parameters.AddWithValue("@name", stud.Name);
            cmd.Parameters.AddWithValue("@w", stud.Section.Width);
            cmd.Parameters.AddWithValue("@d", stud.Section.Depth);
            cmd.Parameters.AddWithValue("@plys", stud.Section.Plys);
            cmd.Parameters.AddWithValue("@matId", stud.MaterialId);
            cmd.ExecuteNonQuery();
        }

        // 5. Insert Stories
        foreach (var s in Stories)
        {
            using var cmd = connection.CreateCommand();
            cmd.CommandText = "INSERT INTO stories (id, name, height, floor_thickness) VALUES (@id, @name, @h, @ft);";
            cmd.Parameters.AddWithValue("@id", s.Id);
            cmd.Parameters.AddWithValue("@name", s.Name);
            cmd.Parameters.AddWithValue("@h", s.Height);
            cmd.Parameters.AddWithValue("@ft", s.FloorThickness);
            cmd.ExecuteNonQuery();
        }

        // 6. Insert Loads
        foreach (var l in Loads)
        {
            using var cmd = connection.CreateCommand();
            cmd.CommandText = "INSERT INTO loads (id, name, load_case, value, load_type) VALUES (@id, @name, @case, @val, @type);";
            cmd.Parameters.AddWithValue("@id", l.Id);
            cmd.Parameters.AddWithValue("@name", l.Name);
            cmd.Parameters.AddWithValue("@case", (int)l.Case);
            cmd.Parameters.AddWithValue("@val", l.Value);
            cmd.Parameters.AddWithValue("@type", (int)l.LoadType);
            cmd.ExecuteNonQuery();
        }

        // 7. Insert Load Combinations
        foreach (var c in LoadCombinations)
        {
            using var cmd = connection.CreateCommand();
            cmd.CommandText = "INSERT INTO load_combinations (id, name) VALUES (@id, @name);";
            cmd.Parameters.AddWithValue("@id", c.Id);
            cmd.Parameters.AddWithValue("@name", c.Name);
            cmd.ExecuteNonQuery();

            foreach (var item in c.Items)
            {
                using var itemCmd = connection.CreateCommand();
                itemCmd.CommandText = "INSERT INTO load_combination_items (combo_id, load_id, factor) VALUES (@cid, @lid, @factor);";
                itemCmd.Parameters.AddWithValue("@cid", c.Id);
                itemCmd.Parameters.AddWithValue("@lid", item.LoadId);
                itemCmd.Parameters.AddWithValue("@factor", item.Factor);
                itemCmd.ExecuteNonQuery();
            }
        }

        // 8. Insert Walls & WallStories
        foreach (var w in Walls)
        {
            using var cmd = connection.CreateCommand();
            cmd.CommandText = @"
                INSERT INTO walls (id, name, length, self_weight, plan_x, plan_y, rotation)
                VALUES (@id, @name, @len, @sw, @x, @y, @rot);";
            cmd.Parameters.AddWithValue("@id", w.Id);
            cmd.Parameters.AddWithValue("@name", w.Name);
            cmd.Parameters.AddWithValue("@len", w.Length);
            cmd.Parameters.AddWithValue("@sw", w.SelfWeight);
            cmd.Parameters.AddWithValue("@x", w.PlanX);
            cmd.Parameters.AddWithValue("@y", w.PlanY);
            cmd.Parameters.AddWithValue("@rot", w.RotationDegrees);
            cmd.ExecuteNonQuery();

            foreach (var ws in w.Stories)
            {
                using var wsCmd = connection.CreateCommand();
                wsCmd.CommandText = @"
                    INSERT INTO wall_stories (id, wall_id, story_id, trib_left, trib_right, lu_width, lu_depth)
                    VALUES (@id, @wid, @sid, @tl, @tr, @luw, @lud);";
                wsCmd.Parameters.AddWithValue("@id", ws.Id);
                wsCmd.Parameters.AddWithValue("@wid", w.Id);
                wsCmd.Parameters.AddWithValue("@sid", ws.StoryId);
                wsCmd.Parameters.AddWithValue("@tl", ws.TribWidthLeft);
                wsCmd.Parameters.AddWithValue("@tr", ws.TribWidthRight);
                wsCmd.Parameters.AddWithValue("@luw", ws.LuWidth);
                wsCmd.Parameters.AddWithValue("@lud", ws.LuDepth);
                wsCmd.ExecuteNonQuery();

                // Insert load links
                foreach (var l in ws.LoadsLeft)
                {
                    using var linkCmd = connection.CreateCommand();
                    linkCmd.CommandText = "INSERT INTO wall_story_loads (wall_story_id, load_id, side) VALUES (@wsid, @lid, 'Left');";
                    linkCmd.Parameters.AddWithValue("@wsid", ws.Id);
                    linkCmd.Parameters.AddWithValue("@lid", l.Id);
                    linkCmd.ExecuteNonQuery();
                }

                foreach (var l in ws.LoadsRight)
                {
                    using var linkCmd = connection.CreateCommand();
                    linkCmd.CommandText = "INSERT INTO wall_story_loads (wall_story_id, load_id, side) VALUES (@wsid, @lid, 'Right');";
                    linkCmd.Parameters.AddWithValue("@wsid", ws.Id);
                    linkCmd.Parameters.AddWithValue("@lid", l.Id);
                    linkCmd.ExecuteNonQuery();
                }

                // Insert results
                foreach (var res in ws.Results)
                {
                    using var resCmd = connection.CreateCommand();
                    resCmd.CommandText = @"
                        INSERT INTO results (wall_story_id, stud_id, spacing, plys, dc_ratio, governing_combo, pf, pr, kd, kh, kse, ksc, kt, kzc, kc, cc, fc, wood_volume, is_final)
                        VALUES (@wsid, @studId, @spacing, @plys, @dc, @combo, @pf, @pr, @kd, @kh, @kse, @ksc, @kt, @kzc, @kc, @cc, @fc, @vol, @isFinal);";
                    resCmd.Parameters.AddWithValue("@wsid", ws.Id);
                    resCmd.Parameters.AddWithValue("@studId", res.StudId);
                    resCmd.Parameters.AddWithValue("@spacing", res.Spacing);
                    resCmd.Parameters.AddWithValue("@plys", res.Plys);
                    resCmd.Parameters.AddWithValue("@dc", res.DcRatio);
                    resCmd.Parameters.AddWithValue("@combo", res.GoverningCombo);
                    resCmd.Parameters.AddWithValue("@pf", res.Pf);
                    resCmd.Parameters.AddWithValue("@pr", res.Pr);
                    resCmd.Parameters.AddWithValue("@kd", res.Kd);
                    resCmd.Parameters.AddWithValue("@kh", res.Kh);
                    resCmd.Parameters.AddWithValue("@kse", res.Kse);
                    resCmd.Parameters.AddWithValue("@ksc", res.Ksc);
                    resCmd.Parameters.AddWithValue("@kt", res.Kt);
                    resCmd.Parameters.AddWithValue("@kzc", res.Kzc);
                    resCmd.Parameters.AddWithValue("@kc", res.Kc);
                    resCmd.Parameters.AddWithValue("@cc", res.Cc);
                    resCmd.Parameters.AddWithValue("@fc", res.Fc);
                    resCmd.Parameters.AddWithValue("@vol", res.WoodVolume);
                    resCmd.Parameters.AddWithValue("@isFinal", res.IsFinal ? 1 : 0);
                    resCmd.ExecuteNonQuery();
                }
            }
        }

        transaction.Commit();
    }

    /// <summary>
    /// Loads an entire project from a .swproj SQLite database file.
    /// </summary>
    public void LoadFromSqlite(string filePath)
    {
        var connectionString = new SqliteConnectionStringBuilder
        {
            DataSource = filePath,
            Mode = SqliteOpenMode.ReadOnly
        }.ToString();

        using var connection = new SqliteConnection(connectionString);
        connection.Open();

        // 1. Load ProjectInfo
        using (var cmd = connection.CreateCommand())
        {
            cmd.CommandText = "SELECT project_number, project_name, address1, address2, engineer, date, unit_system FROM project_info LIMIT 1;";
            using var reader = cmd.ExecuteReader();
            if (reader.Read())
            {
                Project = new ProjectInfo
                {
                    ProjectNumber = reader.GetString(0),
                    ProjectName = reader.GetString(1),
                    ProjectAddress1 = reader.IsDBNull(2) ? "" : reader.GetString(2),
                    ProjectAddress2 = reader.IsDBNull(3) ? "" : reader.GetString(3),
                    Engineer = reader.GetString(4),
                    Date = DateTime.TryParse(reader.GetString(5), out var d) ? d : DateTime.Today,
                    UnitSystem = (UnitSystem)reader.GetInt32(6)
                };
            }
        }

        // 1b. Load Preferences
        try
        {
            using var cmd = connection.CreateCommand();
            cmd.CommandText = "SELECT unit_system, default_engineer, default_company, default_story_height, default_wall_self_weight, default_stud_spacing, max_allowable_cc, max_target_dc_ratio, default_material_name, service_condition_factor FROM preferences WHERE id = 1;";
            using var reader = cmd.ExecuteReader();
            if (reader.Read())
            {
                Preferences = new AppPreferences
                {
                    UnitSystem = (UnitSystem)reader.GetInt32(0),
                    DefaultEngineer = reader.IsDBNull(1) ? "Engineer, P.Eng." : reader.GetString(1),
                    DefaultCompany = reader.IsDBNull(2) ? "Structural Consulting Engineers" : reader.GetString(2),
                    DefaultStoryHeight = reader.GetDouble(3),
                    DefaultWallSelfWeight = reader.GetDouble(4),
                    DefaultStudSpacing = reader.GetDouble(5),
                    MaxAllowableCc = reader.GetDouble(6),
                    MaxTargetDcRatio = reader.GetDouble(7),
                    DefaultMaterialName = reader.IsDBNull(8) ? "SPF No.1/No.2" : reader.GetString(8),
                    DefaultServiceConditionFactor = reader.GetDouble(9)
                };
            }
        }
        catch
        {
            Preferences = new AppPreferences();
        }

        // 1c. Load SizingCriteria
        try
        {
            using var cmd = connection.CreateCommand();
            cmd.CommandText = "SELECT sections, spacings, material_ids, plys, max_target_dc FROM sizing_criteria WHERE id = 1;";
            using var reader = cmd.ExecuteReader();
            if (reader.Read())
            {
                var secStr = reader.IsDBNull(0) ? "" : reader.GetString(0);
                var spcStr = reader.IsDBNull(1) ? "" : reader.GetString(1);
                var matStr = reader.IsDBNull(2) ? "" : reader.GetString(2);
                var plyStr = reader.IsDBNull(3) ? "" : reader.GetString(3);
                var dc = reader.IsDBNull(4) ? 1.0 : reader.GetDouble(4);

                SizingCriteria = new SizingCriteria
                {
                    AllowedSections = secStr.Split(',', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries).ToList(),
                    AllowedSpacings = spcStr.Split(',', StringSplitOptions.RemoveEmptyEntries).Select(s => double.TryParse(s, out var v) ? v : 406.0).ToList(),
                    AllowedMaterialIds = matStr.Split(',', StringSplitOptions.RemoveEmptyEntries).Select(s => int.TryParse(s, out var v) ? v : 0).Where(v => v > 0).ToList(),
                    AllowedPlys = plyStr.Split(',', StringSplitOptions.RemoveEmptyEntries).Select(s => int.TryParse(s, out var v) ? v : 1).ToList(),
                    MaxTargetDcRatio = dc
                };
            }
        }
        catch
        {
            SizingCriteria = new SizingCriteria();
        }

        // 2. Load Materials
        var materials = new List<WoodMaterial>();
        using (var cmd = connection.CreateCommand())
        {
            cmd.CommandText = "SELECT id, name, category, species, grade, fb, fv, fc, fcp, ft, e, e05, material_type FROM wood_materials;";
            using var reader = cmd.ExecuteReader();
            while (reader.Read())
            {
                materials.Add(new WoodMaterial
                {
                    Id = reader.GetInt32(0),
                    Name = reader.GetString(1),
                    Category = reader.GetString(2),
                    Species = reader.GetString(3),
                    Grade = reader.GetString(4),
                    Fb = reader.GetDouble(5),
                    Fv = reader.GetDouble(6),
                    Fc = reader.GetDouble(7),
                    Fcp = reader.GetDouble(8),
                    Ft = reader.GetDouble(9),
                    E = reader.GetDouble(10),
                    E05 = reader.GetDouble(11),
                    MaterialType = reader.GetString(12)
                });
            }
        }
        Materials = materials;
        var matMap = materials.ToDictionary(m => m.Id);

        // 3. Load Studs
        var studs = new List<Stud>();
        using (var cmd = connection.CreateCommand())
        {
            cmd.CommandText = "SELECT id, name, section_width, section_depth, section_plys, material_id FROM studs;";
            using var reader = cmd.ExecuteReader();
            while (reader.Read())
            {
                int matId = reader.GetInt32(5);
                var mat = matMap.GetValueOrDefault(matId) ?? materials.First();
                studs.Add(new Stud
                {
                    Id = reader.GetInt32(0),
                    Name = reader.GetString(1),
                    Section = new Section
                    {
                        Id = reader.GetInt32(0),
                        Width = reader.GetDouble(2),
                        Depth = reader.GetDouble(3),
                        Plys = reader.GetInt32(4)
                    },
                    MaterialId = matId,
                    Material = mat
                });
            }
        }
        Studs = studs;
        var studMap = studs.ToDictionary(s => s.Id);

        // 4. Load Stories
        var stories = new List<Story>();
        using (var cmd = connection.CreateCommand())
        {
            cmd.CommandText = "SELECT id, name, height, floor_thickness FROM stories;";
            using var reader = cmd.ExecuteReader();
            while (reader.Read())
            {
                stories.Add(new Story
                {
                    Id = reader.GetInt32(0),
                    Name = reader.GetString(1),
                    Height = reader.GetDouble(2),
                    FloorThickness = reader.GetDouble(3)
                });
            }
        }
        Stories = stories;
        var storyMap = stories.ToDictionary(s => s.Id);

        // 5. Load Loads
        var loads = new List<Load>();
        using (var cmd = connection.CreateCommand())
        {
            cmd.CommandText = "SELECT id, name, load_case, value, load_type FROM loads;";
            using var reader = cmd.ExecuteReader();
            while (reader.Read())
            {
                loads.Add(new Load
                {
                    Id = reader.GetInt32(0),
                    Name = reader.GetString(1),
                    Case = (LoadCase)reader.GetInt32(2),
                    Value = reader.GetDouble(3),
                    LoadType = (LoadType)reader.GetInt32(4)
                });
            }
        }
        Loads = loads;
        var loadMap = loads.ToDictionary(l => l.Id);

        // 6. Load Combinations
        var combos = new List<LoadCombination>();
        using (var cmd = connection.CreateCommand())
        {
            cmd.CommandText = "SELECT id, name FROM load_combinations;";
            using var reader = cmd.ExecuteReader();
            while (reader.Read())
            {
                combos.Add(new LoadCombination
                {
                    Id = reader.GetInt32(0),
                    Name = reader.GetString(1)
                });
            }
        }
        var comboMap = combos.ToDictionary(c => c.Id);

        using (var cmd = connection.CreateCommand())
        {
            cmd.CommandText = "SELECT combo_id, load_id, factor FROM load_combination_items;";
            using var reader = cmd.ExecuteReader();
            while (reader.Read())
            {
                int cid = reader.GetInt32(0);
                int lid = reader.GetInt32(1);
                double factor = reader.GetDouble(2);
                if (comboMap.TryGetValue(cid, out var combo) && loadMap.TryGetValue(lid, out var load))
                {
                    combo.Items.Add(new LoadCombinationItem
                    {
                        LoadCombinationId = cid,
                        LoadCombination = combo,
                        LoadId = lid,
                        Load = load,
                        Factor = factor
                    });
                }
            }
        }
        LoadCombinations = combos;

        // 7. Load Walls & WallStories
        var walls = new List<Wall>();
        using (var cmd = connection.CreateCommand())
        {
            cmd.CommandText = "SELECT id, name, length, self_weight, plan_x, plan_y, rotation FROM walls;";
            using var reader = cmd.ExecuteReader();
            while (reader.Read())
            {
                walls.Add(new Wall
                {
                    Id = reader.GetInt32(0),
                    Name = reader.GetString(1),
                    Length = reader.GetDouble(2),
                    SelfWeight = reader.GetDouble(3),
                    PlanX = reader.GetDouble(4),
                    PlanY = reader.GetDouble(5),
                    RotationDegrees = reader.GetDouble(6)
                });
            }
        }
        var wallMap = walls.ToDictionary(w => w.Id);

        var wallStories = new List<WallStory>();
        using (var cmd = connection.CreateCommand())
        {
            cmd.CommandText = "SELECT id, wall_id, story_id, trib_left, trib_right, lu_width, lu_depth FROM wall_stories;";
            using var reader = cmd.ExecuteReader();
            while (reader.Read())
            {
                int wid = reader.GetInt32(1);
                int sid = reader.GetInt32(2);
                var wall = wallMap.GetValueOrDefault(wid);
                var story = storyMap.GetValueOrDefault(sid);

                var ws = new WallStory
                {
                    Id = reader.GetInt32(0),
                    WallId = wid,
                    Wall = wall,
                    StoryId = sid,
                    Story = story,
                    TribWidthLeft = reader.GetDouble(3),
                    TribWidthRight = reader.GetDouble(4),
                    LuWidth = reader.GetDouble(5),
                    LuDepth = reader.GetDouble(6)
                };

                wall?.Stories.Add(ws);
                wallStories.Add(ws);
            }
        }
        var wsMap = wallStories.ToDictionary(ws => ws.Id);

        // Load load associations
        using (var cmd = connection.CreateCommand())
        {
            cmd.CommandText = "SELECT wall_story_id, load_id, side FROM wall_story_loads;";
            using var reader = cmd.ExecuteReader();
            while (reader.Read())
            {
                int wsid = reader.GetInt32(0);
                int lid = reader.GetInt32(1);
                string side = reader.GetString(2);

                if (wsMap.TryGetValue(wsid, out var ws) && loadMap.TryGetValue(lid, out var load))
                {
                    if (side.Equals("Left", StringComparison.OrdinalIgnoreCase))
                        ws.LoadsLeft.Add(load);
                    else
                        ws.LoadsRight.Add(load);
                }
            }
        }

        // Load Results
        using (var cmd = connection.CreateCommand())
        {
            cmd.CommandText = @"
                SELECT wall_story_id, stud_id, spacing, plys, dc_ratio, governing_combo, pf, pr, kd, kh, kse, ksc, kt, kzc, kc, cc, fc, wood_volume, is_final
                FROM results;";
            using var reader = cmd.ExecuteReader();
            while (reader.Read())
            {
                int wsid = reader.GetInt32(0);
                int studId = reader.GetInt32(1);

                if (wsMap.TryGetValue(wsid, out var ws) && studMap.TryGetValue(studId, out var stud))
                {
                    ws.Results.Add(new DesignResult
                    {
                        WallStoryId = wsid,
                        WallStory = ws,
                        StudId = studId,
                        Stud = stud,
                        Spacing = reader.GetDouble(2),
                        Plys = reader.GetInt32(3),
                        DcRatio = reader.GetDouble(4),
                        GoverningCombo = reader.GetString(5),
                        Pf = reader.GetDouble(6),
                        Pr = reader.GetDouble(7),
                        Kd = reader.GetDouble(8),
                        Kh = reader.GetDouble(9),
                        Kse = reader.GetDouble(10),
                        Ksc = reader.GetDouble(11),
                        Kt = reader.GetDouble(12),
                        Kzc = reader.GetDouble(13),
                        Kc = reader.GetDouble(14),
                        Cc = reader.GetDouble(15),
                        Fc = reader.GetDouble(16),
                        WoodVolume = reader.GetDouble(17),
                        IsFinal = reader.GetInt32(18) == 1
                    });
                }
            }
        }

        Walls = walls;
    }

    private static void CreateSqliteSchema(SqliteConnection connection)
    {
        const string schemaSql = @"
            CREATE TABLE IF NOT EXISTS project_info (
                project_number TEXT,
                project_name TEXT,
                address1 TEXT,
                address2 TEXT,
                engineer TEXT,
                date TEXT,
                unit_system INTEGER
            );

            CREATE TABLE IF NOT EXISTS preferences (
                id INTEGER PRIMARY KEY,
                unit_system INTEGER,
                default_engineer TEXT,
                default_company TEXT,
                default_story_height REAL,
                default_wall_self_weight REAL,
                default_stud_spacing REAL,
                max_allowable_cc REAL,
                max_target_dc_ratio REAL,
                default_material_name TEXT,
                service_condition_factor REAL
            );

            CREATE TABLE IF NOT EXISTS sizing_criteria (
                id INTEGER PRIMARY KEY,
                sections TEXT,
                spacings TEXT,
                material_ids TEXT,
                plys TEXT,
                max_target_dc REAL
            );

            CREATE TABLE IF NOT EXISTS wood_materials (
                id INTEGER PRIMARY KEY,
                name TEXT,
                category TEXT,
                species TEXT,
                grade TEXT,
                fb REAL,
                fv REAL,
                fc REAL,
                fcp REAL,
                ft REAL,
                e REAL,
                e05 REAL,
                material_type TEXT
            );

            CREATE TABLE IF NOT EXISTS studs (
                id INTEGER PRIMARY KEY,
                name TEXT,
                section_width REAL,
                section_depth REAL,
                section_plys INTEGER,
                material_id INTEGER
            );

            CREATE TABLE IF NOT EXISTS stories (
                id INTEGER PRIMARY KEY,
                name TEXT,
                height REAL,
                floor_thickness REAL
            );

            CREATE TABLE IF NOT EXISTS loads (
                id INTEGER PRIMARY KEY,
                name TEXT,
                load_case INTEGER,
                value REAL,
                load_type INTEGER
            );

            CREATE TABLE IF NOT EXISTS load_combinations (
                id INTEGER PRIMARY KEY,
                name TEXT
            );

            CREATE TABLE IF NOT EXISTS load_combination_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                combo_id INTEGER,
                load_id INTEGER,
                factor REAL
            );

            CREATE TABLE IF NOT EXISTS walls (
                id INTEGER PRIMARY KEY,
                name TEXT,
                length REAL,
                self_weight REAL,
                plan_x REAL,
                plan_y REAL,
                rotation REAL
            );

            CREATE TABLE IF NOT EXISTS wall_stories (
                id INTEGER PRIMARY KEY,
                wall_id INTEGER,
                story_id INTEGER,
                trib_left REAL,
                trib_right REAL,
                lu_width REAL,
                lu_depth REAL
            );

            CREATE TABLE IF NOT EXISTS wall_story_loads (
                wall_story_id INTEGER,
                load_id INTEGER,
                side TEXT
            );

            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                wall_story_id INTEGER,
                stud_id INTEGER,
                spacing REAL,
                plys INTEGER,
                dc_ratio REAL,
                governing_combo TEXT,
                pf REAL,
                pr REAL,
                kd REAL,
                kh REAL,
                kse REAL,
                ksc REAL,
                kt REAL,
                kzc REAL,
                kc REAL,
                cc REAL,
                fc REAL,
                wood_volume REAL,
                is_final INTEGER
            );
        ";

        using var cmd = connection.CreateCommand();
        cmd.CommandText = schemaSql;
        cmd.ExecuteNonQuery();
    }

    /// <summary>
    /// Exports the current project to a human-readable JSON file.
    /// </summary>
    public void ExportToJson(string filePath)
    {
        var dto = new ProjectDto
        {
            Project = Project,
            Preferences = Preferences,
            SizingCriteria = SizingCriteria,
            Materials = Materials,
            Studs = Studs,
            Stories = Stories,
            Loads = Loads,
            LoadCombinations = LoadCombinations,
            Walls = Walls
        };

        var json = JsonSerializer.Serialize(dto, JsonOptions);
        File.WriteAllText(filePath, json);
    }

    /// <summary>
    /// Imports and reconstructs a project from a JSON file.
    /// </summary>
    public void ImportFromJson(string filePath)
    {
        var json = File.ReadAllText(filePath);
        var dto = JsonSerializer.Deserialize<ProjectDto>(json, JsonOptions);
        if (dto == null) throw new InvalidDataException("Failed to parse project JSON.");

        Project = dto.Project;
        Preferences = dto.Preferences ?? new AppPreferences();
        SizingCriteria = dto.SizingCriteria ?? new SizingCriteria();
        Materials = dto.Materials;
        Studs = dto.Studs;
        Stories = dto.Stories;
        Loads = dto.Loads;
        LoadCombinations = dto.LoadCombinations;
        Walls = dto.Walls;

        // Re-link navigation properties
        var matMap = Materials.ToDictionary(m => m.Id);
        var storyMap = Stories.ToDictionary(s => s.Id);
        var loadMap = Loads.ToDictionary(l => l.Id);
        var studMap = Studs.ToDictionary(s => s.Id);

        foreach (var stud in Studs)
        {
            if (matMap.TryGetValue(stud.MaterialId, out var mat)) stud.Material = mat;
        }

        foreach (var combo in LoadCombinations)
        {
            foreach (var item in combo.Items)
            {
                item.LoadCombination = combo;
                if (loadMap.TryGetValue(item.LoadId, out var l)) item.Load = l;
            }
        }

        foreach (var wall in Walls)
        {
            foreach (var ws in wall.Stories)
            {
                ws.Wall = wall;
                if (storyMap.TryGetValue(ws.StoryId, out var st)) ws.Story = st;
                ws.LoadsLeft = ws.LoadsLeft.Select(l => loadMap.GetValueOrDefault(l.Id, l)).ToList();
                ws.LoadsRight = ws.LoadsRight.Select(l => loadMap.GetValueOrDefault(l.Id, l)).ToList();

                foreach (var res in ws.Results)
                {
                    res.WallStory = ws;
                    if (studMap.TryGetValue(res.StudId, out var stMember)) res.Stud = stMember;
                }
            }
        }
    }

    private class ProjectDto
    {
        public ProjectInfo Project { get; set; } = new();
        public AppPreferences Preferences { get; set; } = new();
        public SizingCriteria SizingCriteria { get; set; } = new();
        public List<WoodMaterial> Materials { get; set; } = new();
        public List<Stud> Studs { get; set; } = new();
        public List<Story> Stories { get; set; } = new();
        public List<Load> Loads { get; set; } = new();
        public List<LoadCombination> LoadCombinations { get; set; } = new();
        public List<Wall> Walls { get; set; } = new();
    }
}
