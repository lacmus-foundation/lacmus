using Microsoft.IdentityModel.Tokens;

namespace API_Identity.Models
{
    public interface IJwtEncryptingEncodingKey
    {
        string SigningAlgorithm { get; }
 
        string EncryptingAlgorithm { get; }
 
        SecurityKey GetKey();
    }
}