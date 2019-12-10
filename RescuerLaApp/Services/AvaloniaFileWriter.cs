using System.IO;
using System.Threading.Tasks;
using Avalonia.Controls;

namespace RescuerLaApp.Services
{
    public class AvaloniaFileWriter : Interfaces.IFileWriter
    {
        private readonly Window _window;
        
        public Task<Stream> Write(string name)
        {
            throw new System.NotImplementedException();
        }
    }
}