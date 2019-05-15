using System;
using System.Diagnostics;

namespace RescuerLaApp.Models
{
    public class MlSharpPython : IMlSharpPython
    {
        private readonly string _filePythonExePath;

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
        /// <param name="standardError">Output standard error</param>
        /// <returns>Output text result</returns>
        public string ExecutePythonScript(string filePythonScript)
        {
            var outputText = string.Empty;
            var standardError = string.Empty;
            try
            {
                using (var process = new Process())
                {
                    process.StartInfo = new ProcessStartInfo(_filePythonExePath)
                    {
                        Arguments = filePythonScript,
                        UseShellExecute = false,
                        RedirectStandardOutput = true,
                        RedirectStandardError = true,
                        CreateNoWindow = true                        
                    };
                    var sucsess = process.Start();
                    outputText = process.StandardOutput.ReadToEnd();
                    standardError = process.StandardError.ReadToEnd();
                    process.WaitForExit();
                    if(!sucsess)
                        throw new Exception(standardError);
                }
            }
            catch (Exception ex)
            {
                /*TODO: Сделать нормальный exception*/
                Console.WriteLine(ex.Message);
            }
            //Console.WriteLine(filePythonScript + filePythonScript);
            //Console.WriteLine("txt = "+outputText);
            //Console.WriteLine("err = "+standardError);
            //Console.WriteLine("DONE");
            return outputText;
        }
    }
}