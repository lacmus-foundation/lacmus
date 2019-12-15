using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace RescuerLaApp.Models
{
    public interface INeuroModel : IDisposable
    {
        Task<bool> Run();
        Task<List<BoundBox>> Predict(string path);
        Task Stop();
        Task UpdateModel();
        Task<bool> CanUpdate();
        Task Load();
    }
}