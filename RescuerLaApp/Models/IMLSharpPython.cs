namespace RescuerLaApp.Models
{
    public interface IMlPythonServer
    {
        bool Run(string filePythonScript);
        void Stop();
    }
}