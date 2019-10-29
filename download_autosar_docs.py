import requests
import lxml.html
import sys
import os
import asyncio
import aiofiles
import aiohttp
from aiohttp import ClientSession
import zipfile
import glob

BASE_URL = "http://www.autosar.org/"

def create_dir(url: str) -> None:
    directory = os.path.basename(url)
    os.mkdir(directory)
    os.chdir(directory)
    

async def fetch_zip(url: str) -> None:
    print(f"fetching {url}")
    filename = os.path.basename(url)
    async with aiohttp.ClientSession() as session: 
        async with session.get(url) as r:
            data = await r.read()
    async with aiofiles.open(filename, 'wb') as outfile:
        await outfile.write(data)

def fetch_data(url: str) -> None:
    r = requests.get(url)
    html = lxml.html.fromstring(r.content)
    tasks = []
    loop = asyncio.get_event_loop()
    for *_, url, _ in html.iterlinks():
        if url.startswith("fileadmin"):
            tasks.append(loop.create_task(fetch_zip(os.path.join(BASE_URL, url))))
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()

def unzip_files() -> None:
    for z in glob.glob("*.zip"):
        print(f"extracting {z}")
        with zipfile.ZipFile(z) as zf:
            zf.extractall(".")
        os.unlink(z)
    
    
def main() -> None:
    url = sys.argv[1]
    create_dir(url)
    fetch_data(url)
    unzip_files()
    

    

if __name__ == '__main__':
    main()


