using Avalonia.Media;
using RescuerLaApp.Models;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.IO;
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
        private double _canvasHeight = 500;
        private double _canvasWidth = 500;
        private int _selectedIndex = 0;
        private List<Frame> _frames = new List<Frame>();
        private List<BoundBox> _boundBoxes = new List<BoundBox>();

        public List<BoundBox> BoundBoxes
        {
            get => _boundBoxes; 
            set => this.RaiseAndSetIfChanged(ref _boundBoxes, value);
        }

        public double CanvasWidth
        {
            get => _canvasWidth;
            set => this.RaiseAndSetIfChanged(ref _canvasWidth, value);
        }

        public double CanvasHeight
        {
            get => _canvasHeight;
            set => this.RaiseAndSetIfChanged(ref _canvasHeight, value);
        }

        public int SelectedIndex
        {
            get => _selectedIndex;
            set
            {
                this.RaiseAndSetIfChanged(ref _selectedIndex, value);
                ImageBrush.Source = new Bitmap(Frames[SelectedIndex].Patch);
                CanvasHeight = CanvasWidth * ImageBrush.Source.PixelSize.Height / ImageBrush.Source.PixelSize.Width;
                this.BoundBoxes = Frames[SelectedIndex].Rectangles;
                if(this.Status.Status != Enums.TStatus.Error)
                    this.Status = new AppStatus()
                    {
                        Status = Enums.TStatus.Ready, 
                        StringStatus = $"{Enums.TStatus.Ready.ToString()} | {Frames[SelectedIndex].Patch}"
                    };
            }
        }
        public List<Frame> Frames
        {
            get { return _frames; }
            set { this.RaiseAndSetIfChanged(ref _frames, value); }
        }
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
        private RelayCommand _increaseCanvasCommand;
        private RelayCommand _shrinkCanvasCommand;
        private RelayCommand _nextImageCommand;
        private RelayCommand _prevImageCommand;
        private RelayCommand _predictAllCommand;
        private ImageBrush _imageBrush =  new ImageBrush() { Stretch = Stretch.Uniform };
        private AppStatus _status = new AppStatus() { Status = Enums.TStatus.Ready };

        public ICommand PredictAllCommand
        {
            get
            {
                if (_predictAllCommand == null)
                {
                    _predictAllCommand = new RelayCommand(PredictAll);
                }
                return _predictAllCommand;
            }
        } 
        private void PredictAll()
        {
            using (var model = new NeuroModel())
            {
                model.Initialize();
                foreach (var frame in _frames)
                {
                    frame.Rectangles = model.Predict(frame.Bitmap);
                }
            }

            this.BoundBoxes = Frames[SelectedIndex].Rectangles;
        }
        public ICommand NextImageCommand
        {
            get
            {
                if (_nextImageCommand == null)
                {
                    _nextImageCommand = new RelayCommand(NextImage);
                }
                return _nextImageCommand;
            }
        }
        
        public ICommand PrevImageCommand
        {
            get
            {
                if (_prevImageCommand == null)
                {
                    _prevImageCommand = new RelayCommand(PrevImage);
                }
                return _prevImageCommand;
            }
        }

        private void NextImage()
        {
            if (SelectedIndex < Frames.Count - 1)
                SelectedIndex++;
        }
        private void PrevImage()
        {
            if (SelectedIndex > 0)
                SelectedIndex--;
        }
        public ICommand ShrinkCanvasCommand
        {
            get
            {
                if (_shrinkCanvasCommand == null)
                {
                    _shrinkCanvasCommand = new RelayCommand(ShrinkCanvas);
                }
                return _shrinkCanvasCommand;
            }
        }

        private void ShrinkCanvas()
        {
            this.CanvasWidth -= CanvasWidth * 0.25;
            this.CanvasHeight -= CanvasHeight * 0.25;
        }
        public ICommand IncreaseCanvasCommand
        {
            get
            {
                if (_increaseCanvasCommand == null)
                {
                    _increaseCanvasCommand = new RelayCommand(IncreaseCanvas);
                }
                return _increaseCanvasCommand;
            }
        }

        private void IncreaseCanvas()
        {
            this.CanvasWidth += CanvasWidth * 0.25;
            this.CanvasHeight += CanvasHeight * 0.25;
        }

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
                var openDig = new OpenFolderDialog()
                {
                    Title = "Choose a directory with images"
                };
                var dirName = await openDig.ShowAsync();
                if (string.IsNullOrEmpty(dirName))
                {
                    this.Status = new AppStatus() {Status = Enums.TStatus.Ready};
                    return;
                }
                var fileNames = Directory.GetFiles(dirName);
                _frames = new List<Frame>();
                foreach (var fileName in fileNames)
                {
                    Console.WriteLine(fileName);
                    var frame = new Frame();
                    frame.Load(fileName, Enums.TImageLoadMode.Miniature);
                    _frames.Add(frame);
                }
                Frames = new List<Frame>(_frames);
                this.Status = new AppStatus() {Status = Enums.TStatus.Ready};
                if (SelectedIndex < 0)
                    SelectedIndex = 0;
            }
            catch (Exception ex)
            {
                this.Status = new AppStatus()
                {
                    Status = Enums.TStatus.Error, 
                    StringStatus = $"Error | {ex.Message.Replace('\n', ' ')}"
                };
            }
        }
    }
}
