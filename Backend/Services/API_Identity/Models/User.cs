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
        [JsonProperty("phoneNumber")]
        public string PhoneNumber { get; set; }
    }
}