using System;
using System.Collections.Generic;
using System.IO;
using System.Threading.Tasks;
using  Newtonsoft.Json;

namespace RescuerLaApp.Models
{
    public class NeuroModel : INeuroModel 
    {
        private readonly RestApiClient _client;
        private Docker _docker;
        private string _id = "";
        
        
        public NeuroModel()
        {
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

        public async Task<List<BoundBox>> Predict(string path)
        {
            var list = new List<BoundBox>();
            var status = await _client.GetStatusAsync();
            if (status == null || !status.Contains("server is running"))
            {
                Console.WriteLine("server is not active");
                return list;
            }
            
            var jsonImg = new JsonImage();
            jsonImg.Load(path);
            var json = JsonConvert.SerializeObject(jsonImg);
            var outputText = await _client.PostAsync(json, "image");
            var objects = JsonConvert.DeserializeObject<JsonAnnotation>(outputText);
            if (objects != null || objects.Objects.Count > 0)
            {
                Console.WriteLine("File {0} contains:", Path.GetFileName(path));
                foreach (var ooj in objects.Objects)
                {
                    var x1 = ooj.Xmin;
                    var y1 = ooj.Ymin;
                    var x2 = ooj.Xmax;
                    var y2 = ooj.Ymax;
                    var score = ooj.Score;
                    var label = ooj.Name;
                    var rect = new BoundBox(
                        x1,
                        y1,
                        y2-y1,
                        x2-x1);
                    list.Add(rect);
                    Console.WriteLine("\t{0}: {1:P1}", label, double.Parse(score.Replace('.',',')));
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
            var loadTag = await GetLoadCurrentTag();
            var curTag = await GetInstalledCurrentTag();

            if (loadTag <= curTag)
            {
                Console.WriteLine($"everything is up to date: your version v{curTag} last version v{loadTag}");
                return;
            }
            
            Console.WriteLine($"find new retina-net version: your version v{curTag} last version v{loadTag}");
            Console.WriteLine("downloading new version...");
            await _docker.Initialize(tag: loadTag.ToString());
            Console.WriteLine("installing new version...");
            _id = await _docker.CreateContainer(tag: loadTag.ToString());
            Console.WriteLine("removing old version...");
            await _docker.Remove(tag: curTag.ToString());
            Console.WriteLine($"done! your version v{loadTag}");
        }

        public async Task<bool> CanUpdate()
        {
            return await GetLoadCurrentTag() > await GetInstalledCurrentTag();
        }
        
        public async Task Load()
        {
            var tag = await GetInstalledCurrentTag();
            if (tag < 0)
                tag = await GetLoadCurrentTag();
            Console.WriteLine($"loading retina-net v{tag}...");
            await _docker.Initialize(tag: tag.ToString());
            Console.WriteLine($"installing retina-net v{tag}...");
            _id = await _docker.CreateContainer(tag: tag.ToString());
            Console.WriteLine("done!");
        }

        private async Task<int> GetInstalledCurrentTag()
        {
            var maxTag = 1;
            var tags = await _docker.GetInstalledVersions();
            if (tags.Count < 1)
                return -1;
            foreach (var t in tags)
            {
                if (int.TryParse(t, out var tag))
                    maxTag = Math.Max(maxTag, tag);
            }
            Console.WriteLine(maxTag);
            return maxTag;
        }

        private async Task<int> GetLoadCurrentTag()
        {
            var tags = await _docker.GetTags();
            var maxTag = 1;
            foreach (var t in tags)
            {
                if (int.TryParse(t, out var tag))
                    maxTag = Math.Max(maxTag, tag);
            }
            return maxTag;
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