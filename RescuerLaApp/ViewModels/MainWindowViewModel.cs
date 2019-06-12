using Avalonia.Media;
using RescuerLaApp.Models;
using System;
using System.Collections.Generic;
using System.IO;
using System.Reactive;
using System.Reactive.Linq;
using Avalonia.Controls;
using Avalonia.Media.Imaging;
using ReactiveUI;
using ReactiveUI.Fody.Helpers;
using Newtonsoft.Json;

namespace RescuerLaApp.ViewModels
{
    public class MainWindowViewModel : ReactiveObject
    {
        private int _frameLoadProgressIndex;
        
        public MainWindowViewModel()
        {
            var canGoNext = this
                .WhenAnyValue(x => x.SelectedIndex)
                .Select(index => index < Frames.Count - 1);
            
            // The bound button will stay disabled, when
            // there is no more frames left.
            NextImageCommand = ReactiveCommand.Create(
                () => { SelectedIndex++; },
                canGoNext);

            var canGoBack = this
                .WhenAnyValue(x => x.SelectedIndex)
                .Select(index => index > 0);
            
            // The bound button will stay disabled, when
            // there are no frames before the current one.
            PrevImageCommand = ReactiveCommand.Create(
                () => { SelectedIndex--; }, 
                canGoBack);
            
            IncreaseCanvasCommand = ReactiveCommand.Create(IncreaseCanvas);
            ShrinkCanvasCommand = ReactiveCommand.Create(ShrinkCanvas);
            PredictAllCommand = ReactiveCommand.Create(PredictAll);
            OpenFileCommand = ReactiveCommand.Create(OpenFile);

            this.WhenAnyValue(x => x.SelectedIndex)
                .Skip(1)
                .Subscribe(x =>
                {
                    if (Status.Status == Enums.Status.Ready)
                        Status = new AppStatusInfo
                        {
                            Status = Enums.Status.Ready, 
                            StringStatus = $"{Enums.Status.Ready.ToString()} | {Frames[SelectedIndex].Patch}"
                        };
                    UpdateUi();
                });
        }
        
        #region Public API

        [Reactive] public List<BoundBox> BoundBoxes { get; set; } = new List<BoundBox>();
        
        [Reactive] public double CanvasWidth { get; set; } = 500;
        
        [Reactive] public double CanvasHeight { get; set; } = 500;
        
        [Reactive] public int SelectedIndex { get; set; } = 0;
        
        [Reactive] public List<Frame> Frames { get; set; } = new List<Frame>();
        
        [Reactive] public AppStatusInfo Status { get; set; } = new AppStatusInfo { Status = Enums.Status.Ready };
        
        [Reactive] public ImageBrush ImageBrush { get; set; } = new ImageBrush { Stretch = Stretch.Uniform };
        
        public ReactiveCommand<Unit, Unit> PredictAllCommand { get; }
        
        public ReactiveCommand<Unit, Unit> NextImageCommand { get; }
        
        public ReactiveCommand<Unit, Unit> PrevImageCommand { get; }
        
        public ReactiveCommand<Unit, Unit> ShrinkCanvasCommand { get; }
        
        public ReactiveCommand<Unit, Unit> IncreaseCanvasCommand { get; }
        
        public ReactiveCommand<Unit, Unit> OpenFileCommand { get; }
        
        #endregion

        private async void PredictAll()
        {
            if (Frames == null || Frames.Count < 1) return;
            using (var model = new NeuroModel())
            {
                var isLoaded = await model.Load();
                if (!isLoaded)
                {
                    Status = new AppStatusInfo()
                    {
                        Status = Enums.Status.Error, 
                        StringStatus = $"Error: unable to load model"
                    };
                    return;
                }
                    
                var index = 0;
                Status = new AppStatusInfo()
                {
                    Status = Enums.Status.Working, 
                    StringStatus = $"Working | processing images: {index} / {Frames.Count}"
                };
                foreach (var frame in Frames)
                {
                    index++;
                    frame.Rectangles = await model.Predict(frame);
                    if(index < Frames.Count)
                        Status = new AppStatusInfo()
                        {
                            Status = Enums.Status.Working, 
                            StringStatus = $"Working | processing images: {index} / {Frames.Count}"
                        };
                    else
                    {
                        Status = new AppStatusInfo()
                        {
                            Status = Enums.Status.Ready
                        };
                    }
                }
            }
            UpdateUi();
        }
        
        private void ShrinkCanvas()
        {
            CanvasWidth -= CanvasWidth * 0.25;
            CanvasHeight -= CanvasHeight * 0.25;
            UpdateUi();
        }
        
        private void IncreaseCanvas()
        {
            CanvasWidth += CanvasWidth * 0.25;
            CanvasHeight += CanvasHeight * 0.25;
            UpdateUi();
        }

        private async void OpenFile()
        {
            Status = new AppStatusInfo() {Status = Enums.Status.Working};
            try
            {
                var openDig = new OpenFolderDialog()
                {
                    Title = "Choose a directory with images"
                };
                var dirName = await openDig.ShowAsync(new Window());
                if (string.IsNullOrEmpty(dirName))
                {
                    Status = new AppStatusInfo() {Status = Enums.Status.Ready};
                    return;
                }
                var fileNames = Directory.GetFiles(dirName);
                _frameLoadProgressIndex = 0;
                Frames = new List<Frame>();
                foreach (var fileName in fileNames)
                {
                    var frame = new Frame();
                    frame.OnLoad += FrameLoadingProgressUpdate;
                    frame.Load(fileName, Enums.ImageLoadMode.Miniature);
                    Frames.Add(frame);
                }
                
                
                Frames = new List<Frame>(Frames);
                if (SelectedIndex < 0)
                    SelectedIndex = 0;
            }
            catch (Exception ex)
            {
                Status = new AppStatusInfo()
                {
                    Status = Enums.Status.Error, 
                    StringStatus = $"Error | {ex.Message.Replace('\n', ' ')}"
                };
            }
        }

        private void FrameLoadingProgressUpdate()
        {
            _frameLoadProgressIndex++;
            if(_frameLoadProgressIndex < Frames.Count)
                Status = new AppStatusInfo()
                {
                    Status = Enums.Status.Working, 
                    StringStatus = $"Working | loading images: {_frameLoadProgressIndex} / {Frames.Count}"
                };
            else
            {
                Status = new AppStatusInfo()
                {
                    Status = Enums.Status.Ready
                };
            }
        }

        private void UpdateUi()
        {
            /*TODO: Вынести сюда все функции обновления UI*/
            ImageBrush.Source = new Bitmap(Frames[SelectedIndex].Patch); //replace to frame.load(...)
            CanvasHeight = CanvasWidth * ImageBrush.Source.PixelSize.Height / ImageBrush.Source.PixelSize.Width;
            //Frames[SelectedIndex].Resize(CanvasWidth, CanvasHeight);
            if (Frames[SelectedIndex].Rectangles != null && Frames[SelectedIndex].Rectangles.Count > 0)
            {
                var scaleX = CanvasWidth / ImageBrush.Source.PixelSize.Width;
                var scaleY = CanvasHeight / ImageBrush.Source.PixelSize.Height;
                Console.WriteLine($"{ImageBrush.Source.PixelSize.Width} x {ImageBrush.Source.PixelSize.Height}");
                Console.WriteLine($"{CanvasWidth} x {CanvasHeight}");
                foreach (var box in Frames[SelectedIndex].Rectangles)
                {
                    box.Update(scaleX, scaleY);
                }
                BoundBoxes = new List<BoundBox>(Frames[SelectedIndex].Rectangles);
            }
            else
            {
                BoundBoxes = null;
            }
        }
    }
}
