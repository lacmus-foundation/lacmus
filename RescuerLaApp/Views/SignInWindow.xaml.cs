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
    public class SignInWindow : Window
    {
        [JsonObject]
        public class SignInResult
        {
            [JsonProperty("email")]
            public string Email { get; set; }
            [JsonProperty("passwordHash")]
            public string PasswordHash { get; set; }
            [JsonProperty("id")]
            public int Id { get; set; }
            [JsonProperty("time")]
            public string Time { get; set; }

            public bool IsSignIn { get; set; } = false;
        }

        public SignInWindow() => AvaloniaXamlLoader.Load(this);

        public static Task<SignInResult> Show(Window parent)
        {
            var title = "Sign In";
            var msgbox = new SignInWindow()
            {
                Title = title
            };
            var buttonPanel = msgbox.FindControl<StackPanel>("Buttons");

            SignInResult res = new SignInResult();
            res.IsSignIn = false;

            void AddButton(string caption)
            {
                var btn = new Button {Content = caption};
                btn.Click += (_, __) =>
                {
                    var path = AppDomain.CurrentDomain.BaseDirectory + "user_info";
                    if (File.Exists(path))
                    {
                        res = JsonConvert.DeserializeObject<SignInResult>(File.ReadAllText(path));
                        res.IsSignIn = false;
                    }
                    else
                    {
                        ShowError("There are no account. Please sign up");
                        msgbox.Close();
                        return;
                    }

                    var passwordHash = msgbox.FindControl<TextBox>("tbPassword").Text;
                    var email = msgbox.FindControl<TextBox>("tbEmail").Text;
                    PasswordHasher hasher = new PasswordHasher();
                    if (string.IsNullOrWhiteSpace(passwordHash) || passwordHash.Length < 6)
                    {
                        ShowError("Incorrect Password");
                        msgbox.Close();
                        return;
                    }
                    else if (string.IsNullOrWhiteSpace(passwordHash) || !hasher.VerifyIdentityV3Hash(passwordHash, res.PasswordHash))
                    {
                        ShowError("Incorrect Password");
                        msgbox.Close();
                        return;
                    }
                    else if (string.IsNullOrWhiteSpace(email) || !email.Contains('@') || !email.Contains('.') || email != res.Email)
                    {
                        ShowError("Incorrect Email");
                        msgbox.Close();
                        return;
                    }
                    else if(email == res.Email && hasher.VerifyIdentityV3Hash(passwordHash, res.PasswordHash))
                        res.IsSignIn = true;
                    
                    msgbox.Close();
                };
                buttonPanel.Children.Add(btn);
            }
            
            AddButton("Sign In");
            var tcs = new TaskCompletionSource<SignInResult>();
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
    }
}