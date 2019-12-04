using System.Collections.Generic;
using System.Threading.Tasks;

namespace RescuerLaApp.Models
{
    internal class NeuroModelMock : INeuroModel
    {
        public async Task<bool> Run()
        {
            return true;
        }

        public async Task<List<BoundBox>> Predict(string path)
        {
            return new List<BoundBox> { new BoundBox(100, 100, 40, 40), new BoundBox(200, 300, 40, 40), new BoundBox(300, 200, 40, 40) };
        }

        public async Task Stop()
        {
        }

        public async Task UpdateModel()
        {
        }

        public async Task<bool> CanUpdate()
        {
            return true;
        }

        public async Task Load()
        {
        }

        public void Dispose()
        {
        }
    }
}