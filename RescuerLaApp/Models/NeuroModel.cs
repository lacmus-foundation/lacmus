using System;
using System.Collections.Generic;
using System.IO;
using System.Threading.Tasks;
using  Newtonsoft.Json;

namespace RescuerLaApp.Models
{
    public class NeuroModel : IDisposable
    {
        /*TODO: реализовать логику*/
        private readonly string _pythonExecName;
        private readonly string _fileNameParameter;
        private readonly RestApiClient _client;
        private MlSharpPython _mlSharpPython;
        
        
        public NeuroModel()
        {
            _pythonExecName = "python3";
            var appPath = System.IO.Path.GetDirectoryName(System.Reflection.Assembly.GetExecutingAssembly().Location);
            var modelName = "resnet50_liza_alert_v1_interface.h5";
            var modelPatch = $"{appPath}/python/snapshots/{modelName}";
            _fileNameParameter = $"{appPath}/python/inference.py --model {modelPatch}";
            
            _client = new RestApiClient("http://127.0.0.1:5000/");
        }

        public async Task<bool> Load()
        {
            _mlSharpPython = new MlSharpPython(_pythonExecName);
            return await Task.Run(() => _mlSharpPython.Run(_fileNameParameter));
        }

        public async Task<List<BoundBox>> Predict(Frame frame)
        {
            var list = new List<BoundBox>();
            var status = await _client.GetAsync();
            if (status == null || !status.Contains("server is running"))
            {
                Console.WriteLine("server is not active");
                return list;
            }
            
            var jsonImg = new JsonImage();
            jsonImg.Load(frame.Patch);
            var json = JsonConvert.SerializeObject(jsonImg);
            var outputText = await _client.PostAsync(json, "image");
             
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
            try
            {
                _mlSharpPython.Stop();
                _client.Get("exit");
            }
            catch
            {
                // ignored
            }
            
        }
    }
}