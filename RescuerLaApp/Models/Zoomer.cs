using System;
using Avalonia.Controls.PanAndZoom;
using Avalonia.Input;

namespace RescuerLaApp.Models
{
    public class Zoomer
    {
        private static ZoomBorder _zoomBorder = null;

        public static void Init(ZoomBorder zoomBorder)
        {
            _zoomBorder = zoomBorder;
        }

        public static void Zoom(double scale)
        {
            _zoomBorder?.ZoomTo(scale, 0, 0);
        }

        public static void MoveTo(double x, double y)
        {
            _zoomBorder?.StartPan(x,y);
        }

        public static double GetZoomX()
        {
            return _zoomBorder?.ZoomX ?? 1;
        }
        public static double GetZoomY()
        {
            return _zoomBorder?.ZoomY ?? 1;
        }

        public static void Reset()
        {
            _zoomBorder?.Reset();
        }
        
        public static event EventHandler<KeyEventArgs> KeyDown
        {
            add => _zoomBorder.KeyDown+=value;
            remove => _zoomBorder.KeyDown+=value; 
        }
    }
}