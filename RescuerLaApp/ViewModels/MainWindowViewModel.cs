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
        private NeuroModel _model = null;
        
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
            
            // Add here newer commands
            IncreaseCanvasCommand = ReactiveCommand.Create(IncreaseCanvas);
            ShrinkCanvasCommand = ReactiveCommand.Create(ShrinkCanvas);
            PredictAllCommand = ReactiveCommand.Create(PredictAll);
            OpenFileCommand = ReactiveCommand.Create(OpenFile);
            SaveAllCommand = ReactiveCommand.Create(SaveAll);
        }

        public void UpdateFramesRepo()
        {
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
        
        public ReactiveCommand<Unit, Unit> SaveAllCommand { get; }
        
        #endregion

        private async void PredictAll()
        {
            if (Frames == null || Frames.Count < 1) return;
            Status = new AppStatusInfo()
            {
                Status = Enums.Status.Working, 
                StringStatus = $"Working | loading model..."
            };
            
            if (_model == null)
            {
                _model = new NeuroModel();
            }
            var isLoaded = await _model.Load();
            if (!isLoaded)
            {
                Status = new AppStatusInfo()
                {
                    Status = Enums.Status.Error, 
                    StringStatus = $"Error: unable to load model"
                };
                _model.Dispose();
                _model = null;
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
                frame.Rectangles = await _model.Predict(frame);
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
            UpdateUi();
        }
        
        private void ShrinkCanvas()
        {
            Zoomer.Zoom(0.8);
        }
        
        private void IncreaseCanvas()
        {
            Zoomer.Zoom(1.2);
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
                if (string.IsNullOrEmpty(dirName) || !Directory.Exists(dirName))
                {
                    Status = new AppStatusInfo() {Status = Enums.Status.Ready};
                    return;
                }
                var fileNames = Directory.GetFiles(dirName);
                _frameLoadProgressIndex = 0;
                Frames.Clear();
                var loadingFrames = new List<Frame>();
                foreach (var fileName in fileNames)
                {
                    // TODO: Проверка IsImage вне зависимости от расширений.
                    if(!Path.HasExtension(fileName))
                        continue;
                    if (Path.GetExtension(fileName).ToLower() != ".jpg" &&
                        Path.GetExtension(fileName).ToLower() != ".jpeg" &&
                        Path.GetExtension(fileName).ToLower() != ".png" &&
                        Path.GetExtension(fileName).ToLower() != ".bmp")
                        continue;
                    
                    var frame = new Frame();
                    frame.OnLoad += FrameLoadingProgressUpdate;
                    frame.Load(fileName, Enums.ImageLoadMode.Miniature);
                    loadingFrames.Add(frame);
                }
                if(loadingFrames.Count == 0)
                {
                    Status = new AppStatusInfo() {Status = Enums.Status.Ready};
                    return;
                }
                
                Frames = loadingFrames;
                if (SelectedIndex < 0)
                    SelectedIndex = 0;
                UpdateFramesRepo();
                UpdateUi();
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

        private async void SaveAll()
        {
            try
            {
                if (Frames == null || Frames.Count < 1)
                {
                    Status = new AppStatusInfo() {Status = Enums.Status.Ready};
                    return;
                }
                Status = new AppStatusInfo() {Status = Enums.Status.Working};
                var openDig = new OpenFolderDialog()
                {
                    Title = "Choose a directory to save annotations"
                };
                var dirName = await openDig.ShowAsync(new Window());
                if (string.IsNullOrEmpty(dirName) || !Directory.Exists(dirName))
                {
                    Status = new AppStatusInfo() {Status = Enums.Status.Ready};
                    return;
                }
                
                foreach (var frame in Frames)
                {
                    if (frame.Rectangles == null || frame.Rectangles.Count <= 0)
                        continue;
                    var annotation = new Annotation();
                    annotation.Filename = Path.GetFileNameWithoutExtension(frame.Patch);
                    annotation.Folder = Path.GetRelativePath(dirName, Path.GetDirectoryName(frame.Patch));
                    annotation.Segmented = 0;
                    frame.Load(frame.Patch);
                    annotation.Size = new Models.Size()
                    {
                        Depth = 3,
                        Height = frame.Height,
                        Width = frame.Width
                    };
                    foreach (var rectangle in frame.Rectangles)
                    {
                        var o = new Models.Object();
                        o.Name = "Pedestrian";
                        o.Box = new Box()
                        {
                            Xmax = rectangle.XBase + rectangle.WidthBase,
                            Ymax = rectangle.YBase + rectangle.HeightBase,
                            Xmin = rectangle.XBase,
                            Ymin = rectangle.YBase
                        };
                        annotation.Objects.Add(o);
                    }

                    annotation.SaveToXml(Path.Join(dirName,$"{annotation.Filename}.xml"));
                    Status = new AppStatusInfo() {Status = Enums.Status.Ready};
                }
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
            CanvasHeight = ImageBrush.Source.PixelSize.Height;
            CanvasWidth = ImageBrush.Source.PixelSize.Width;
            if (Frames[SelectedIndex].Rectangles != null && Frames[SelectedIndex].Rectangles.Count > 0)
            {
                BoundBoxes = new List<BoundBox>(Frames[SelectedIndex].Rectangles);
            }
            else
            {
                BoundBoxes = null;
            }
        }
    }
}
