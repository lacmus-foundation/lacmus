using Avalonia;
using Avalonia.Markup.Xaml;

namespace RescuerLaApp
{
    public class App : Application
    {
        public override void Initialize()
        {
            AvaloniaXamlLoader.Load(this);
        }
    }
}
