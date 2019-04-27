using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Controls.Shapes;
using Avalonia.Media;
using Avalonia.Platform;
using Avalonia.Skia;
using SkiaSharp;
using Bitmap = Avalonia.Media.Imaging.Bitmap;
using ImageBrush = Avalonia.Media.ImageBrush;

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

        public void Load(string imgFileName, Enums.TImageLoadMode loadMode)
        {
            if(loadMode == Enums.TImageLoadMode.Miniature)
            using (SKStream stream = new SKFileStream(imgFileName))
            using (SKBitmap src = SKBitmap.Decode(stream))
            {
                float scale = 100f / src.Width;
                SKBitmap resized = new SKBitmap(
                    (int)(src.Width * scale),
                    (int)(src.Height * scale), src.ColorType, src.AlphaType);
                SKBitmap.Resize(resized, src, SKBitmapResizeMethod.Hamming);
                this._bitmap = new Bitmap(
                    resized.ColorType.ToPixelFormat(),
                    resized.GetPixels(),
                    new PixelSize(resized.Width, resized.Height), 
                    SkiaPlatform.DefaultDpi, 
                    resized.RowBytes);
            }
            else
                this._bitmap = new Bitmap(imgFileName);
            this._imageBrush.Source = _bitmap;
            this.Name = imgFileName;
        }
        
        public void Load(string ingFileName, string annotationFileName)
        {
            this._bitmap = new Bitmap(ingFileName);
            this._annotation = Annotation.ParseFromXml(annotationFileName);
        }

        public void Load(Bitmap bitmap)
        {
            this._bitmap = bitmap;
        }
        
        public void LoadFromAnnotation(string annotationFileName)
        {
            this._annotation = Annotation.ParseFromXml(annotationFileName);
        }
        public void LoadFromAnnotation(Annotation annotation)
        {
            this._annotation = annotation;
            this._bitmap = new Bitmap(_annotation.Patch);
        }
    }
}