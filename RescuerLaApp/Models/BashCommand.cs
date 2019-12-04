using System.Diagnostics;

namespace RescuerLaApp.Models
{
    public class BashCommand : IBashCommand
    {
        public string Execute(string command, out string standardError)
        {
            var outputText = string.Empty;
            standardError = string.Empty;
            try
            {
                using (var process = new Process())
                {
                    process.StartInfo = new ProcessStartInfo
                    {
                        FileName = "/bin/bash",
                        Arguments = $"-c \"{command}\"",
                        UseShellExecute = false,
                        RedirectStandardOutput = true,
                        RedirectStandardError = true,
                        CreateNoWindow = true                        
                    };
                    process.Start();
                    outputText = process.StandardOutput.ReadToEnd();
                    standardError = process.StandardError.ReadToEnd();
                    process.WaitForExit();
                }
            }
            catch
            {
                
            }
            return outputText;
        }
    }
}