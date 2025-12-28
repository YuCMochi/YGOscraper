import requests
import argparse
import os

def get_konami_data(cid):
    """
    Fetches card data from Konami website for a given CID.
    """
    url = f"https://www.db.yugioh-card.com/yugiohdb/card_search.action?ope=2&cid={cid}&request_locale=ja"
    print(f"Fetching URL: {url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'ja'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Konami Card Scraper')
    parser.add_argument('--cid', type=str, default='4007', help='Card ID (CID)')
    args = parser.parse_args()
    
    html_content = get_konami_data(args.cid)
    
    if html_content:
        # Save to a temporary file for inspection or further processing
        output_file = f"konami_{args.cid}.html"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"Successfully fetched data for CID {args.cid}. Content saved to {output_file}")
    else:
        print("Failed to fetch data.")
