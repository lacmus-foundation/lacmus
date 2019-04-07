using System;

namespace RescuerLaApp.Models.Exceptions
{
    public class FrameException : Exception
    {
        public FrameException() : base ()
            { }
        public FrameException(string message) : base($"FrameException: {message}")
            { }
    }
}