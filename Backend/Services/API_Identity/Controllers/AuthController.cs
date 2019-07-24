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
        private readonly IPasswordHasher _passwordHasher;
        private readonly ITokenService _tokenService;

        public AuthController(IConfiguration configuration, IPasswordHasher passwordHasher, ITokenService tokenService)
        {
            if(_repository == null)
                _repository = new UserRepository();
            _configuration = configuration;
            _passwordHasher = passwordHasher;
            _tokenService = tokenService;
        }

        [Route("register")]
        [AllowAnonymous]
        [HttpPost]
        public ActionResult InsertUser([FromBody] RegisterViewModel model)
        {
            if (_repository.GetByEmail(model.Email) != null)
                return BadRequest();
            
            var user = new User()
            {
                Email = model.Email,
                Phone = model.Phone,
                FirstName = model.FirstName,
                LastName = model.LastName,
                PasswordHash = _passwordHasher.GenerateIdentityV3Hash(model.Password)
            };
            _repository.Add(user);
            return Ok(user);
        }

        [Route("login")]
        [AllowAnonymous]
        [HttpPost]
        public ActionResult Login([FromBody] LoginViewModel model, 
            [FromServices] IJwtSigningEncodingKey signingEncodingKey,
            [FromServices] IJwtEncryptingEncodingKey encryptingEncodingKey)
        {
            var user = _repository.GetByEmail(model.Email);
            if (user == null || !_passwordHasher.VerifyIdentityV3Hash(model.Password, user.PasswordHash))
                return Unauthorized();

            var usersClaims = new [] 
            {
                new Claim(ClaimTypes.Name, user.Email),                
                new Claim(ClaimTypes.NameIdentifier, user.Id.ToString())
            };
            
            var jwtToken = _tokenService.GenerateAccessToken(usersClaims, signingEncodingKey, encryptingEncodingKey);
            var refreshToken = _tokenService.GenerateRefreshToken();

            return Ok(
                new
                {
                    token = jwtToken,
                    refreshToken = refreshToken
                });
        }
    }
}