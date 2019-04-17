using System;
using System.Collections.Generic;
using System.IO;
using System.Xml.Serialization;
using RescuerLaApp.Models.Exceptions;

namespace RescuerLaApp.Models
{
    public class Annotation
    {
        public string Folder { get; set; }
        public string Patch { get; set; }
        public Sourse Source { get; set; }
        public Size Size { get; set; }
        public int Segmented { get; set; }
        public List<TObject> Objects { get; set; }
        
        public static Annotation ParseFromXml(string annotationFileName)
        {
            var formatter = new XmlSerializer(type:typeof(Annotation));
            try
            {
                using (var fs = new FileStream(annotationFileName, FileMode.Open))
                {
                    return (Annotation)formatter.Deserialize(fs);
                }
            }
            catch (Exception e)
            {
                throw new AnnotationException("unable to create annotation! " + e.Message);
            }
        }

        public void SaveToXml(string annotationFileName)
        {
            try
            {
                var formatter = new XmlSerializer(type:typeof(Annotation));
                using (var fs = new FileStream(annotationFileName, FileMode.Create))
                {
                    formatter.Serialize(fs, this);
                }
            }
            catch (Exception e)
            {
                throw new AnnotationException("unable to save annotation! " + e.Message);
            }
        }
    }

    public struct TObject
    {
        public string Name { get; set; }
        public Box Box { get; set; }
    }

    public struct Box
    {
        public int Ymin { get; set; }
        public int Xmin { get; set; }
        public int Ymax { get; set; }
        public int Xmax { get; set; }
    }

    public struct Size
    {
        public uint Height { get; set; }
        public uint Width { get; set; }
        public byte Depth { get; set; }
    }

    public struct Sourse
    {
        public string DtatBase { get; set; }
    }
}