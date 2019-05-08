using System;

namespace RescuerLaApp.Models
{
    public class BoundBox
    {
        private int _x;
        private int _y;
        private int _height;
        private int _width;
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

        public void Update(double scaleX, double scaleY)
        {
            _x = (int)(_xBase * scaleX);
            _width = (int)(_widthBase * scaleX);
            _y = (int)(_yBase * scaleY);
            _height = (int)(_heightBase * scaleY);
        }
    }
}