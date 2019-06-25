using System.Collections.Generic;
using System.IO;
using Avalonia.Media.Imaging;
using Newtonsoft.Json;

namespace RescuerLaApp.Models
{
    [JsonObject]
    public class JsonImage
    {
        [JsonProperty("objects")]
        public List<Object> Objects { get; set; } = new List<Object>();
        [JsonProperty("data")]
        public byte[] Data { get; set; }

        public void Load(string imagePatch)
        {
            Data = File.ReadAllBytes(imagePatch);
        }

        public Bitmap GetBitmap()
        {
            return new Bitmap(new MemoryStream(Data));
        }

        public List<BoundBox> GetAndBoxes()
        {
            var result = new List<BoundBox>();
            foreach (var obj in Objects)
            {
                var box = new BoundBox(
                    obj.Box.Xmin,
                    obj.Box.Ymin,
                    obj.Box.Ymax - obj.Box.Ymin,
                    obj.Box.Xmax - obj.Box.Xmin
                    );
                result.Add(box);
            }
            return result;
        }
    }
}