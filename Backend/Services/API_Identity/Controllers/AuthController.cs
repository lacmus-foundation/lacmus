using System;
using System.Security.Claims;
using System.Text;
using System.Threading.Tasks;
using System.IdentityModel.Tokens.Jwt;
using API_Identity.Models;
using API_Identity.ViewModels;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Configuration;
using Microsoft.IdentityModel.Tokens;


namespace API_Identity.Controllers
{
    public class AuthController : Controller
    {
        private static UserRepository _repository;
        private readonly IConfiguration _configuration;

        public AuthController(IConfiguration configuration)
        {
            if(_repository == null)
                _repository = new UserRepository();
            _configuration = configuration;
        }

        [Route("register")]
        [AllowAnonymous]
        [HttpPost]
        public ActionResult InsertUser([FromBody] RegisterViewModel model)
        {
            var user = new User()
            {
                Email = model.Email,
                Phone = model.Phone,
                FirstName = model.FirstName,
                LastName = model.LastName,
                PasswordHash = Crypto.GetMd5Hash(model.Password)
            };
            _repository.Add(user);
            return Ok(user);
        }

        [Route("login")]
        [AllowAnonymous]
        [HttpPost]
        public ActionResult Login([FromBody] LoginViewModel model, [FromServices] IJwtSigningEncodingKey signingEncodingKey)
        {
            var user = _repository.GetByEmail(model.Email);
            if (user == null || !Crypto.VerifyMd5Hash(model.Password, user.PasswordHash))
                return Unauthorized();

            var claims = new Claim[]
            {
                new Claim(ClaimTypes.NameIdentifier, user.Email)
            };
            
            var expiryInMinutes = Convert.ToInt32(_configuration["Jwt:ExpiryInMinutes"]);
            
            var token = new JwtSecurityToken(
                issuer: _configuration["Jwt:Site"],
                audience: _configuration["Jwt:Site"],
                claims: claims,
                expires: DateTime.UtcNow.AddMinutes(expiryInMinutes),
                signingCredentials: new SigningCredentials(
                    signingEncodingKey.GetKey(),
                    signingEncodingKey.SigningAlgorithm)
            );

            return Ok(
                new
                {
                    token = new JwtSecurityTokenHandler().WriteToken(token),
                    expiration = token.ValidTo
                });
        }
    }
}