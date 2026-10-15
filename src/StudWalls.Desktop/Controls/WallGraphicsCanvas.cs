using System.Globalization;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Media;
using StudWalls.Core.Models;

namespace StudWalls.Desktop.Controls;

/// <summary>
/// Custom Avalonia graphics control rendering a Building Plan View of all walls.
/// Supports toggling tributary widths and applied loads, and highlights the currently active wall.
/// Strictly uses standard OOTB Avalonia drawing primitives without custom skins or emoji.
/// </summary>
public class WallGraphicsCanvas : Control
{
    public static readonly StyledProperty<IReadOnlyList<Wall>?> WallsProperty =
        AvaloniaProperty.Register<WallGraphicsCanvas, IReadOnlyList<Wall>?>(nameof(Walls));

    public static readonly StyledProperty<Wall?> SelectedWallProperty =
        AvaloniaProperty.Register<WallGraphicsCanvas, Wall?>(nameof(SelectedWall));

    public static readonly StyledProperty<Story?> ActiveStoryProperty =
        AvaloniaProperty.Register<WallGraphicsCanvas, Story?>(nameof(ActiveStory));

    public static readonly StyledProperty<bool> ShowTributariesProperty =
        AvaloniaProperty.Register<WallGraphicsCanvas, bool>(nameof(ShowTributaries), true);

    public static readonly StyledProperty<bool> ShowLoadsProperty =
        AvaloniaProperty.Register<WallGraphicsCanvas, bool>(nameof(ShowLoads), true);

    public IReadOnlyList<Wall>? Walls
    {
        get => GetValue(WallsProperty);
        set => SetValue(WallsProperty, value);
    }

    public Wall? SelectedWall
    {
        get => GetValue(SelectedWallProperty);
        set => SetValue(SelectedWallProperty, value);
    }

    public Story? ActiveStory
    {
        get => GetValue(ActiveStoryProperty);
        set => SetValue(ActiveStoryProperty, value);
    }

    public bool ShowTributaries
    {
        get => GetValue(ShowTributariesProperty);
        set => SetValue(ShowTributariesProperty, value);
    }

    public bool ShowLoads
    {
        get => GetValue(ShowLoadsProperty);
        set => SetValue(ShowLoadsProperty, value);
    }

    static WallGraphicsCanvas()
    {
        AffectsRender<WallGraphicsCanvas>(WallsProperty, SelectedWallProperty, ActiveStoryProperty, ShowTributariesProperty, ShowLoadsProperty);
    }

    public override void Render(DrawingContext context)
    {
        base.Render(context);

        var bounds = Bounds;
        if (bounds.Width < 10 || bounds.Height < 10) return;

        // Background canvas fill
        context.DrawRectangle(Brushes.White, new Pen(Brushes.LightGray, 1), bounds);

        if (Walls == null || Walls.Count == 0)
        {
            var noDataText = new FormattedText(
                "No walls configured to display in plan view.",
                CultureInfo.CurrentCulture,
                FlowDirection.LeftToRight,
                Typeface.Default,
                14,
                Brushes.Gray);
            context.DrawText(noDataText, new Point(bounds.Width / 2 - 120, bounds.Height / 2 - 10));
            return;
        }

        // Determine bounding box across all walls
        double minX = double.MaxValue, maxX = double.MinValue;
        double minY = double.MaxValue, maxY = double.MinValue;

        foreach (var w in Walls)
        {
            double endX = w.PlanX + (w.Length * Math.Cos(w.RotationDegrees * Math.PI / 180.0));
            double endY = w.PlanY + (w.Length * Math.Sin(w.RotationDegrees * Math.PI / 180.0));

            double maxTrib = 2000.0; // Margin allowance for trib widths
            minX = Math.Min(minX, Math.Min(w.PlanX, endX) - maxTrib);
            maxX = Math.Max(maxX, Math.Max(w.PlanX, endX) + maxTrib);
            minY = Math.Min(minY, Math.Min(w.PlanY, endY) - maxTrib);
            maxY = Math.Max(maxY, Math.Max(w.PlanY, endY) + maxTrib);
        }

        double modelWidth = Math.Max(maxX - minX, 1000.0);
        double modelHeight = Math.Max(maxY - minY, 1000.0);

        double padding = 40.0;
        double scaleX = (bounds.Width - (2 * padding)) / modelWidth;
        double scaleY = (bounds.Height - (2 * padding)) / modelHeight;
        double scale = Math.Min(scaleX, scaleY);

        Point WorldToScreen(double x, double y)
        {
            double screenX = padding + (x - minX) * scale;
            double screenY = padding + (y - minY) * scale;
            return new Point(screenX, screenY);
        }

        // Draw each wall and its tributary zones
        foreach (var wall in Walls)
        {
            bool isSelected = SelectedWall != null && SelectedWall.Id == wall.Id;

            // Find wall story for active story
            var ws = wall.Stories.FirstOrDefault(s => ActiveStory != null && s.StoryId == ActiveStory.Id)
                     ?? wall.Stories.FirstOrDefault();

            double rad = wall.RotationDegrees * Math.PI / 180.0;
            double dirX = Math.Cos(rad);
            double dirY = Math.Sin(rad);

            // Perpendicular unit vector (points to the left side of the wall direction)
            double perpX = -dirY;
            double perpY = dirX;

            double p1X = wall.PlanX;
            double p1Y = wall.PlanY;
            double p2X = p1X + (wall.Length * dirX);
            double p2Y = p1Y + (wall.Length * dirY);

            var screenP1 = WorldToScreen(p1X, p1Y);
            var screenP2 = WorldToScreen(p2X, p2Y);

            if (ws != null && ShowTributaries)
            {
                // Left tributary band
                if (ws.TribWidthLeft > 0)
                {
                    double t1X = p1X + (ws.TribWidthLeft * perpX);
                    double t1Y = p1Y + (ws.TribWidthLeft * perpY);
                    double t2X = p2X + (ws.TribWidthLeft * perpX);
                    double t2Y = p2Y + (ws.TribWidthLeft * perpY);

                    var st1 = WorldToScreen(t1X, t1Y);
                    var st2 = WorldToScreen(t2X, t2Y);

                    var leftPoly = new StreamGeometry();
                    using (var geomCtx = leftPoly.Open())
                    {
                        geomCtx.BeginFigure(screenP1, isFilled: true);
                        geomCtx.LineTo(screenP2);
                        geomCtx.LineTo(st2);
                        geomCtx.LineTo(st1);
                        geomCtx.EndFigure(isClosed: true);
                    }

                    var leftBrush = new SolidColorBrush(Color.FromArgb(40, 0, 100, 200));
                    context.DrawGeometry(leftBrush, new Pen(Brushes.SteelBlue, 0.8, DashStyle.Dash), leftPoly);

                    // Tributary width annotation
                    var midX = (screenP1.X + st2.X) / 2.0;
                    var midY = (screenP1.Y + st2.Y) / 2.0;
                    var tribText = new FormattedText($"Trib L: {ws.TribWidthLeft:F0}mm", CultureInfo.CurrentCulture, FlowDirection.LeftToRight, Typeface.Default, 10, Brushes.DarkSlateBlue);
                    context.DrawText(tribText, new Point(midX, midY));
                }

                // Right tributary band (points opposite to perp)
                if (ws.TribWidthRight > 0)
                {
                    double r1X = p1X - (ws.TribWidthRight * perpX);
                    double r1Y = p1Y - (ws.TribWidthRight * perpY);
                    double r2X = p2X - (ws.TribWidthRight * perpX);
                    double r2Y = p2Y - (ws.TribWidthRight * perpY);

                    var sr1 = WorldToScreen(r1X, r1Y);
                    var sr2 = WorldToScreen(r2X, r2Y);

                    var rightPoly = new StreamGeometry();
                    using (var geomCtx = rightPoly.Open())
                    {
                        geomCtx.BeginFigure(screenP1, isFilled: true);
                        geomCtx.LineTo(screenP2);
                        geomCtx.LineTo(sr2);
                        geomCtx.LineTo(sr1);
                        geomCtx.EndFigure(isClosed: true);
                    }

                    var rightBrush = new SolidColorBrush(Color.FromArgb(40, 0, 160, 60));
                    context.DrawGeometry(rightBrush, new Pen(Brushes.SeaGreen, 0.8, DashStyle.Dash), rightPoly);

                    var midX = (screenP1.X + sr2.X) / 2.0;
                    var midY = (screenP1.Y + sr2.Y) / 2.0;
                    var tribText = new FormattedText($"Trib R: {ws.TribWidthRight:F0}mm", CultureInfo.CurrentCulture, FlowDirection.LeftToRight, Typeface.Default, 10, Brushes.DarkGreen);
                    context.DrawText(tribText, new Point(midX, midY));
                }
            }

            if (ws != null && ShowLoads)
            {
                // Applied loads annotation
                double leftDL = ws.LoadsLeft.Where(l => l.Case == StudWalls.Core.Enums.LoadCase.Dead).Sum(l => l.Value);
                double leftLL = ws.LoadsLeft.Where(l => l.Case == StudWalls.Core.Enums.LoadCase.Live).Sum(l => l.Value);
                double rightDL = ws.LoadsRight.Where(l => l.Case == StudWalls.Core.Enums.LoadCase.Dead).Sum(l => l.Value);
                double rightLL = ws.LoadsRight.Where(l => l.Case == StudWalls.Core.Enums.LoadCase.Live).Sum(l => l.Value);

                if (leftDL > 0 || leftLL > 0)
                {
                    var text = new FormattedText($"Left: D={leftDL:F1}, L={leftLL:F1} kPa", CultureInfo.CurrentCulture, FlowDirection.LeftToRight, Typeface.Default, 9, Brushes.MidnightBlue);
                    context.DrawText(text, new Point(screenP1.X, screenP1.Y - 20));
                }

                if (rightDL > 0 || rightLL > 0)
                {
                    var text = new FormattedText($"Right: D={rightDL:F1}, L={rightLL:F1} kPa", CultureInfo.CurrentCulture, FlowDirection.LeftToRight, Typeface.Default, 9, Brushes.DarkOliveGreen);
                    context.DrawText(text, new Point(screenP1.X, screenP1.Y + 20));
                }
            }

            // Draw the wall line
            var wallPen = isSelected
                ? new Pen(Brushes.Crimson, 6.0, lineCap: PenLineCap.Square)
                : new Pen(Brushes.Black, 4.0, lineCap: PenLineCap.Square);

            context.DrawLine(wallPen, screenP1, screenP2);

            // Wall label
            var wallLabel = new FormattedText(
                $"{wall.Name} (L = {wall.Length:F0} mm)",
                CultureInfo.CurrentCulture,
                FlowDirection.LeftToRight,
                isSelected ? new Typeface(FontFamily.Default, FontStyle.Normal, FontWeight.Bold) : Typeface.Default,
                11,
                isSelected ? Brushes.Crimson : Brushes.Black);

            context.DrawText(wallLabel, new Point((screenP1.X + screenP2.X) / 2.0 - 40, (screenP1.Y + screenP2.Y) / 2.0 - 18));
        }
    }
}
