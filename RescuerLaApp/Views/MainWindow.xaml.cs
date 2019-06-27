using Avalonia;
using Avalonia.Controls;
using Avalonia.Controls.PanAndZoom;
using Avalonia.Input;
using Avalonia.Markup.Xaml;
using RescuerLaApp.ViewModels;
using ReactiveUI;
using RescuerLaApp.Models;

namespace RescuerLaApp.Views
{
    public sealed class MainWindow : ReactiveWindow<MainWindowViewModel>
    {
        ZoomBorder z = new ZoomBorder();
        public MainWindow()
        {
            AvaloniaXamlLoader.Load(this);
            this.WhenActivated(disposables => { });
#if DEBUG
            this.AttachDevTools();
#endif
            Zoomer.Init(this.Find<ZoomBorder>("zoomBorder"));
            Zoomer.KeyDown += ZoomBorder_KeyDown;
        }

        private void ZoomBorder_KeyDown(object sender, KeyEventArgs e)
        {
            if (e.Key == Key.R)
            {
                Zoomer.Reset();
            }
        }
    }
}
