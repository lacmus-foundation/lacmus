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
        private Annotation _annotation;
        private List<BoundBox> _rectangles;
        private string _name;

        public string Patch => _name;

        public string Name
        {
            get
            {
                var name = System.IO.Path.GetFileName(_name);
                if (name.Length > 10)
                {
                    name = name.Substring(0, 3) + "{~}" + name.Substring(name.Length - 5);
                }
                return name;
            }
            set => _name = value;
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

        public Annotation Annotation
        {
            get => _annotation;
            set => _annotation = value;
        }
        
        public List<BoundBox> Rectangles
        {
            get => _rectangles;
            set => _rectangles = value;
        }

        public Frame()
        {
            _annotation = new Annotation();
        }
        
        public delegate void MethodContainer();

        public event MethodContainer onLoad;

        public void Load(string imgFileName, Enums.ImageLoadMode loadMode = Enums.ImageLoadMode.Full)
        {
            ThreadPool.QueueUserWorkItem(o =>
            {
                _name = imgFileName;
                switch (loadMode)
                {
                    case Enums.ImageLoadMode.Full:
                        _bitmap = new Bitmap(imgFileName);
                        break;
                    case Enums.ImageLoadMode.Miniature:
                        using (SKStream stream = new SKFileStream(imgFileName))
                        using (SKBitmap src = SKBitmap.Decode(stream))
                        {
                            float scale = 100f / src.Width;
                            SKBitmap resized = new SKBitmap(
                                (int)(src.Width * scale),
                                (int)(src.Height * scale), 
                                src.ColorType, 
                                src.AlphaType);
                            SKBitmap.Resize(resized, src, SKBitmapResizeMethod.Hamming);
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
                    onLoad?.Invoke();
                });
            });
        }
        
        public void Load(string imgFileName, string annotationFileName, Enums.ImageLoadMode loadMode = Enums.ImageLoadMode.Full)
        {
            Load(imgFileName, loadMode);
            _annotation = Annotation.ParseFromXml(annotationFileName);
        }

        public void Load(Bitmap bitmap)
        {
            _bitmap = bitmap;
        }
        
        public void LoadFromAnnotation(string annotationFileName, Enums.ImageLoadMode loadMode = Enums.ImageLoadMode.Full)
        {
            _annotation = Annotation.ParseFromXml(annotationFileName);
            Load(_annotation.Patch, loadMode);
        }
        public void LoadFromAnnotation(Annotation annotation, Enums.ImageLoadMode loadMode = Enums.ImageLoadMode.Full)
        {
            _annotation = annotation;
            Load(annotation.Patch, loadMode);
        }
    }
}