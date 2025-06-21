import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import dateparser
import time
import random
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    retry_if_result,
)


def is_rate_limited(response):
    """Check if the response indicates rate limiting (status code 429)"""
    return response.status_code == 429


@retry(
    retry=(retry_if_result(is_rate_limited)),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    stop=stop_after_attempt(5),
)
def make_request(url, headers):
    """Make a request with retry logic for rate limiting"""
    # Random delay before each request to avoid detection
    time.sleep(random.uniform(2, 6))
    response = requests.get(url, headers=headers)
    return response


def getNewsData(query, start_date, end_date):
    """
    Scrape Google News search results for a given query and date range.
    query: str - search query
    start_date: str - start date in the format yyyy-mm-dd or mm/dd/yyyy
    end_date: str - end date in the format yyyy-mm-dd or mm/dd/yyyy
    """

    # Convert date strings for query parameters and create datetime objects for
    # filtering the results. This prevents news from outside the date range from
    # being included (e.g. articles from last year).
    if "-" in start_date:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        start_query = start_dt.strftime("%m/%d/%Y")
    else:
        start_dt = datetime.strptime(start_date, "%m/%d/%Y")
        start_query = start_date
    if "-" in end_date:
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        end_query = end_dt.strftime("%m/%d/%Y")
    else:
        end_dt = datetime.strptime(end_date, "%m/%d/%Y")
        end_query = end_date

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/101.0.4951.54 Safari/537.36"
        )
    }

    news_results = []
    page = 0
    while True:
        offset = page * 10
        url = (
            f"https://www.google.com/search?q={query}"
            f"&tbs=cdr:1,cd_min:{start_query},cd_max:{end_query}"
            f"&tbm=nws&start={offset}"
        )

        try:
            response = make_request(url, headers)
            soup = BeautifulSoup(response.content, "html.parser")
            results_on_page = soup.select("div.SoaBEf")

            if not results_on_page:
                break  # No more results found

            for el in results_on_page:
                try:
                    link = el.find("a")["href"]
                    title = el.select_one("div.MBeuO").get_text()
                    snippet = el.select_one(".GI74Re").get_text()
                    raw_date = el.select_one(".LfVVr").get_text()
                    parsed_date = dateparser.parse(raw_date)
                    # Skip if we can't parse or it's outside the desired range
                    if not parsed_date:
                        continue
                    if not (start_dt.date() <= parsed_date.date() <= end_dt.date()):
                        continue
                    source = el.select_one(".NUnG9d span").get_text()
                    news_results.append(
                        {
                            "link": link,
                            "title": title,
                            "snippet": snippet,
                            "date": parsed_date.strftime("%Y-%m-%d"),
                            "source": source,
                        }
                    )
                except Exception as e:
                    print(f"Error processing result: {e}")
                    # If one of the fields is not found, skip this result
                    continue

            # Update the progress bar with the current count of results scraped

            # Check for the "Next" link (pagination)
            next_link = soup.find("a", id="pnnext")
            if not next_link:
                break

            page += 1

        except Exception as e:
            print(f"Failed after multiple retries: {e}")
            break

    return news_results
