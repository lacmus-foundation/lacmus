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
            Console.WriteLine("Lacmus desktop application. Version 0.2.6 alpha. \nCopyright (c) 2019 Georgy Perevozghikov <gosha20777@live.ru>\nGithub page: https://github.com/lizaalert/lacmus/.\nProvided by Yandex Cloud: https://cloud.yandex.com/.");
            Console.WriteLine("This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.");
            Console.WriteLine("This is free software, and you are welcome to redistribute it\nunder certain conditions; type `show c' for details.");
            Console.WriteLine("------------------------------------");
            BuildAvaloniaApp().Start<MainWindow>(() => new MainWindowViewModel());
        }

        public static AppBuilder BuildAvaloniaApp()
            => AppBuilder.Configure<App>()
                .UsePlatformDetect()
                .UseReactiveUI()
                .LogToDebug();
    }
}
