using Avalonia.Media;
using System;
using System.Collections.Generic;
using System.Text;
using Avalonia.Styling;
using static RescuerLaApp.Models.Enums;

namespace RescuerLaApp.Models
{
    public class AppStatus
    {
        private TStatus _status;

        public TStatus Status
        {
            get { return _status; }
            set
            {
                this._status = value;
                this.StringStatus = this.Status.ToString();
                this.StatusColor = GetColor();
            }
        }
        public string StringStatus { get; set; }
        public ISolidColorBrush StatusColor { get; private set; }

        private ISolidColorBrush GetColor()
        {
            switch (this._status)
            {
                case TStatus.Ready: return new SolidColorBrush(Color.FromRgb(0, 128, 255));
                case TStatus.Success: return new SolidColorBrush(Color.FromRgb(0, 135, 60));
                case TStatus.Working: return new SolidColorBrush(Color.FromRgb(226, 90, 0));
                case TStatus.Error: return new SolidColorBrush(Color.FromRgb(216, 14, 0)); 
                default: return new SolidColorBrush(0x007ED8);
            }
        }
    }
}
