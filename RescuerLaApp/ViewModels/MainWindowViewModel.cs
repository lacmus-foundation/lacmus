using Avalonia.Media;
using RescuerLaApp.Models;
using System;
using System.Collections.Generic;
using System.Text;

namespace RescuerLaApp.ViewModels
{
    public class MainWindowViewModel : ViewModelBase
    {
        public AppStatus Status { get; set; } = new AppStatus() { Status = Enums.TStatus.Working };
    }
}
