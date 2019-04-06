using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Text;
using ReactiveUI;

namespace RescuerLaApp.ViewModels
{
    public class ViewModelBase : ReactiveObject
    {
        public event PropertyChangedEventHandler PropertyChanged;

        protected void NotifyPropertyChanged(string propertyName)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }

    }
}
