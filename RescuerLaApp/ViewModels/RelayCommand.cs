using System;
using System.Windows.Input;
using RescuerLaApp.Models;

namespace RescuerLaApp.ViewModels
{
    public class RelayCommand : ICommand
    {
        private readonly Action _execute;
        private readonly Func<bool> _canExecute;

        public RelayCommand(Action execute, Func<bool> canExecute = null)
        {
            _execute = execute ?? throw new ArgumentNullException(nameof(execute));
            _canExecute = canExecute;
            _raiseCanExecuteChangedAction = RaiseCanExecuteChanged;
            SimpleCommandManager.AddRaiseCanExecuteChangedAction(ref _raiseCanExecuteChangedAction);
        }

        ~RelayCommand()
        {
            RemoveCommand();
        }

        public void RemoveCommand()
        {
            SimpleCommandManager.RemoveRaiseCanExecuteChangedAction(_raiseCanExecuteChangedAction);
        }

        bool ICommand.CanExecute(object parameter)
        {
            return CanExecute;
        }

        public void Execute(object parameter)
        {
            _execute();
            SimpleCommandManager.RefreshCommandStates();
        }

        public bool CanExecute => _canExecute == null || _canExecute();

        public void RaiseCanExecuteChanged()
        {
            var handler = CanExecuteChanged;
            handler?.Invoke(this, new EventArgs());
        }

        private readonly Action _raiseCanExecuteChangedAction;

        public event EventHandler CanExecuteChanged;
    }
}