using System.ComponentModel.DataAnnotations;

namespace API_Identity.ViewModels
{
    public class LoginViewModel
    {
        [Required]
        public string Email { get; set; }
        [Required]
        public string Password { get; set; }
    }
}