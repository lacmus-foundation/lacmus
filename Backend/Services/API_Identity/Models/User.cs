using API_Identity.Models.Enums;
using Newtonsoft.Json;

namespace API_Identity.Models
{
    [JsonObject]
    public class User : IElement
    {
        [JsonProperty("id")]
        public int Id { get; set; }
        [JsonProperty("firstName")]
        public string FirstName { get; set; }
        [JsonProperty("lastName")]
        public string LastName { get; set; }
        [JsonProperty("Email")]
        public string Email { get; set; }
        [JsonProperty("phoneNumber")]
        public string Phone { get; set; }
        public string PasswordHash { get; set; }
        [JsonProperty("role")]
        public TRole Role { get; set; } = TRole.User;
    }
}