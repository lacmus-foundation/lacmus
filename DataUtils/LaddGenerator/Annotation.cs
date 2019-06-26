using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Xml.Serialization;

namespace LaddGenerator
{
    [Serializable]
    //[XmlRoot("annotation")]
    [XmlRoot("annotation")]
    public class Annotation
    {
        [XmlElement("folder")]
        public string Folder { get; set; } = "VocGalsTfl";
        [XmlElement("filename")]
        public string Filename { get; set; }
        [XmlElement("source")]
        public Sourse Source { get; set; } = new Sourse();
        [XmlElement("size")]
        public Size Size { get; set; }
        [XmlElement("segmented")]
        public int Segmented { get; set; } = 0;
        [XmlElement("object")]
        public List<Object> Objects { get; set; } = new List<Object>();
        
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
                throw new Exception("unable to create annotation! " + e.Message);
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
                throw new Exception("unable to save annotation! " + e.Message);
            }
        }
    }
    
    public class Object
    {
        [XmlElement("name")]
        public string Name { get; set; }
        [XmlElement("pose")]
        public string Pose { get; set; } = "Unspecified";
        [XmlElement("truncated")]
        public int Truncated { get; set; } = 0;
        [XmlElement("difficult")]
        public int Difficult { get; set; } = 0;
        [XmlElement("bndbox")]
        public Box Box { get; set; }
    }
    
    public class Box
    {
        [XmlElement("ymin")]
        public string Ymin
        {
            get; set;
        }

        [XmlElement("xmin")]
        public string Xmin
        {
            get; set;
        }

        [XmlElement("ymax")]
        public string Ymax
        {
            get; set;
        }

        [XmlElement("xmax")]
        public string Xmax
        {
            get; set;
        }

        public void Normalize()
        {
            Xmin = ParseInt(Xmin);
            Xmax = ParseInt(Xmax);
            Ymin = ParseInt(Ymin);
            Ymax = ParseInt(Ymax);
        }

        private string ParseInt(string str)
        {
            if (str.StartsWith("-"))
                return $"{0}";
            str = str.Split('.').First();
            if (int.TryParse(str, out var r))
            {
                 return $"{r}";
            }
            throw new Exception();
        }
    }

    public class Size
    {
        [XmlElement("height")]
        public uint Height { get; set; }
        [XmlElement("width")]
        public uint Width { get; set; }
        [XmlElement("depth")] 
        public byte Depth { get; set; } = 3;
    }

    public class Sourse
    {
        [XmlElement("database")]
        public string DtatBase { get; set; } = "Unknown";
    }
}