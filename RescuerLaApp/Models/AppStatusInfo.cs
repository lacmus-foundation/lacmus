using System;
using Avalonia.Media;
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
                case Status.Unauthenticated: return new SolidColorBrush(Color.FromRgb(120, 0, 120));
                default: throw new Exception($"Invalid app status {_status.ToString()}");
            }
        }
    }
}
