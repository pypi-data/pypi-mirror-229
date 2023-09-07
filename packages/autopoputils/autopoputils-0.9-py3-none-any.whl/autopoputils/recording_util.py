import time
import requests
from selenium import webdriver
from urllib.parse import urljoin

def get_recording_data(url=None, max_attempts=20, sleep_interval=1, scrape=False):

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    # Browse to the target website
    driver.get(url)
    
    # Inject JavaScript to monitor XHR responses
    script = '''
    (function() {
        var open = window.XMLHttpRequest.prototype.open;
        window.responses = [];
        window.XMLHttpRequest.prototype.open = function(method, url) {
            this.addEventListener('load', function() {
                if(this.responseText.startsWith('WEBVTT')) {
                    window.responses.push({content: this.responseText, url: url});
                }
            });
            open.apply(this, arguments);
        };
    })();
    '''
    driver.execute_script(script)
    
    # Poll for captured responses
    attempts = 0
    webvtt_content = None
    webvtt_url = None
    while attempts < max_attempts:
        webvtt_responses = driver.execute_script('return window.responses')
        if webvtt_responses:
            webvtt_content = webvtt_responses[0]['content']
            webvtt_url = webvtt_responses[0]['url']
            break
        time.sleep(sleep_interval)
        attempts += 1
    
    driver.quit()
    
    return webvtt_content if scrape else urljoin(url, webvtt_url)