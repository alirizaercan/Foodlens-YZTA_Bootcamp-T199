import requests
import json
import time
import os
import csv

def test_api_endpoint():
    """
    API endpoint'ini test et
    """
    test_urls = [
        "https://world.openfoodfacts.org/country/turkey/1.json",
        "https://world.openfoodfacts.org/api/v0/product/country/turkey.json",
        "https://world.openfoodfacts.org/cgi/search.pl?search_terms=&search_simple=1&action=process&sort_by=unique_scans_n&page_size=50&page=1&axis_x=energy&axis_y=products_n&graph_title=Products&flavors_en=&countries_tags_en=turkey&json=1"
    ]
    
    for url in test_urls:
        try:
            print(f"Testing URL: {url}")
            response = requests.get(url, timeout=10)
            print(f"Status Code: {response.status_code}")
            print(f"Content Type: {response.headers.get('content-type', 'Not specified')}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"JSON Response Keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                    if isinstance(data, dict) and 'products' in data:
                        print(f"Number of products: {len(data['products'])}")
                        return url, data
                except json.JSONDecodeError:
                    print("Invalid JSON response")
            print("---")
        except Exception as e:
            print(f"Error: {e}")
            print("---")
    
    return None, None

def fetch_turkey_products():
    """
    Open Food Facts API'sinden Türkiye ürünlerinin TÜM sayfalarını çeker
    """
    products = []
    page = 1
    max_pages = 200  # Güvenlik için maksimum sayfa sayısı
    
    print("Türkiye ürünleri çekiliyor... (Tüm sayfalar)")
    
    # API endpoint'ini test et
    working_url, test_data = test_api_endpoint()
    
    if not working_url:
        print("Geçerli API endpoint bulunamadı!")
        return []
    
    print(f"Kullanılacak API endpoint: {working_url}")
    
    # Eğer test URL'i sayfa numarası içeriyorsa, onu temel alarak diğer sayfaları çek
    if "page=1" in working_url:
        base_url = working_url.replace("page=1", "page={}")
        
        while page <= max_pages:
            url = base_url.format(page)
            
            try:
                print(f"Sayfa {page} çekiliyor...")
                response = requests.get(url, timeout=15)
                response.raise_for_status()
                
                data = response.json()
                page_products = data.get("products", [])
                
                if not page_products:
                    print(f"Sayfa {page}'de ürün bulunamadı, çekme işlemi tamamlandı.")
                    break
                    
                products.extend(page_products)
                print(f"Sayfa {page} tamamlandı, bu sayfada {len(page_products)} ürün, toplam: {len(products)}")
                
                # Her 10 sayfada bir verileri kaydet (güvenlik için)
                if page % 10 == 0:
                    temp_filename = f"turkey_products_temp_{page}.json"
                    save_products_to_json(products, temp_filename)
                    print(f"Geçici kayıt yapıldı: {temp_filename}")
                
                # API'ye çok hızlı istek göndermemek için kısa bekleme
                time.sleep(1)
                
                page += 1
                
            except requests.exceptions.RequestException as e:
                print(f"Sayfa {page} çekilirken hata: {e}")
                print("5 saniye bekleyip tekrar deneniyor...")
                time.sleep(5)
                continue
                
            except Exception as e:
                print(f"Beklenmeyen hata: {e}")
                break
                
    else:
        # Eğer tek sayfa ise, sadece o sayfadaki ürünleri al
        if test_data and 'products' in test_data:
            products = test_data['products']
            print(f"Tek sayfadan {len(products)} ürün çekildi")
    
    return products

def save_products_to_json(products, filename="turkey_products.json"):
    """
    Ürünleri JSON formatında kaydet
    """
    # raw_data dizininin mutlak yolunu oluştur
    current_dir = os.path.dirname(os.path.abspath(__file__))
    raw_data_dir = os.path.join(current_dir, "..", "raw_data")
    
    # Dizin yoksa oluştur
    os.makedirs(raw_data_dir, exist_ok=True)
    
    filepath = os.path.join(raw_data_dir, filename)
    
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        print(f"Veriler başarıyla kaydedildi: {filepath}")
        return True
    except Exception as e:
        print(f"Dosya kaydedilirken hata: {e}")
        return False

def save_products_to_csv(products, filename="turkey_products.csv"):
    """
    Ürünleri CSV formatında kaydet
    """
    if not products:
        print("Kaydedilecek ürün bulunamadı.")
        return False
    
    # raw_data dizininin mutlak yolunu oluştur
    current_dir = os.path.dirname(os.path.abspath(__file__))
    raw_data_dir = os.path.join(current_dir, "..", "raw_data")
    
    # Dizin yoksa oluştur
    os.makedirs(raw_data_dir, exist_ok=True)
    
    filepath = os.path.join(raw_data_dir, filename)
    
    try:
        # CSV başlıkları - en yaygın alanlar
        fieldnames = [
            'id', 'product_name', 'brands', 'categories', 'countries',
            'energy_100g', 'fat_100g', 'saturated_fat_100g', 'carbohydrates_100g',
            'sugars_100g', 'proteins_100g', 'salt_100g', 'fiber_100g',
            'allergens', 'ingredients_text', 'nova_group', 'nutriscore_grade',
            'ecoscore_grade', 'packaging', 'labels', 'image_url'
        ]
        
        with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for product in products:
                # Ürün bilgilerini düzenle
                row = {}
                
                # Temel bilgiler
                row['id'] = product.get('_id', '')
                row['product_name'] = product.get('product_name', '')
                row['brands'] = product.get('brands', '')
                row['categories'] = product.get('categories', '')
                row['countries'] = product.get('countries', '')
                
                # Besin değerleri (100g başına)
                nutriments = product.get('nutriments', {})
                row['energy_100g'] = nutriments.get('energy_100g', '')
                row['fat_100g'] = nutriments.get('fat_100g', '')
                row['saturated_fat_100g'] = nutriments.get('saturated-fat_100g', '')
                row['carbohydrates_100g'] = nutriments.get('carbohydrates_100g', '')
                row['sugars_100g'] = nutriments.get('sugars_100g', '')
                row['proteins_100g'] = nutriments.get('proteins_100g', '')
                row['salt_100g'] = nutriments.get('salt_100g', '')
                row['fiber_100g'] = nutriments.get('fiber_100g', '')
                
                # Diğer önemli bilgiler
                row['allergens'] = product.get('allergens', '')
                row['ingredients_text'] = product.get('ingredients_text', '')
                row['nova_group'] = product.get('nova_group', '')
                row['nutriscore_grade'] = product.get('nutriscore_grade', '')
                row['ecoscore_grade'] = product.get('ecoscore_grade', '')
                row['packaging'] = product.get('packaging', '')
                row['labels'] = product.get('labels', '')
                row['image_url'] = product.get('image_url', '')
                
                writer.writerow(row)
        
        print(f"CSV veriler başarıyla kaydedildi: {filepath}")
        return True
        
    except Exception as e:
        print(f"CSV dosyası kaydedilirken hata: {e}")
        return False

if __name__ == "__main__":
    # Ürünleri çek
    products = fetch_turkey_products()
    
    if products:
        print(f"\nToplam çekilen ürün sayısı: {len(products)}")
        
        # İlk birkaç ürünün örnek bilgilerini göster
        if len(products) > 0:
            print("\nÖrnek ürün bilgisi:")
            sample_product = products[0]
            print(f"Ürün adı: {sample_product.get('product_name', 'N/A')}")
            print(f"Marka: {sample_product.get('brands', 'N/A')}")
            print(f"Kategori: {sample_product.get('categories', 'N/A')}")
        
        # JSON olarak kaydet
        json_success = save_products_to_json(products)
        
        if json_success:
            print("Veri çekme ve kaydetme işlemi başarıyla tamamlandı!")
        else:
            print("Veri kaydedilirken hata oluştu.")
    else:
        print("Hiç ürün çekilemedi.")
