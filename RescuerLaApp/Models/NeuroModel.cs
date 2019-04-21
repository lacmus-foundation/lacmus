using System;
using System.Collections.Generic;
using System.Drawing;
using Bitmap = Avalonia.Media.Imaging.Bitmap;

namespace RescuerLaApp.Models
{
    public class NeuroModel : IDisposable
    {
        public void Initialize()
        {
            
        }

        public void Load(string fileName)
        {
            
        }

        public List<BoundBox> Predict(Bitmap bitmap)
        {
            var list = new List<BoundBox>();
            var rect = new BoundBox(
                bitmap.PixelSize.Width / 2,
                bitmap.PixelSize.Height / 2,
                10,
                10);
            list.Add(rect);
            return list;
        }

        public void Dispose()
        {
        }
    }
}