using Avalonia.Media;
using RescuerLaApp.Models;
using System;
using System.Collections.Generic;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Input;
using Avalonia.Controls;
using Avalonia.Media.Imaging;
using ReactiveUI;

namespace RescuerLaApp.ViewModels
{
    public class MainWindowViewModel : ViewModelBase
    {
        public AppStatus Status
        {
            get => _status;
            set => this.RaiseAndSetIfChanged(ref _status, value);
        }
        public ImageBrush ImageBrush
        {
            get => _imageBrush;
            set => this.RaiseAndSetIfChanged(ref _imageBrush, value);
        }
        
        private RelayCommand _openFieCommand;
        private ImageBrush _imageBrush =  new ImageBrush() { Stretch = Stretch.Uniform };
        private AppStatus _status = new AppStatus() { Status = Enums.TStatus.Ready };

        public ICommand OpenFileCommand
        {
            get
            {
                if (_openFieCommand == null)
                {
                    _openFieCommand = new RelayCommand(OpenFile);
                }
                return _openFieCommand;
            }
        }

        private async void OpenFile()
        {
            this.Status = new AppStatus() {Status = Enums.TStatus.Working};
            try
            {
                var openDig = new OpenFileDialog
                {
                    Title = "Выбирете файл...",
                    AllowMultiple = false,
                    Filters = new List<FileDialogFilter>()
                        { new FileDialogFilter(){ Name = "Картинки (*.png; *.jpg;)|*.png;*.jpg;" } }
                };
                string[] fileNames = await openDig.ShowAsync();
                Frame frame = new Frame();
                frame.Load(fileNames[0]);
                ImageBrush = new ImageBrush()
                {
                    Source = new Bitmap(fileNames[0])
                };
            }
            catch (Exception ex)
            {
                //MessageBox.Show(ex.Message, "Ошибка", MessageBoxButton.OK, MessageBoxImage.Error);
            }
            this.Status = new AppStatus() {Status = Enums.TStatus.Ready};
        }
    }
}
