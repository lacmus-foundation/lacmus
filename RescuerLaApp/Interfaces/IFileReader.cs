using System.IO;
using System.Threading.Tasks;

namespace RescuerLaApp.Interfaces
{
    public interface IFileReader
    {
        Task<(string Name, Stream Stream)> Read();
        Task<(string Name, Stream Stream)[]> ReadMultiple();
        Task<(string Name, Stream Stream)[]> ReadAllFromDir(bool isRecursive = false);
    }
}