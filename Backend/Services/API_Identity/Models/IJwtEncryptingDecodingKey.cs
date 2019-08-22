using Microsoft.IdentityModel.Tokens;

namespace API_Identity.Models
{
    public interface IJwtEncryptingDecodingKey
    {
        SecurityKey GetKey();
    }
}