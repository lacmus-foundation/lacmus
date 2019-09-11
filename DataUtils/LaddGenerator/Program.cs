using System;
using System.Collections.Generic;
using System.IO;

namespace LaddGenerator
{
    class Program
    {
        private static readonly Dictionary<string, string> _argsKeys = new Dictionary<string, string>()
        {
            {"--src", "source path"},
            {"--dst", "destination path"},
        };
        
        static void Main(string[] args)
        {
            var parser = new ArgsParser(_argsKeys);
            var parsedArgs = parser.Parse(args);
            if (parsedArgs == null)
            {
                return;
            }

            var imgSrcPatch = parsedArgs["src"] + "JPEGImages/";
            var annSrcPatch = parsedArgs["src"] + "Annotations/";
            var imgDstPatch = parsedArgs["dst"] + "JPEGImages/";
            var annDstPatch = parsedArgs["dst"] + "Annotations/";
            var spltDstPatch = parsedArgs["dst"] + "ImageSets/Main/";
            if (!Directory.Exists(imgSrcPatch))
            {
                Console.Write("unable to open: " + imgSrcPatch);
                return;
            }
            if (!Directory.Exists(annSrcPatch))
            {
                Console.Write("unable to open: " + annSrcPatch);
                return;
            }
            if (!Directory.Exists(imgDstPatch))
            {
                Directory.CreateDirectory(imgDstPatch);
            }
            if (!Directory.Exists(annDstPatch))
            {
                Directory.CreateDirectory(annDstPatch);
            }

            var srcFiles = Directory.GetFiles(annSrcPatch);
            var dstImgFileNames = Directory.GetFiles(imgDstPatch);
            int count = 0; //420;
            if (dstImgFileNames == null || dstImgFileNames.Length == 0)
                count = 0;
            else
            {
                count = dstImgFileNames.Length;
            }
            Console.WriteLine(count);
            Console.ReadLine();
            foreach (var sfile in srcFiles)
            {
                try
                {
                    var srcAnnotation = Annotation.ParseFromXml(sfile);
                    if (!srcAnnotation.Filename.ToLower().EndsWith(".jpg"))
                        srcAnnotation.Filename += ".jpg";

                    var dstAnnotation = new Annotation();
                    dstAnnotation.Folder = "VocGalsTfl";
                    dstAnnotation.Source = new Sourse();
                    dstAnnotation.Filename = $"{count}";
                    dstAnnotation.Objects = srcAnnotation.Objects;
                    dstAnnotation.Size = srcAnnotation.Size;
                    if (dstAnnotation.Objects == null || dstAnnotation.Objects.Count <= 0)
                    {
                        throw new Exception("no objects in the image!");
                    }
                    foreach (var obj in dstAnnotation.Objects)
                    {
                        obj.Box.Normalize();
                    }
                    dstAnnotation.SaveToXml(annDstPatch + $"{count}.xml");
                    File.Copy(imgSrcPatch + srcAnnotation.Filename,
                        imgDstPatch + $"{count}.jpg");
                    Console.WriteLine($"saved for {srcAnnotation.Filename} => {count}.jpg");
                    count++;
                }
                catch (Exception e)
                {
                    Console.WriteLine($"skip {sfile} : {e.Message}");
                }
            }
            
            Console.Write($"Shuffling {count-1} files");
            List<int> files = new List<int>();
            for (int i = 0; i < count; i++)
            {
                files.Add(i);
            }
            Shuffle(files);
            int trainSplit = 0;
            List<string> lines = new List<string>();
            for (int i = 0; i < files.Count-trainSplit; i++)
            {
                lines.Add($"{files[i]}");
            }
            File.WriteAllLines(spltDstPatch+"train.txt", lines);
            File.WriteAllLines(spltDstPatch+"trainval.txt", lines);
            lines = new List<string>();
            for (int i = files.Count-trainSplit; i < files.Count; i++)
            {
                lines.Add($"{files[i]}");
            }
            File.WriteAllLines(spltDstPatch+"test.txt", lines);
            File.WriteAllLines(spltDstPatch+"val.txt", lines);
            Console.WriteLine("Done!");
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