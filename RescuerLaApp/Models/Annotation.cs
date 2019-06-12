using System;
using System.Collections.Generic;
using System.IO;
using System.Xml.Serialization;
using RescuerLaApp.Models.Exceptions;
using Newtonsoft.Json;

namespace RescuerLaApp.Models
{
    [Serializable]
    public class Annotation
    {
        public string Folder { get; set; }
        public string Patch { get; set; }
        public Sourse Source { get; set; }
        public Size Size { get; set; }
        public int Segmented { get; set; }
        public List<Object> Objects { get; set; }
        
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

    [JsonObject]
    public struct Object
    {
        [JsonProperty("name")]
        public string Name { get; set; }
        [JsonProperty("box")]
        public Box Box { get; set; }
    }

    [JsonObject]
    public struct Box
    {
        [JsonProperty("ymin")]
        public int Ymin { get; set; }
        [JsonProperty("xmin")]
        public int Xmin { get; set; }
        [JsonProperty("ymax")]
        public int Ymax { get; set; }
        [JsonProperty("xmax")]
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