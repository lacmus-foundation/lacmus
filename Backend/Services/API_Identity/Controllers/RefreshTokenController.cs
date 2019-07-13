using System;
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using API_Identity.Models;
using API_Identity.ViewModels;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Configuration;
using Microsoft.IdentityModel.Tokens;

namespace API_Identity.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class RefreshTokenController : Controller
    {
        private readonly IConfiguration _configuration;
        private readonly ITokenService _tokenService;
        
        public RefreshTokenController(IConfiguration configuration, ITokenService tokenService)
        {
            _configuration = configuration;
            _tokenService = tokenService;
        }
        
        // GET
        [HttpPost]
        public IActionResult RefreshToken([FromBody] RefreshTokenViewModel model, [FromServices] IJwtSigningEncodingKey signingEncodingKey)
        {
            var principal = _tokenService.GetPrincipalFromExpiredToken(model.Token);
            var username = principal.Identity.Name;

            var newJwtToken = _tokenService.GenerateAccessToken(principal.Claims, signingEncodingKey);
            var newRefreshToken = _tokenService.GenerateRefreshToken();

            return Ok(
                new
                {
                    token = newJwtToken,
                    refreshToken = newRefreshToken
                });
        }
    }
}