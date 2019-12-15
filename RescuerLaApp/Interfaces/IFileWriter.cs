using System.IO;
using System.Threading.Tasks;

namespace RescuerLaApp.Interfaces
{
    public interface IFileWriter
    {
        Task<Stream> Write(string name);
    }
}