using System.Collections.Generic;
using System.Security.Claims;

namespace API_Identity.Models
{
    public interface ITokenService
    {
        string GenerateAccessToken(IEnumerable<Claim> claims, IJwtSigningEncodingKey signingEncodingKey, IJwtEncryptingEncodingKey encryptingEncodingKey);         
        string GenerateRefreshToken();    
        ClaimsPrincipal GetPrincipalFromExpiredToken(string token);            
    }
}