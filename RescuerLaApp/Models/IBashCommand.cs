namespace RescuerLaApp.Models
{
    public interface IBashCommand
    {
        string Execute(string command, out string standardError);
    }
}