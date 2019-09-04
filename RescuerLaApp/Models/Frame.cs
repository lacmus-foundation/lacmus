using System;
using System.Collections.Generic;
using System.Threading;
using Avalonia;
using Avalonia.Media;
using Avalonia.Skia;
using Avalonia.Threading;
using SkiaSharp;
using Avalonia.Media.Imaging;

namespace RescuerLaApp.Models
{
    public class Frame
    {
        private ImageBrush _imageBrush = new ImageBrush() { Stretch = Stretch.Uniform };
        private Bitmap _bitmap;
        private List<BoundBox> _rectangles;

        public string Patch { get; set; }

        public string Name
        {
            get
            {
                var name = System.IO.Path.GetFileName(Patch);
                if (name.Length > 10)
                {
                    name = name.Substring(0, 3) + "{~}" + name.Substring(name.Length - 5);
                }
                return name;
            }
        }

        public ImageBrush ImageBrush
        {
            get => _imageBrush;
            set => _imageBrush = value;
        }

        public Bitmap Bitmap
        {
            get => _bitmap;
            set => _bitmap = value;
        }

        public List<BoundBox> Rectangles
        {
            get => _rectangles;
            set => _rectangles = value;
        }
        public int Width { get; private set; }
        public int Height { get; private set; }

        public bool IsVisible { get; set; } = false;
        
        public delegate void MethodContainer();

        public event MethodContainer OnLoad;

        public void Load(string imgFileName, Enums.ImageLoadMode loadMode = Enums.ImageLoadMode.Full)
        {
            ThreadPool.QueueUserWorkItem(o =>
            {
                Patch = imgFileName;
                switch (loadMode)
                {
                    case Enums.ImageLoadMode.Full:
                        _bitmap = new Bitmap(imgFileName);
                        Width = _bitmap.PixelSize.Width;
                        Height = _bitmap.PixelSize.Height;
                        break;
                    case Enums.ImageLoadMode.Miniature:
                        using (SKStream stream = new SKFileStream(imgFileName))
                        using (SKBitmap src = SKBitmap.Decode(stream))
                        {
                            Width = src.Width;
                            Height = src.Height;
                            float scale = 100f / src.Width;
                            SKBitmap resized = new SKBitmap(
                                (int)(src.Width * scale),
                                (int)(src.Height * scale), 
                                src.ColorType, 
                                src.AlphaType);
                            src.ScalePixels(resized, SKFilterQuality.Low);
                            _bitmap = new Bitmap(
                                resized.ColorType.ToPixelFormat(),
                                resized.GetPixels(),
                                new PixelSize(resized.Width, resized.Height), 
                                SkiaPlatform.DefaultDpi, 
                                resized.RowBytes);
                        }
                        break;
                    default:
                        throw new Exception($"invalid ImageLoadMode:{loadMode.ToString()}");
                }
                Dispatcher.UIThread.InvokeAsync(() =>
                {
                    _imageBrush.Source = _bitmap;
                    OnLoad?.Invoke();
                });
            });
        }
    }
}