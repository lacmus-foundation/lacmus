using System;
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

        public Rectangle Predict(Bitmap bitmap)
        {
            return new Rectangle()
            {
                X = bitmap.PixelSize.Width / 2,
                Y = bitmap.PixelSize.Height / 2,
                Width = 10,
                Height = 10
            };
        }

        public void Dispose()
        {
        }
    }
}