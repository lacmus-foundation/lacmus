using System;
using System.Collections.Generic;
using System.ComponentModel;

namespace RescuerLaApp.Models
{
    public static class SimpleCommandManager
    {
        private static List<Action> _raiseCanExecuteChangedActions = new List<Action>();

        public static void AddRaiseCanExecuteChangedAction(ref Action raiseCanExecuteChangedAction)
        {
            _raiseCanExecuteChangedActions.Add(raiseCanExecuteChangedAction);
        }

        public static void RemoveRaiseCanExecuteChangedAction(Action raiseCanExecuteChangedAction)
        {
            _raiseCanExecuteChangedActions.Remove(raiseCanExecuteChangedAction);
        }

        public static void AssignOnPropertyChanged(ref PropertyChangedEventHandler propertyEventHandler)
        {
            propertyEventHandler += OnPropertyChanged;
        }

        private static void OnPropertyChanged(object sender, PropertyChangedEventArgs e)
        {
            if (e.PropertyName != "CanExecute")
            {
                RefreshCommandStates();
            }
        }

        public static void RefreshCommandStates()
        {
            foreach (var raiseCanExecuteChangedAction in _raiseCanExecuteChangedActions)
            {
                raiseCanExecuteChangedAction?.Invoke();
            }
        }
    }
}