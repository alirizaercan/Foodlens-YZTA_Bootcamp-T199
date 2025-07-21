using System;
using System.IO;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;

public class Product
{
    public string name { get; set; }
    public string brand { get; set; }
    public string category { get; set; }
    public string barcode { get; set; }
    public string volume { get; set; }
    public string unit { get; set; }
    public string image { get; set; }
    public string price { get; set; }
}

class Program
{
    static void Main()
    {
        try
        {
            string jsonPath = "turkey_products.json";
            string json = File.ReadAllText(jsonPath);
            List<Product> urunler = JsonSerializer.Deserialize<List<Product>>(json);

            string ocrText = "Lipton Ice Tea Şeftali 330 ml";
            Product enYakin = urunler
                .OrderBy(u => Levenshtein(u.name.ToLower(), ocrText.ToLower()))
                .First();

            Console.WriteLine("OCR çıktısı: " + ocrText);
            Console.WriteLine("Eşleşen Ürün: " + enYakin.name);
            Console.WriteLine("Marka: " + enYakin.brand);
            Console.WriteLine("Fiyat: " + enYakin.price);
        }
        catch (Exception ex)
        {
            Console.WriteLine("Hata oluştu: " + ex.Message);
        }
    }

    public static int Levenshtein(string s, string t)
    {
        int n = s.Length, m = t.Length;
        var d = new int[n + 1, m + 1];

        if (n == 0) return m;
        if (m == 0) return n;

        for (int i = 0; i <= n; i++) d[i, 0] = i;
        for (int j = 0; j <= m; j++) d[0, j] = j;

        for (int i = 1; i <= n; i++)
            for (int j = 1; j <= m; j++)
            {
                int cost = (t[j - 1] == s[i - 1]) ? 0 : 1;
                d[i, j] = Math.Min(Math.Min(
                    d[i - 1, j] + 1,
                    d[i, j - 1] + 1),
                    d[i - 1, j - 1] + cost);
            }

        return d[n, m];
    }
}