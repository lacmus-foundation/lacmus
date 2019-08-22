using Microsoft.IdentityModel.Tokens;

namespace API_Identity.Models
{
    public interface IJwtSigningEncodingKey
    {
        string SigningAlgorithm { get; }
 
        SecurityKey GetKey();
    }
}