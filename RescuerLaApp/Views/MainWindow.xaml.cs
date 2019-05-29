using Avalonia;
using Avalonia.Markup.Xaml;
using RescuerLaApp.ViewModels;
using ReactiveUI;

namespace RescuerLaApp.Views
{
    public sealed class MainWindow : ReactiveWindow<MainWindowViewModel>
    {
        public MainWindow()
        {
            AvaloniaXamlLoader.Load(this);
            this.WhenActivated(disposables => { });
#if DEBUG
            this.AttachDevTools();
#endif
        }
    }
}
