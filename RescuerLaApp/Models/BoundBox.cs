using System;
using System.Collections.Generic;
using Avalonia;

namespace RescuerLaApp.Models
{
    public class BoundBox
    {
        public BoundBox(int x, int y, int height, int width)
        {
            X = XBase = x;
            Y = YBase = y;
            Width = WidthBase = width;
            Height = HeightBase = height;
            IsVisible = true;
        }

        public List<Point> Points
        {
            get
            {
                var p1 = new Point(X, Y);
                var p2 = new Point(X, Y + Height);
                var p3 = new Point(X + Width, Y);
                var p4 = new Point(X + Width, Y + Height);
                return new List<Point> {p1, p3, p4, p2};
            }
        }

        public bool IsVisible { get; set; }

        public int X { get; set; }

        public int Y { get; set; }

        public int Height { get; set; }

        public int Width { get; set; }

        public int HeightBase { get; }

        public int WidthBase { get; }

        public int XBase { get; }

        public int YBase { get; }

        public void Update(double scaleX, double scaleY)
        {
            Console.WriteLine($"{XBase} {YBase}");
            X = (int)(XBase * scaleX);
            Width = (int)(WidthBase * scaleX);
            Y = (int)(YBase * scaleY);
            Height = (int)(HeightBase * scaleY);
            Console.WriteLine($"{X} {Y}");
        }
    }
}