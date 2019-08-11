using System;
using System.Threading.Tasks;
using Avalonia;
using Avalonia.Logging.Serilog;
using RescuerLaApp.ViewModels;
using RescuerLaApp.Views;

namespace RescuerLaApp
{
    internal static class Program
    {
        private static void Main(string[] args)
        {
            BuildAvaloniaApp().Start<MainWindow>(() => new MainWindowViewModel());
        }

        public static AppBuilder BuildAvaloniaApp()
            => AppBuilder.Configure<App>()
                .UsePlatformDetect()
                .UseReactiveUI()
                .LogToDebug();
    }
}
