using Avalonia.Media;
using System;
using System.Collections.Generic;
using System.Text;
using Avalonia.Styling;
using static RescuerLaApp.Models.Enums;

namespace RescuerLaApp.Models
{
    public class AppStatusInfo
    {
        private Status _status;

        public Status Status
        {
            get => _status;
            set
            {
                _status = value;
                StringStatus = Status.ToString();
                StatusColor = GetColor();
            }
        }
        public string StringStatus { get; set; }
        public ISolidColorBrush StatusColor { get; private set; }

        private ISolidColorBrush GetColor()
        {
            switch (_status)
            {
                case Status.Ready: return new SolidColorBrush(Color.FromRgb(0, 128, 255));
                case Status.Success: return new SolidColorBrush(Color.FromRgb(0, 135, 60));
                case Status.Working: return new SolidColorBrush(Color.FromRgb(226, 90, 0));
                case Status.Error: return new SolidColorBrush(Color.FromRgb(216, 14, 0)); 
                default: throw new Exception($"Invalid app status {_status}");
            }
        }
    }
}
