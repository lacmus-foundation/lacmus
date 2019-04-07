using System.Collections.Generic;

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
        
        // TODO: create annotation xml parser
        /*
        public static Annotation ParseFromXml(string annotationFileName)
        {
            
        }
        */
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