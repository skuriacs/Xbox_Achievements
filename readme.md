# Xbox Achievement Scraper
This application will scrape the Xbox achievements website and gathers information on the recently played tab and dumps the information into a csv file.

There are two ways to use this script, by either downloading the release exe or by running the Python script

In either way, you're going to need to download the appropriate web driver for your browser. Download the exe and extract it the directory of either the executable/script.

### Webdrivers
Chrome: https://chromedriver.chromium.org/downloads

Firefox: https://github.com/mozilla/geckodriver/releases/
# Instructions

## Executable (A bit slower, bulkier than just the script, easier to set up)
<ol>
<li> Download the release zip from the releases tab, and store it somewhere on your computer.
<li> Place the web driver into the same folder as the executable (Xbox.exe)
<li> Run the exe and choose the appropriate web browser on the console that comes up. Your browser should open up and you should be able to login to your microsoft account.
<li> After logging in, you should see the web page start changing to different links. Wait for the browser to close, that marks the end of the scraping of data.
<li> After the browser closes, check back to the console, and decide whether or not you want to remove data about games with 0 minutes played.
<li> After deciding, you should have a XboxStats.csv show up in the folder! 
</ol>

## Script
<ol>
<li> Clone the repo, and make sure the webdriver exe is in the same directory as the script. Make sure you have the same Python modules installed. If not, use PIP to install them.
<li> Follow steps 3-6 from the Executable section.