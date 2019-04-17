using System.Collections.Generic;
using Avalonia.Controls.Shapes;
using Avalonia.Media.Imaging;

namespace RescuerLaApp.Models
{
    public class Frame
    {
        private Bitmap _bitmap;
        private Annotation _annotation;
        private List<Rectangle> _rectangles;

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
        
        public List<Rectangle> Rectangles
        {
            get => _rectangles;
            set => _rectangles = value;
        }

        public Frame()
        {
            _annotation = new Annotation();
        }

        public void Load(string ingFileName)
        {
            this._bitmap = new Bitmap(ingFileName);
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