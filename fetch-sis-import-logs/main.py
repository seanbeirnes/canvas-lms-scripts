import sys
import os

import aiohttp
import asyncio

from dotenv import load_dotenv
from typing import Optional

load_dotenv()

BASE_URL: Optional[str] = os.getenv("BASE_URL")
ACCESS_TOKEN: Optional[str] = os.getenv("ACCESS_TOKEN")
MAX_REQUESTS: int = 20

if BASE_URL is None:
    print("[ERROR] Base url not found in .env file")
    sys.exit(1) 
if ACCESS_TOKEN is None:
    print("[ERROR] Access token not found in .env file")
    sys.exit(1) 

async def fetch_logs(client: aiohttp.ClientSession, page: int):
    assert page > 0

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
    params = {
        "per_page": "100",
        "page": page
    }

    url = "/api/v1/accounts/1/sis_imports"
    async with client.get(url, headers=headers, params=params) as resp:
        assert resp.status < 400
        print(f"[INFO] Successfully retrieved '{url}' with {params}")
        return await resp.json()

async def process_batch(client: aiohttp.ClientSession, start_page: int, size: int):
    tasks = [asyncio.create_task(fetch_logs(client, (start_page + index))) for index in range(size)]
    responses = await asyncio.gather(*tasks)

    for sis_logs_page in responses:
        sis_imports = sis_logs_page['sis_imports']
        for sis_import in sis_imports:
            id = sis_import.get('id')
            created_at = sis_import.get('created_at')
            workflow_state = sis_import.get('workflow_state')
            data = sis_import.get('data')

            processing_errors = []
            if 'processing_errors' in sis_import:
                processing_errors = sis_import.get('processing_errors')

            batches = []
            if 'supplied_batches' in data:
                batches = data.get('supplied_batches')

            log_msg = f"[INFO] ID: {id} TIME: {created_at}\tSTATUS: {workflow_state}\tBATCHES: {batches}\tERRORS: {processing_errors}" 
            
            with open("logs.log", "a") as f:
                f.write(f"{log_msg}\n")

async def main():
    pages: int = 20

    if len(sys.argv) == 3 and (sys.argv[1] == "--pages" or sys.argv[1] == "-p"):
        custom_page_count: str = sys.argv[2]
        if custom_page_count.isnumeric():
            pages = int(custom_page_count)
        else:
            print("[ERROR] Non-numeric paramater used for pages\nUsage: --pages 10")
            sys.exit(1)
    elif len(sys.argv) > 1:
        print("[ERROR] Unrecognized argument\nUsage: --pages 10")
        sys.exit(1)

    print(f"[INFO] Extracting {pages} page(s) of SIS import logs via the Canvas REST API...")

    batch_size: int = MAX_REQUESTS
    if pages < batch_size:
        print(f"[INFO] Page count is lower than default batch size of {batch_size}. Updating batch size...")
        batch_size = pages
    
    if pages > 100:
        print(f"[WARN] Page count exceeds 100. This may take a few moments...")

    batches: int = round(pages / batch_size)
    last_batch_size: int = pages % batch_size
    async with aiohttp.ClientSession(BASE_URL) as client:
        for i in range(batches):
            await process_batch(client, (i * batch_size) + 1, batch_size)

        if last_batch_size > 0:
            await process_batch(client, (batches * batch_size) + 1, last_batch_size)

if __name__ == "__main__":
    asyncio.run(main())
