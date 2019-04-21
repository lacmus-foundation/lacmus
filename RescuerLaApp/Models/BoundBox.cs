namespace RescuerLaApp.Models
{
    public class BoundBox
    {
        private int _x;
        private int _y;
        private int _height;
        private int _width;

        public BoundBox(int x, int y, int height, int width)
        {
            _x = x;
            _y = y;
            _width = width;
            _height = height;
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

        public void Update(double canvasWidth, double canvasHeight)
        {
            
        }
    }
}