# Treehouse Downloader

* Download [**Treehouse**](https://teamtreehouse.com/) Tracks, Courses and Workshops for offline use.
* You need an active account at teamtreehouse.com to download the courses.

* **NOTE** Your library might have partnered with teamtreehouse.com to offer you free teamtreehouse.com account.

## Features
* Download
    - Courses
    - Tracks
    - Workshops
    - Practice Sessions
    - Instructions
    - Project Files
* Auto recognize download type
* Adapt folder structure accordingly

## Requirements

* Python3
* ChromeWeb Driver (In your PATH)
* BeautifulSoup
* selenium
* [aria2](https://github.com/aria2/aria2/releases)

## Installation
* Install Python 3
* Install [ChromeWeb Driver](https://chromedriver.chromium.org/downloads) and add it to your PATH (Version has to match your installed chrome browser version)
* Install aria2

```bash
# open terminal or commandline
$ pip install -r requirements.txt
```

## Configuration

* Add your email, password and download path to the settings file `data/settings.json`

```javascript
{
  "email": "treehouse-login",
  "password": "treehouse-password",
  "webdriver": "chromedriver",
  "download_folder": "PATH/TO/YOUR/DOWNLOAD/FOLDER/",
  "EXTERNAL_DL": "  --external-downloader aria2c --external-downloader-args '-j1 -x16 -s16 -k1M' "
}
```

# Links to Download

* Add the download links to Tracks, Courses, Workshops, etc. seperated by line to `data/links.txt`
* Comments with "#" are possible

## Usage

```bash
# open terminal or commandline
$ python treehouse.py
```

## Acknowledgement

* Thanks to [**muse-sisay**](https://github.com/muse-sisay/treehouseDownloader), for inspiration.
