using System;
using System.Diagnostics;
using System.Reactive.Disposables;

namespace RescuerLaApp.Models
{
    public class MlSharpPython : IMlPythonServer
    {
        private readonly string _filePythonExePath;
        private Process _process;

        /// <summary>
        /// ML Sharp Python class constructor
        /// </summary>
        /// <param name="exePythonPath">Python exec file path</param>
        public MlSharpPython(string exePythonPath)
        {
            _filePythonExePath = exePythonPath;
        }

        /// <summary>
        /// Execute Python script file
        /// </summary>
        /// <param name="filePythonScript">Python script file and input parameter(s)</param>
        /// <returns>Output text result</returns>
        public bool Run(string filePythonScript)
        {
            try
            {
                _process = new Process();
                Console.WriteLine($">>>{_filePythonExePath} {filePythonScript}");
                _process.StartInfo = new ProcessStartInfo(_filePythonExePath)
                {
                    Arguments = filePythonScript,
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    CreateNoWindow = true                        
                };
                var success = _process.Start();
                if(!success)
                    throw new Exception();
                var startTime = DateTime.Now;
                TimeSpan waitingTime = new TimeSpan(0, 0, 0, 20);
                var sr = _process.StandardOutput;
                var or = _process.StandardError;
                while (!sr.EndOfStream)
                {
                    String s = sr.ReadLine();
                    string e = or.ReadLine();
                    if(s != null)
                        Console.WriteLine($"std>> {DateTime.Now} {s}");
                    if(e != null)
                        Console.WriteLine($"err>> {DateTime.Now} {e}");
                    
                    if (s != null && s.Contains("model loaded"))
                        return true;
                    if (DateTime.Now - startTime > waitingTime)
                    {
                        Console.WriteLine("timeout");
                        return false;
                    }
                        
                }
            }
            catch (Exception ex)
            {
                /*TODO: Сделать нормальный exception*/
                Console.WriteLine(ex.Message);
            }
            return false;
        }

        public void Stop()
        {
            _process.Kill();
            _process.Dispose();
            Console.Write("killed");
        }
    }
}