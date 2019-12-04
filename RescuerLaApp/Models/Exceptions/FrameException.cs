using System;

namespace RescuerLaApp.Models.Exceptions
{
    public class FrameException : Exception
    {
        public FrameException(string message) : base($"FrameException: {message}") { }
    }
}