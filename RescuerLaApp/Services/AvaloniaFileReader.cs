using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using Avalonia.Controls;

namespace RescuerLaApp.Services
{
    public class AvaloniaFileReader : Interfaces.IFileReader
    {
        private readonly Window _window;
        
        public async Task<(string Name, Stream Stream)> Read()
        {
            var fileDialog = new OpenFileDialog {AllowMultiple = false};
            var files = await fileDialog.ShowAsync(_window);
            var path = files.First();
            
            var attributes = File.GetAttributes(path);
            var isFolder = attributes.HasFlag(FileAttributes.Directory);
            if (isFolder) throw new Exception("Folders are not supported.");

            var stream = File.OpenRead(path);
            var name = Path.GetFileName(path);
            return (name, stream);
        }

        public async Task<(string Name, Stream Stream)[]> ReadMultiple()
        {
            var fileDialog = new OpenFileDialog {AllowMultiple = true};
            var files = await fileDialog.ShowAsync(_window);
            var result = new List<(string Name, Stream Stream)>();
            foreach (var file in files)
            {
                var attributes = File.GetAttributes(file);
                var isFolder = attributes.HasFlag(FileAttributes.Directory);
                if (isFolder) throw new Exception("Folders are not supported.");
                var stream = File.OpenRead(file);
                var name = Path.GetFileName(file);
                result.Add((name, stream));
            }
            return  result.ToArray();
        }

        public async Task<(string Name, Stream Stream)[]> ReadAllFromDir(bool isRecursive = false)
        {
            var fileDialog = new OpenFileDialog {AllowMultiple = false};
            var dirPaths = await fileDialog.ShowAsync(_window);
            var dirPath = dirPaths.First();
            
            var attributes = File.GetAttributes(dirPath);
            var isFolder = attributes.HasFlag(FileAttributes.Directory);
            if (!isFolder) throw new Exception("Files are not supported.");
            
            var files = GetFilesFromDir(dirPath, isRecursive);
            var result = new List<(string Name, Stream Stream)>();
            foreach (var file in files)
            {
                var stream = File.OpenRead(file);
                var name = Path.GetFileName(file);
                result.Add((name, stream));
            }
            return  result.ToArray();
        }

        //TODO: Create Recursive Search
        private static IEnumerable<string> GetFilesFromDir(string dirPath, bool isRecursive)
        {
            return Directory.GetFiles(dirPath);
        }
    }
}