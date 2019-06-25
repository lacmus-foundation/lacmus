using System;
using System.Collections.Generic;

namespace LaddGenerator
{
    public class ArgsParser
    {
        private readonly Dictionary<string, string> _argsKeys;
        
        public ArgsParser(Dictionary<string, string> argsKeys)
        {
            _argsKeys = argsKeys;
        }

        public Dictionary<string, string> Parse(string[] args)
        {
            if (args.Length / 2 != _argsKeys.Count)
            {
                Console.Write("usage\n");
                foreach (var (key, value) in _argsKeys)
                {
                    Console.WriteLine($"\t{key}\t{value}");
                }

                return null;
            }
            
            Dictionary<string, string> result = new Dictionary<string, string>();
            foreach (var (key, value) in _argsKeys)
            {
                for (int i = 0; i < args.Length; i += 2)
                {
                    if(args[i].Contains(key))
                        result.Add(key.Replace("--", ""), args[i+1]);
                }
            }

            return result;
        }
    }
}