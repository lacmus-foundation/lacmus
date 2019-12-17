using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace LaddValidator
{
    class Program
    {
        private static readonly Dictionary<string, string> _argsKeys = new Dictionary<string, string>()
        {
            {"--src", "source path"},
            {"--val_file", "destination path"},
        };
        
        static void Main(string[] args)
        {
            var parser = new ArgsParser(_argsKeys);
            var parsedArgs = parser.Parse(args);
            if (parsedArgs == null)
            {
                return;
            }
            var splitPatch = parsedArgs["src"] + "ImageSets/Main/";
            var valFilePatch = parsedArgs["val_file"];
            if (!Directory.Exists(splitPatch))
            {
                Console.Write("unable to open: " + splitPatch);
                return;
            }
            if (!File.Exists(valFilePatch))
            {
                Console.Write("unable to open: " + valFilePatch);
                return;
            }

            var valLines = File.ReadLines(valFilePatch).ToList();
            var trainLines = File.ReadLines(splitPatch + "train.txt").ToList();
            var testLines = File.ReadLines(splitPatch + "test.txt").ToList();
            trainLines.AddRange(testLines);
            
            for (int i = 0; i < trainLines.Count; i++)
            {
                for (int j = 0; j < valLines.Count; j++)
                {
                    if (valLines[j] == trainLines[i])
                    {
                        trainLines.RemoveAt(i);
                        Console.WriteLine($"{valLines[j]} moved to val set");
                        if(i>0)
                            i--;
                    }
                }
            }
            Shuffle(valLines);
            File.WriteAllLines(splitPatch+"train.txt", trainLines);
            File.WriteAllLines(splitPatch+"trainval.txt", trainLines);
            File.WriteAllLines(splitPatch+"test.txt", valLines);
            File.WriteAllLines(splitPatch+"val.txt", valLines);
        }
        
        private static void Shuffle<T>(IList<T> list)  
        {  
            Random rng = new Random();  
            int n = list.Count;  
            while (n > 1) {  
                n--;  
                int k = rng.Next(n + 1);  
                T value = list[k];  
                list[k] = list[n];  
                list[n] = value;  
            }  
        }
    }
}