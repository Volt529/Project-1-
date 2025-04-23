import requests
from bs4 import BeautifulSoup
import csv
import os



url = "https://books.toscrape.com"  


response = requests.get('https://books.toscrape.com')
response.raise_for_status()

soup = BeautifulSoup(response.text, 'html.parser')

categories_data = []

for link in soup.find_all('a', href=True):
    if 'catalogue/category/books' in link['href']:
        category_name = link.get_text(strip=True).strip('"').strip()
        if category_name:

            category_url = link['href']
            if not category_url.startswith('http'):
                category_url = url + '/' + category_url.lstrip('/')
            
            categories_data.append({
                'name': category_name,
                'url': category_url
            })

output_dir = 'liens'
os.makedirs(output_dir, exist_ok=True)

filename = os.path.join(output_dir, 'liens.csv')

with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['name', 'url']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for category in categories_data:
        writer.writerow(category)

print(f"Les données ont été sauvegardées dans {filename}")
    
print("Catégories")
for i, category in enumerate(categories_data, 1):
    print(f"{i}. {category['name']}")
    if category['url']:
        print(f"   Lien: {category['url']}")
    else:
        print("   Lien: non disponible")
        
