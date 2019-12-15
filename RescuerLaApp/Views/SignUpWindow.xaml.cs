using System;
using System.IO;
using System.Threading.Tasks;
using Avalonia.Controls;
using Avalonia.Markup.Xaml;
using MessageBox.Avalonia;
using MessageBox.Avalonia.DTO;
using MessageBox.Avalonia.Enums;
using Newtonsoft.Json;
using RescuerLaApp.Models;

namespace RescuerLaApp.Views
{
    class SignUpWindow : Window
    {
        [JsonObject]
        public class SignUpResult
        {
            [JsonProperty("email")]
            public string Email { get; set; }
            [JsonProperty("passwordHash")]
            public string PasswordHash { get; set; }
            [JsonProperty("id")]
            public int Id { get; set; }
            [JsonProperty("time")]
            public string Time { get; set; }

            public bool IsSignIn { get; set; }
        }

        public SignUpWindow()
        {
            AvaloniaXamlLoader.Load(this);
        }

        public static Task<SignUpResult> Show(Window parent)
        {
            var title = "Create Account";
            var msgbox = new SignUpWindow
            {
                Title = title
            };
            var buttonPanel = msgbox.FindControl<StackPanel>("Buttons");

            SignUpResult res = new SignUpResult();

            void AddButton(string caption)
            {
                var btn = new Button {Content = caption};
                btn.Click += (_, __) =>
                {
                    var nickName = msgbox.FindControl<TextBox>("tbNickName").Text;
                    var passwordHash = msgbox.FindControl<TextBox>("tbPassword").Text;
                    var email = msgbox.FindControl<TextBox>("tbEmail").Text;
                    var firstName = msgbox.FindControl<TextBox>("tbFirstName").Text;
                    var lastName = msgbox.FindControl<TextBox>("tbLastName").Text;
                    if (string.IsNullOrWhiteSpace(nickName))
                    {
                        ShowError("Incorrect Nick name");
                        return;
                    }
                    if (string.IsNullOrWhiteSpace(passwordHash) || passwordHash.Length < 6)
                    {
                        ShowError("Incorrect Password");
                        return;
                    }
                    if (string.IsNullOrWhiteSpace(firstName))
                    {
                        ShowError("Incorrect First name");
                        return;
                    }
                    if (string.IsNullOrWhiteSpace(lastName))
                    {
                        ShowError("Incorrect Last name");
                        return;
                    }
                    if (string.IsNullOrWhiteSpace(email) || !email.Contains('@') || !email.Contains('.'))
                    {
                        ShowError("Incorrect Email");
                        return;
                    }
                    
                    PasswordHasher hasher = new PasswordHasher();
                    passwordHash = hasher.GenerateIdentityV3Hash(passwordHash);
                    
                    res = new SignUpResult
                    {
                        Email = email,
                        PasswordHash = passwordHash,
                        Id = 1,
                        Time = DateTime.Now.ToString()
                    };

                    var path = AppDomain.CurrentDomain.BaseDirectory + "user_info";
                    if (File.Exists(path))
                    {
                        ShowInfo("You already signed up. Please log in.");
                        msgbox.Close();
                        return;
                    }

                    res.IsSignIn = true;
                    
                    File.AppendAllText(
                        path,
                        JsonConvert.SerializeObject(res));
                    msgbox.Close();
                };
                buttonPanel.Children.Add(btn);
            }
            
            AddButton("Sign Up");
            var tcs = new TaskCompletionSource<SignUpResult>();
            msgbox.Closed += delegate { tcs.TrySetResult(res); };
            if (parent != null)
                msgbox.ShowDialog(parent);
            else msgbox.Show();
            return tcs.Task;
        }

        private static async void ShowError(string message)
        {
            var msgbox = MessageBoxManager.GetMessageBoxStandardWindow(new MessageBoxStandardParams
            {
                ButtonDefinitions = ButtonEnum.Ok,
                ContentTitle = "Error",
                ContentMessage = message,
                Icon = MessageBox.Avalonia.Enums.Icon.Error,
                Style = Style.None,
                ShowInCenter = true
            });
            var result = await msgbox.Show();
        }
        private static async void ShowInfo(string message)
        {
            var msgbox = MessageBoxManager.GetMessageBoxStandardWindow(new MessageBoxStandardParams
            {
                ButtonDefinitions = ButtonEnum.Ok,
                ContentTitle = "Info",
                ContentMessage = message,
                Icon = MessageBox.Avalonia.Enums.Icon.Lock,
                Style = Style.None,
                ShowInCenter = true
            });
            var result = await msgbox.Show();
        }
    }
}