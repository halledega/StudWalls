using System.Globalization;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Media;
using StudWalls.Core.Models;

namespace StudWalls.Desktop.Controls;

/// <summary>
/// Custom Avalonia graphics control rendering a cross-sectional detail of a wood stud member.
/// Shows individual plys (1, 2, 3 plys), depth (d), width (b), and dimension callouts.
/// OOTB Avalonia vector drawing.
/// </summary>
public class StudSectionCanvas : Control
{
    public static readonly StyledProperty<Stud?> StudProperty =
        AvaloniaProperty.Register<StudSectionCanvas, Stud?>(nameof(Stud));

    public static readonly StyledProperty<int> PlysProperty =
        AvaloniaProperty.Register<StudSectionCanvas, int>(nameof(Plys), 1);

    public Stud? Stud
    {
        get => GetValue(StudProperty);
        set => SetValue(StudProperty, value);
    }

    public int Plys
    {
        get => GetValue(PlysProperty);
        set => SetValue(PlysProperty, value);
    }

    static StudSectionCanvas()
    {
        AffectsRender<StudSectionCanvas>(StudProperty, PlysProperty);
    }

    public override void Render(DrawingContext context)
    {
        base.Render(context);

        var bounds = Bounds;
        if (bounds.Width < 10 || bounds.Height < 10) return;

        context.DrawRectangle(Brushes.White, new Pen(Brushes.LightGray, 1), bounds);

        if (Stud == null)
        {
            var text = new FormattedText("Select a stud to view cross-section detail.", CultureInfo.CurrentCulture, FlowDirection.LeftToRight, Typeface.Default, 13, Brushes.Gray);
            context.DrawText(text, new Point(bounds.Width / 2 - 120, bounds.Height / 2 - 10));
            return;
        }

        double singlePlyWidth = Stud.Section.Width > 0 ? Stud.Section.Width : 38.1;
        double depth = Stud.Section.Depth > 0 ? Stud.Section.Depth : 139.7;
        int plys = Plys > 0 ? Plys : 1;
        double totalWidth = singlePlyWidth * plys;

        // Scale to fit center of canvas with margins
        double maxDrawWidth = bounds.Width * 0.55;
        double maxDrawHeight = bounds.Height * 0.55;

        double scale = Math.Min(maxDrawWidth / totalWidth, maxDrawHeight / depth);

        double drawTotalWidth = totalWidth * scale;
        double drawSingleWidth = singlePlyWidth * scale;
        double drawDepth = depth * scale;

        double startX = (bounds.Width - drawTotalWidth) / 2.0;
        double startY = (bounds.Height - drawDepth) / 2.0;

        var woodFill = new SolidColorBrush(Color.FromRgb(245, 235, 215)); // Natural wood hue
        var woodStroke = new Pen(new SolidColorBrush(Color.FromRgb(140, 100, 50)), 1.5);
        var centerLinePen = new Pen(new SolidColorBrush(Color.FromRgb(180, 140, 90)), 1.0, DashStyle.Dash);

        // Draw each ply rectangle
        for (int p = 0; p < plys; p++)
        {
            var plyRect = new Rect(startX + (p * drawSingleWidth), startY, drawSingleWidth, drawDepth);
            context.DrawRectangle(woodFill, woodStroke, plyRect);

            // Draw timber framing cross hatching (X)
            context.DrawLine(centerLinePen, plyRect.TopLeft, plyRect.BottomRight);
            context.DrawLine(centerLinePen, plyRect.BottomLeft, plyRect.TopRight);
        }

        // Draw dimension callouts
        var dimPen = new Pen(Brushes.Black, 1.0);

        // Depth dimension (right side)
        double dimRightX = startX + drawTotalWidth + 25;
        context.DrawLine(dimPen, new Point(dimRightX, startY), new Point(dimRightX, startY + drawDepth));
        context.DrawLine(dimPen, new Point(dimRightX - 5, startY), new Point(dimRightX + 5, startY));
        context.DrawLine(dimPen, new Point(dimRightX - 5, startY + drawDepth), new Point(dimRightX + 5, startY + drawDepth));

        var depthText = new FormattedText($"d = {depth:F1} mm", CultureInfo.CurrentCulture, FlowDirection.LeftToRight, Typeface.Default, 11, Brushes.Black);
        context.DrawText(depthText, new Point(dimRightX + 8, startY + (drawDepth / 2) - 8));

        // Width dimension (top side)
        double dimTopY = startY - 20;
        context.DrawLine(dimPen, new Point(startX, dimTopY), new Point(startX + drawTotalWidth, dimTopY));
        context.DrawLine(dimPen, new Point(startX, dimTopY - 5), new Point(startX, dimTopY + 5));
        context.DrawLine(dimPen, new Point(startX + drawTotalWidth, dimTopY - 5), new Point(startX + drawTotalWidth, dimTopY + 5));

        var widthText = new FormattedText($"b = {totalWidth:F1} mm ({plys} ply @ {singlePlyWidth:F1} mm)", CultureInfo.CurrentCulture, FlowDirection.LeftToRight, Typeface.Default, 11, Brushes.Black);
        context.DrawText(widthText, new Point(startX, dimTopY - 18));

        // Member description header
        var titleText = new FormattedText(
            $"({plys})-{Stud.Name} | Material: {Stud.Material.Name} | Ag: {Stud.Section.Ag * plys:F0} mm²",
            CultureInfo.CurrentCulture,
            FlowDirection.LeftToRight,
            new Typeface(FontFamily.Default, FontStyle.Normal, FontWeight.Bold),
            12,
            Brushes.Black);
        context.DrawText(titleText, new Point(20, 20));
    }
}
