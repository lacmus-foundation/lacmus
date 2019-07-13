using Microsoft.AspNetCore.Cryptography.KeyDerivation;

namespace API_Identity.Models
{
    public interface IPasswordHasher
    {
        string GenerateIdentityV3Hash(string password, KeyDerivationPrf prf = KeyDerivationPrf.HMACSHA256, int iterationCount = 10000, int saltSize = 16);
        bool VerifyIdentityV3Hash(string password, string passwordHash);
    }
}