using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using API_Identity.Models;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.HttpsPolicy;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using Microsoft.IdentityModel.Tokens;
using Microsoft.AspNetCore.Authentication.JwtBearer;

namespace API_Identity
{
    public class Startup
    {
        public Startup(IConfiguration configuration)
        {
            Configuration = configuration;
        }

        public IConfiguration Configuration { get; }

        // This method gets called by the runtime. Use this method to add services to the container.
        public void ConfigureServices(IServiceCollection services)
        {
            var signingKey = new SigningSymmetricKey(Configuration["Jwt:SigningKey"]);
            services.AddSingleton<IJwtSigningEncodingKey>(signingKey);
            
            var encryptionEncodingKey = new EncryptingSymmetricKey(Configuration["Jwt:EncodingKey"]);
            services.AddSingleton<IJwtEncryptingEncodingKey>(encryptionEncodingKey);
            
            services.AddTransient<ITokenService, TokenService>();
            services.AddTransient<IPasswordHasher, PasswordHasher>();
            
            services.AddMvc().SetCompatibilityVersion(CompatibilityVersion.Version_2_2);
            
            const string jwtSchemeName = "JwtBearer";
            var signingDecodingKey = (IJwtSigningDecodingKey)signingKey;
            var encryptingDecodingKey = (IJwtEncryptingDecodingKey)encryptionEncodingKey;
            services
                .AddAuthentication(options => {
                    options.DefaultAuthenticateScheme = jwtSchemeName;
                    options.DefaultChallengeScheme = jwtSchemeName;
                })
                .AddJwtBearer(jwtSchemeName, jwtBearerOptions => {
                    jwtBearerOptions.TokenValidationParameters = new TokenValidationParameters {
                        ValidateIssuerSigningKey = true,
                        IssuerSigningKey = signingDecodingKey.GetKey(),
                        TokenDecryptionKey = encryptingDecodingKey.GetKey(),
 
                        ValidateIssuer = true,
                        ValidateAudience = true,
                        ValidateLifetime = true,
                        ValidAudience = Configuration["Jwt:Site"],
                        ValidIssuer = Configuration["Jwt:Site"],
                        ClockSkew = TimeSpan.FromMinutes(Convert.ToInt32(Configuration["Jwt:ExpiryInMinutes"]))
                    };
                });
        }

        // This method gets called by the runtime. Use this method to configure the HTTP request pipeline.
        public void Configure(IApplicationBuilder app, IHostingEnvironment env)
        {
            if (env.IsDevelopment())
            {
                app.UseDeveloperExceptionPage();
            }
            else
            {
                // The default HSTS value is 30 days. You may want to change this for production scenarios, see https://aka.ms/aspnetcore-hsts.
                app.UseHsts();
            }

            app.UseAuthentication();
            app.UseHttpsRedirection();
            app.UseMvc();
            
#if DEBUG
            /* show security key size in exceptions */ 
            Microsoft.IdentityModel.Logging.IdentityModelEventSource.ShowPII = true;
#endif
        }
    }
}