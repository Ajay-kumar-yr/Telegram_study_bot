from bs4 import BeautifulSoup
import requests
import os
from urllib.parse import urljoin
import json

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}


def download_file(url, filename, download_path='downloaded_notes'):

    # Create the download directory if it doesn't exist
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    file_path = os.path.join(download_path, filename)
    try:
        file_id=url.split('/')[-2]
    except IndexError:
        return None
    direct_download_link= f"https://drive.google.com/uc?export=download&id={file_id}"

    try:
        # Use stream=True to handle large files efficiently
        with requests.get(direct_download_link, stream=True) as response:
            response.raise_for_status() # Check for HTTP errors

            # Write the content to a file in binary mode
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        return file_path
            
    except requests.exceptions.RequestException as e:
        return None

def get_source(branch,sem):
    sources=[]
    merged_list=[]
    try: 
        link = f"https://saividya.ac.in/study-blogs"

        web_page = requests.get(link, headers=header).text
        scrape = BeautifulSoup(web_page, "lxml")
        tables = scrape.find_all("table")

        try:
            for table in tables:
                rows = table.find_all("tr")
                current_sem=None

            
                for row in rows:
                    th = row.find("th")  
                    if th and 'SEMESTER' in th.get_text():
                        current_sem = th.get_text(strip=True)


                    tds = row.find_all("td")
                
                    if (sem==current_sem and len(tds) > 1) or  ((branch=="physics-cycle" or branch=="chemistry-cycle") and len(tds)>1):
                        full_subject=[]
                        blog_link = tds[1].u.a["href"]
                        sub_code=tds[0].text.strip()
                        sub_name = tds[1].u.a.text.strip()

                        sources.append(blog_link)
                        full_subject.append(sub_code)
                        full_subject.append(sub_name)

                        merging=full_subject[0] + "-" + full_subject[1]
                        merged_list.append(merging)

            return merged_list,sources
        except Exception as e:
            return [],[]
    except requests.exceptions.RequestException as e:
       r="couldn't able to fetch"
       return r


def fetch_links_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status() # Raises an exception for bad status codes

        soup = BeautifulSoup(response.text, 'html.parser')

        all_links = []

        # Find all <iframe> tags that have a 'src' attribute
        for iframe in soup.find_all('iframe', src=True):
            src = iframe.get('src')
            all_links.append(urljoin(url, src))
        
        if all_links:
            all_links.pop()

        return all_links
    except requests.exceptions.RequestException as e:
        print(f"Error scraping the page: {e}")
        return []
