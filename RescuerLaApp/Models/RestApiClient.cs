using System;
using System.IO;
using System.Net;
using System.Net.NetworkInformation;
using System.Threading.Tasks;

namespace RescuerLaApp.Models
{
    internal class RestApiClient
    {
        private readonly string _baseUrl;

        /// <summary>
        /// Create REST API client with GET, PUT, POST, DELETE methods 
        /// </summary>
        /// <param name="baseUrl">Base end point of host</param>
        public RestApiClient(string baseUrl)
        {
            _baseUrl = baseUrl;
        }
        #region Ping
        /// <summary>
        /// ping host and check if it active
        /// </summary>
        /// <returns>bool</returns>
        public bool IsHostActive()
        {
            using(var p = new Ping())
            {
                var host = _baseUrl;
                try
                {
                    var reply = p.Send(host, 2000);
                    if (reply != null && reply.Status == IPStatus.Success)
                        return true;
                }
                catch
                {
                    // ignored
                }
                return false;
            }
            
        }
        
        /// <summary>
        /// async ping host and check if it active
        /// </summary>
        /// <returns>bool</returns>
        public async Task<bool> IsHostActiveAsync()
        {
            using (var p = new Ping())
            {
                var host = _baseUrl;
                try
                {
                    var reply = await p.SendPingAsync(host, 2000);
                    if (reply != null && reply.Status == IPStatus.Success)
                        return true;
                }
                catch
                {
                    // ignored
                }
                return false;
            }

        }
        #endregion
        
        #region Get
        /// <summary>
        /// GET request
        /// </summary>
        /// <param name="subUrl">sub url. default = ""</param>
        /// <returns>response string</returns>
        public string Get(string subUrl = "")
        {
            var webRequest = WebRequest.Create(_baseUrl + subUrl);
            using (var resp = webRequest.GetResponse())
            using (var stream = resp.GetResponseStream())
            using (var sr = new StreamReader(stream ?? throw new Exception("stream is null")))
            {
                return sr.ReadToEnd();
            }
        }
        
        /// <summary>
        /// async GET request
        /// </summary>
        /// <param name="subUrl">sub url. default = ""</param>
        /// <returns>response string</returns>
        public async Task<string> GetAsync(string subUrl = "")
        {
            try
            {
                var webRequest = WebRequest.Create(_baseUrl + subUrl);

                using (var resp = webRequest.GetResponse())
                using (var stream = resp.GetResponseStream())
                using (var sr = new StreamReader(stream ?? throw new Exception("stream is null")))
                {
                    return await sr.ReadToEndAsync();
                }
            }
            catch
            {
                throw new WebException();
            }
        }
        #endregion
        
        #region Post
        /// <summary>
        /// POST request
        /// </summary>
        /// <param name="jsonString">POST request json body</param>
        /// <param name="subUrl">sub url. default = ""</param>
        /// <returns>response string</returns>
        public string Post(string jsonString, string subUrl = "")
        {
            var webRequest = WebRequest.Create(_baseUrl + subUrl);
            webRequest.ContentType = "application/json; charset=utf-8";
            webRequest.Method = "POST";

            using (var streamWriter = new StreamWriter(webRequest.GetRequestStream()))
            {
                streamWriter.Write(jsonString);
                streamWriter.Flush();
            }
            using (var resp = webRequest.GetResponse())
            using (var sr = new StreamReader(resp.GetResponseStream() ?? throw new Exception("stream is null")))
            {
                return sr.ReadToEnd();
            }
        }

        /// <summary>
        /// async POST request
        /// </summary>
        /// <param name="jsonString">POST request json body</param>
        /// <param name="subUrl">sub url. default = ""</param>
        /// <returns>response string</returns>
        public async Task<string> PostAsync(string jsonString, string subUrl = "")
        {
            var webRequest = WebRequest.Create(_baseUrl + subUrl);
            webRequest.ContentType = "application/json; charset=utf-8";
            webRequest.Method = "POST";

            using (var streamWriter = new StreamWriter(await webRequest.GetRequestStreamAsync()))
            {
                await streamWriter.WriteAsync(jsonString);
                await streamWriter.FlushAsync();
            }
            using (var resp = await webRequest.GetResponseAsync())
            using (var sr = new StreamReader(resp.GetResponseStream() ?? throw new Exception("stream is null")))
            {
                return await sr.ReadToEndAsync();
            }
        }
        #endregion

        #region Put
        /* TODO: create PUT method */
        #endregion
        
        #region Delete
        /* TODO: create DELETE method */
        #endregion
    }
}