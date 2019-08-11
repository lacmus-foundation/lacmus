using System;
using System.Collections.Generic;
using System.IO;
using System.Threading;
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
        private Docker _docker;
        private string _id = "";
        
        
        public NeuroModel()
        {
            _pythonExecName = "python3";
            #if DEBUG
            _pythonExecName = "/home/gosha20777/anaconda3/bin/python";
            #endif
            var appPath = System.IO.Path.GetDirectoryName(System.Reflection.Assembly.GetExecutingAssembly().Location);
            var modelName = "resnet50_liza_alert_v3_interface.h5";
            var modelPatch = $"{appPath}/python/snapshots/{modelName}";
            _fileNameParameter = $"{appPath}/python/inference.py --model {modelPatch}";
            
            _client = new RestApiClient("http://127.0.0.1:5000/");
            _docker = new Docker();
        }

        public async Task<bool> Run()
        {
            Console.WriteLine("Checking reina-net service...");
            var status = await _client.GetStatusAsync();
            if (status != null && status.Contains("server is running"))
            {
                Console.WriteLine("Reina-net is ready!");
                return true;
            }
            Console.WriteLine("Retina-net is not running: trying to run...");

            await Load();
            
            
            if (await _docker.Run(_id))
            {
                Console.WriteLine("Container runs. Loading retina-net model...");
                var startTime = DateTime.Now;
                TimeSpan waitingTime = new TimeSpan(0, 0, 10, 0);
                while (DateTime.Now - startTime < waitingTime)
                {
                    // Provide a 100ms startup delay
                    await Task.Delay(TimeSpan.FromMilliseconds(100));
                    status = await _client.GetStatusAsync();
                    if (status != null && status.Contains("server is running"))
                    {
                        Console.WriteLine("Reina-net is ready!");
                        return true;
                    }   
                }
            }
            return false;
        }

        public async Task<List<BoundBox>> Predict(Frame frame)
        {
            var list = new List<BoundBox>();
            var status = await _client.GetStatusAsync();
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
                    Console.WriteLine($">{label}: {score}");
                }
            }
            return list;
        }

        public async Task Stop()
        {
            if (!string.IsNullOrWhiteSpace(_id))
            {
                Console.WriteLine($"stopping retina-net... {_id}");
                await _docker.Stop(_id);
            }
                
        }

        public async Task UpdateModel()
        {   
            Console.WriteLine("updating retina-net...");
            var tags = await _docker.GetTags();
            var maxTag = 1;
            var curTag = await GetCurrentTag();
            foreach (var t in tags)
            {
                if (int.TryParse(t, out var tag))
                    maxTag = Math.Max(maxTag, tag);
            }

            if (maxTag <= curTag)
            {
                Console.WriteLine($"everything is up to date: your version v{curTag} last version v{maxTag}");
                return;
            }
            
            Console.WriteLine($"find new retina-net version: your version v{curTag} last version v{maxTag}");
            Console.WriteLine("downloading new version...");
            await _docker.Initialize(tag: maxTag.ToString());
            Console.WriteLine("installing new version...");
            _id = await _docker.CreateContainer(tag: maxTag.ToString());
            Console.WriteLine("removing old version...");
            await _docker.Remove(tag: curTag.ToString());
            Console.WriteLine($"done! your version v{maxTag}");
        }

        public async Task<bool> CanUpdate()
        {
            var tags = await _docker.GetTags();
            var maxTag = 1;
            foreach (var t in tags)
            {
                if (int.TryParse(t, out var tag))
                   maxTag = Math.Max(maxTag, tag);
            }

            return maxTag > await GetCurrentTag();
        }

        private async Task<int> GetCurrentTag()
        {
            var tags = await _docker.GetInstalledVersions();
            var maxTag = 1;
            foreach (var t in tags)
            {
                if (int.TryParse(t, out var tag))
                    maxTag = Math.Max(maxTag, tag);
            }
            return maxTag;
        }

        public async Task Load()
        {
            var tag = await GetCurrentTag();
            Console.WriteLine($"loading retina-net v{tag}...");
            await _docker.Initialize(tag: tag.ToString());
            Console.WriteLine($"installing retina-net v{tag}...");
            _id = await _docker.CreateContainer(tag: tag.ToString());
            Console.WriteLine("done!");
        }

        public void Dispose()
        {
            try
            {
                _docker.Dispose();
            }
            catch
            {
                // ignored
            }
            
        }
    }
}