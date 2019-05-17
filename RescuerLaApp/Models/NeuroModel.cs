using System;
using System.Collections.Generic;
using System.Drawing;
using System.Threading.Tasks;
using Bitmap = Avalonia.Media.Imaging.Bitmap;

namespace RescuerLaApp.Models
{
    public class NeuroModel : IDisposable
    {
        /*TODO: реализовать логику*/
        public void Initialize()
        {
            
        }

        public void Load(string fileName)
        {
            
        }

        public async Task<List<BoundBox>> Predict(Frame frame)
        {
            var list = new List<BoundBox>();

            // Instantiate Machine Learning C# - Python class object            
            IMlSharpPython mlSharpPython = new MlSharpPython("python3");

            // Test image
            string imagePathName = "";
            var appPath = System.IO.Path.GetDirectoryName(System.Reflection.Assembly.GetExecutingAssembly().Location);
            var modelPatch = $"{appPath}/python/snapshots/resnet50_liza_alert_v1_interface.h5";

            // Define Python script file and input parameter name
            string fileNameParameter = $"{appPath}/python/inference.py --model {modelPatch} --image {frame.Patch}";

            // Execute the python script file 
            var outputText = await Task.Run(() => mlSharpPython.ExecutePythonScript(fileNameParameter));
             
            if (!string.IsNullOrEmpty(outputText))
            {
                foreach (var line in outputText.Split(Environment.NewLine))
                {
                    if(!line.StartsWith("output=")) continue;
                    var output = line.Split(' ');
                    var x1 = int.Parse(output[1]);
                    var y1 = int.Parse(output[2]);
                    var x2 = int.Parse(output[3]);
                    var y2 = int.Parse(output[4]);
                    var score = output[6];
                    var label = output[5];
                    var rect = new BoundBox(
                        x1,
                        y1,
                        y2-y1,
                        x2-x1);
                    list.Add(rect);
                    Console.WriteLine($"{label}: {score}");
                }
            }
            return list;
        }

        public void Dispose()
        {
        }
    }
}