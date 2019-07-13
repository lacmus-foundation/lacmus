using Newtonsoft.Json;

namespace API_Identity.ViewModels
{
    [JsonObject]
    public class RefreshTokenViewModel
    {
        [JsonProperty("token")]
        public string Token { get; set; }
        [JsonProperty("refreshToken")]
        public string RefreshToken { get; set; }
    }
}