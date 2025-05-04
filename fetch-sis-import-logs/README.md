# Fetch Canvas SIS Import Logs
Use this Python script to fetch Canvas SIS import logs in large batches. It will let you capture all the logs from the past
several weeks or even months in a single file so it is easier to identify patterns in the error messages.

## Setup
1. Initialize virtual environment
```bash
python -m venv .venv
```
2. Activate virtual environment
```bash
source .venv/bin/activate
```
3. Install dependencies
```bash
pip install -r requirements.txt
```
4. Create a .env file with the following:
    - BASE_URL=[add Canvas base URL here, i.e. https://myschool.instructure.com]
    - ACCESS_TOKEN=[add access token here]

## Usage
Run the script with:
```bash
python main.py
```
An optional `-p` or `--pages` argument may be passed to customize the number of SIS Import Log pages to retrieve from
the Canvas API. The default is `20` when the argument is not used. 

Example:
```bash
python main.py --pages 100
```
Keep in mind that each page of the API will have 100 logs. Therefore, 100 pages of logs is 10,000 logs.

The logs will be saved to `logs.log`
