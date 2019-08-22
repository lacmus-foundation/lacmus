using Microsoft.IdentityModel.Tokens;

namespace API_Identity.Models
{
    public interface IJwtSigningDecodingKey
    {
        SecurityKey GetKey();
    }
}