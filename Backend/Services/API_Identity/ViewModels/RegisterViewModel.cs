using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using Newtonsoft.Json;

namespace API_Identity.ViewModels
{
    [JsonObject]
    public class RegisterViewModel
    {
        [Required]
        [EmailAddress]
        [JsonProperty("email")]
        public string Email { get; set; }
        [Required]
        [Phone]
        [JsonProperty("phone")]
        public string Phone { get; set; }
        [Required]
        [JsonProperty("firstName")]
        public string FirstName { get; set; }
        [Required]
        [JsonProperty("lastName")]
        public string LastName { get; set; }
        [Required]
        [JsonProperty("password")]
        public string Password { get; set; }
    }
}