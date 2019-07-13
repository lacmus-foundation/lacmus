using System;
using System.Collections.Generic;
using System.IdentityModel.Tokens.Jwt;
using System.Linq;
using System.Security.Claims;
using System.Security.Cryptography;
using System.Text;
using Microsoft.Extensions.Configuration;
using Microsoft.IdentityModel.Tokens;

namespace API_Identity.Models
{
    public class TokenService : ITokenService
    {
        private readonly IConfiguration _configuration;

        public TokenService(IConfiguration configuration)
        {
            _configuration = configuration;
        }
        public string GenerateAccessToken(IEnumerable<Claim> claims,
            IJwtSigningEncodingKey signingEncodingKey,
            IJwtEncryptingEncodingKey encryptingEncodingKey)
        {
            var tokenHandler = new JwtSecurityTokenHandler();
            var expiryInMinutes = Convert.ToInt32(_configuration["Jwt:ExpiryInMinutes"]);
            var jwtToken = tokenHandler.CreateJwtSecurityToken(
                issuer: _configuration["Jwt:Site"],
                audience: _configuration["Jwt:Site"],
                subject: new ClaimsIdentity(claims),
                notBefore: DateTime.UtcNow,
                expires: DateTime.UtcNow.AddMinutes(expiryInMinutes),
                issuedAt: DateTime.UtcNow,
                signingCredentials: new SigningCredentials(
                    signingEncodingKey.GetKey(),
                    signingEncodingKey.SigningAlgorithm),
                encryptingCredentials: new EncryptingCredentials(
                    encryptingEncodingKey.GetKey(),
                    encryptingEncodingKey.SigningAlgorithm,
                    encryptingEncodingKey.EncryptingAlgorithm));

            return tokenHandler.WriteToken(jwtToken);
        }

        public string GenerateRefreshToken()
        {
            var randomNumber = new byte[32];
            using (var rng = RandomNumberGenerator.Create())
            {
                rng.GetBytes(randomNumber);
                return Convert.ToBase64String(randomNumber);
            }
        }
        
        public ClaimsPrincipal GetPrincipalFromExpiredToken(string token)
        {
            var tokenValidationParameters = new TokenValidationParameters
            {
                ValidateAudience = true, 
                ValidateIssuer = true,
                ValidateIssuerSigningKey = true,
                IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(_configuration["Jwt:SigningKey"])),
                TokenDecryptionKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(_configuration["Jwt:EncodingKey"])),
                ValidAudience = _configuration["Jwt:Site"],
                ValidIssuer = _configuration["Jwt:Site"],
                ValidateLifetime = false
            };

            var tokenHandler = new JwtSecurityTokenHandler();
            SecurityToken securityToken;
            var principal = tokenHandler.ValidateToken(token, tokenValidationParameters, out securityToken);
            
            var jwtSecurityToken = securityToken as JwtSecurityToken;
            if (jwtSecurityToken == null || !jwtSecurityToken.Header.Alg.Equals("dir", StringComparison.InvariantCultureIgnoreCase))
                throw new SecurityTokenException("Invalid token");
            

            return principal;
        }
    }
}