using System;
using System.Runtime.InteropServices;
using Avalonia;
using Avalonia.ReactiveUI;
using Avalonia.Rendering;
using RescuerLaApp.ViewModels;
using RescuerLaApp.Views;

namespace RescuerLaApp
{
    internal static class Program
    {
        private static void Main(string[] args)
        {
            Console.WriteLine("Lacmus desktop application. Version 0.3.1 alpha. \nCopyright (c) 2019 Georgy Perevozghikov <gosha20777@live.ru>\nGithub page: https://github.com/lizaalert/lacmus/.\nProvided by Yandex Cloud: https://cloud.yandex.com/.");
            Console.WriteLine("This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.");
            Console.WriteLine("This is free software, and you are welcome to redistribute it\nunder certain conditions; type `show c' for details.");
            Console.WriteLine("------------------------------------");
            BuildAvaloniaApp().StartWithClassicDesktopLifetime(args);
        }
        
        private static AppBuilder BuildAvaloniaApp()
        {
            bool useGpuLinux = true;

            var result = AppBuilder.Configure<App>();

            if (RuntimeInformation.IsOSPlatform(OSPlatform.Windows))
            {
                result
                    .UseWin32()
                    .UseSkia()
                    .UsePlatformDetect();
            }
            else
            {
                result.UsePlatformDetect();
            }

            // TODO remove this overriding of RenderTimer when Avalonia 0.9 is released.
            // fixes "Thread Leak" issue in 0.8.1 Avalonia.
            var old = result.WindowingSubsystemInitializer;

            result.UseWindowingSubsystem(() =>
            {
                old();

                AvaloniaLocator.CurrentMutable.Bind<IRenderTimer>().ToConstant(new DefaultRenderTimer(60));
            });
            
            result.UseReactiveUI();
            
            return result
                .With(new Win32PlatformOptions { AllowEglInitialization = true, UseDeferredRendering = true })
                .With(new X11PlatformOptions { UseGpu = useGpuLinux, WmClass = "lacmus" })
                .With(new AvaloniaNativePlatformOptions { UseDeferredRendering = true, UseGpu = true })
                .With(new MacOSPlatformOptions { ShowInDock = true });
        }

        /*
        public static AppBuilder BuildAvaloniaApp()
            => AppBuilder.Configure<App>()
                .UsePlatformDetect()
                .UseReactiveUI()
                .LogToDebug();
        */
    }
}
