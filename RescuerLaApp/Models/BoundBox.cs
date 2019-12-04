using System;
using System.Collections.Generic;
using Avalonia;

namespace RescuerLaApp.Models
{
    public class BoundBox
    {
        private int _x;
        private int _y;
        private int _height;
        private int _width;
        private bool _isVisible;
        private readonly int _xBase;
        private readonly int _yBase;
        private readonly int _heightBase;
        private readonly int _widthBase; 

        public BoundBox(int x, int y, int height, int width)
        {
            _x = _xBase = x;
            _y = _yBase = y;
            _width = _widthBase = width;
            _height = _heightBase = height;
            _isVisible = true;
        }

        public List<Point> Points
        {
            get
            {
                var p1 = new Point(_x, _y);
                var p2 = new Point(_x, _y + _height);
                var p3 = new Point(_x + _width, _y);
                var p4 = new Point(_x + _width, _y + _height);
                return new List<Point> {p1, p3, p4, p2};
            }
        }

        public bool IsVisible
        {
            get => _isVisible;
            set => _isVisible = value;
        }

        public int X
        {
            get => _x;
            set => _x = value;
        }

        public int Y
        {
            get => _y;
            set => _y = value;
        }

        public int Height
        {
            get => _height;
            set => _height = value;
        }

        public int Width
        {
            get => _width;
            set => _width = value;
        }

        public int HeightBase => _heightBase;
        public int WidthBase => _widthBase;
        public int XBase => _xBase;
        public int YBase => _yBase;

        public void Update(double scaleX, double scaleY)
        {
            Console.WriteLine($"{_xBase} {_yBase}");
            _x = (int)(_xBase * scaleX);
            _width = (int)(_widthBase * scaleX);
            _y = (int)(_yBase * scaleY);
            _height = (int)(_heightBase * scaleY);
            Console.WriteLine($"{_x} {_y}");
        }
    }
}