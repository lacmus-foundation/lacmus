using Avalonia;
using Avalonia.Markup.Xaml;
using RescuerLaApp.ViewModels;
using RescuerLaApp.Views;

namespace RescuerLaApp
{
    public class App : Application
    {
        public override void Initialize() => AvaloniaXamlLoader.Load(this);

        public override void OnFrameworkInitializationCompleted()
        {
            var view = new MainWindow();
            var context = new MainWindowViewModel(view);
            view.DataContext = context;
            view.Show();
            base.OnFrameworkInitializationCompleted();
        }
    }
}
