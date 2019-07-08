using System;
using System.Collections.Generic;
using System.IO;
using System.Xml.Serialization;
using RescuerLaApp.Models.Exceptions;

namespace RescuerLaApp.Models
{
    [Serializable]
    [XmlRoot("annotation")]
    public class Annotation
    {
        [XmlElement("folder")] public string Folder { get; set; } = "VocGalsTfl";
        [XmlElement("filename")] public string Filename { get; set; }
        [XmlElement("source")] public Source Source { get; set; } = new Source();
        [XmlElement("size")] public Size Size { get; set; }
        [XmlElement("segmented")] public int Segmented { get; set; } = 0;
        [XmlElement("object")] public List<Object> Objects { get; set; } = new List<Object>();
        
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
    
    public class Object
    {
        [XmlElement("name")] public string Name { get; set; } 
        [XmlElement("pose")] public string Pose { get; set; } = "Unspecified";
        [XmlElement("truncated")] public int Truncated { get; set; } = 0;
        [XmlElement("difficult")] public int Difficult { get; set; } = 0;
        [XmlElement("bndbox")] public Box Box { get; set; }
    }
    
    public class Box
    {
        [XmlElement("ymin")] public int Ymin { get; set; }
        [XmlElement("xmin")] public int Xmin { get; set; }
        [XmlElement("ymax")] public int Ymax { get; set; }
        [XmlElement("xmax")] public int Xmax { get; set; }
    }

    public class Size
    {
        [XmlElement("height")] public int Height { get; set; }
        [XmlElement("width")] public int Width { get; set; }
        [XmlElement("depth")] public byte Depth { get; set; } = 3;
    }

    public class Source
    {
        [XmlElement("database")] public string DataBase { get; set; } = "Unknown";
    }
}