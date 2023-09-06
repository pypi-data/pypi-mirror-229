import time,json
from gorillacareer.constants import LINKEDIN_JOB_LEVEL_MAP, INDEED_JOB_LEVEL_MAP
from typing import Dict
from selenium.webdriver.chrome.webdriver import WebDriver;
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup


LINKEDIN_LOGIN_PAGE = "https://www.linkedin.com/login?trk=guest_homepage-basic_nav-header-signin"
LINKEDIN_SEARCH_BY_KEYWORD = "https://www.linkedin.com/jobs/search/?&f_E=%s&keywords=%s&location=%s"
LINKEDIN_DETAIL_PAGE = "https://www.linkedin.com/jobs/view/"
INDEED_QUERY_PAGE = "https://www.indeed.com/jobs?q=%s&l=%s&sc=0kf:explvl(%s);"
INDEED_PREFIX_DETAIL_PAGE = 'https://www.indeed.com/viewjob?jk=%s'

def login_linkedin(browser : WebDriver, username : str, password : str) -> None:
    """
    Log in to Linkedin on the browser given username and password.
    """
    browser.get(LINKEDIN_LOGIN_PAGE)
    try:
        user_field = browser.find_element("id","username")
        pw_field = browser.find_element("id","password")
        login_button = browser.find_element("xpath",
                    '//*[@id="organic-div"]/form/div[3]/button')
        user_field.send_keys(username)
        user_field.send_keys(Keys.TAB)
        time.sleep(2)
        pw_field.send_keys(password)
        time.sleep(2)
        login_button.click()
        time.sleep(3)
    except TimeoutException:
        print("Unable to locate username or password field.")
    print("login succesfully.")

def get_job_info_from_browser(browser: WebDriver, keyword : str, location : str, experience : str) -> Dict[str, str]:
    """
    Obtain a list of job information by querying Linkedin with keyword and geographic location
    """
    browser.set_window_position(1, 1)
    browser.maximize_window()
    browser.get(LINKEDIN_SEARCH_BY_KEYWORD % (LINKEDIN_JOB_LEVEL_MAP.get(experience.lower()),keyword,location))
    load_page(browser)

    # Obtain the job id from current page.
    links = browser.find_elements("xpath",'//div[@data-job-id]')
    if len(links) <= 0:
        print("Unable to locate Job Posts.")
        return None 
    
    jobIDs: list = []
    
    # Iterate through all job posting, extract job IDs, and store them into a list.
    for link in links:
        children = link.find_elements("xpath",'//ul[@class="scaffold-layout__list-container"]')
        for child in children:
            temp = link.get_attribute("data-job-id")
            jobID = temp.split(":")[-1]
            jobIDs.append(int(jobID))

    # Use the jobID to access job posting detail page.
    detailinfoMap = {}
    for jobID in jobIDs: 
        browser.get(LINKEDIN_DETAIL_PAGE + str(jobID))
        currentPage = load_page(browser)

        serialized_job_detail = parse_job_details_from_current_page(currentPage)

        detailinfoMap[jobID] = serialized_job_detail
        time.sleep(2)

    return detailinfoMap

def load_page(browser: WebDriver) -> BeautifulSoup:
    """
    Load the page where we need to scroll down to see all the content.
    """
    scrollPage = 0
    while scrollPage < 4000:
        browser.execute_script("window.scrollTo(0," + str(scrollPage) + " );")
        scrollPage += 200
        time.sleep(1)

    browser.execute_script("window.scrollTo(0,0);")
    time.sleep(3)

    page = BeautifulSoup(browser.page_source, "lxml")
    return page

def parse_job_details_from_current_page(page : BeautifulSoup) -> str:
    """
    Parse the html element that contains company and job.
    """
    jobDetailDict = {}
    jobDetailDict["job title"] = page.select(".jobs-unified-top-card__job-title")[0].getText().strip("\n")
    jobDetailDict["salary"] = page.select(".jobs-unified-top-card__job-insight")[0].getText().strip("\n")
    jobDetailDict["company size"] = page.select(".jobs-unified-top-card__job-insight")[1].getText().strip("\n")
    jobDetailDict["job description"]  = page.select(".jobs-description-content__text")[0].getText().strip("\n")

    return json.dumps(jobDetailDict)

def request_to_indeed(browser: WebDriver,
                        keyword : str,
                        location : str,
                        salary : str,
                        experience : str
                        ) -> str:
    query = INDEED_QUERY_PAGE % (keyword + "+$" + salary, location, INDEED_JOB_LEVEL_MAP.get(experience.lower()))
    browser.get(query)
    
    soup = BeautifulSoup(browser.page_source, 'lxml')
    jobs = soup.find_all('div', class_='tapItem')
    detailinfoMap = {}
    for job in jobs:
        detailInfo = {}
        job_id = job.find('a')["id"].split('_')[-1]
        job_title = job.find('span', title=True).text.strip()
        company = job.find('span', class_='companyName').text.strip()
        loc = job.find('div', class_='companyLocation').text.strip()
        posted = job.find('span', class_='date').text.strip()
        job_link = INDEED_PREFIX_DETAIL_PAGE % job_id
        detailInfo["job title"] = job_title
        detailInfo["company"] = company
        detailInfo["location"] = loc
        detailInfo["posting info"] = posted
        detailInfo["job link"] = job_link
        detailinfoMap[job_id] = detailInfo
    return json.dumps(detailinfoMap)
