from selenium import webdriver

from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import re
import time

chrome_options = Options()
chrome_options.add_argument('--headless') # 창 없이 백그라운드로 실행

def searchList(prece):

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:

        # 웹페이지 로드
        driver.get(f'https://law.go.kr/precSc.do?menuId=7&subMenuId=47&tabMenuId=213&query={prece}')

        # 특정 요소가 로드될 때까지 기다림
        wait = WebDriverWait(driver, 20)
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'tbl_wrap')))

        # 페이지의 HTML 소스를 가져옴
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # 결과를 저장할 JSON 배열
        results = []

        # 'a' 태그를 순회하며 정보 추출
        for a_tag in soup.find_all('a'):
            a_text = a_tag.text  # a 태그의 전체 텍스트 (span 포함)
            span_text = a_tag.find('span').text if a_tag.find('span') else ''  # span 태그의 텍스트
            a_only_text = a_text.replace(span_text, '').strip()  # a 태그에서 span 텍스트를 제외한 순수 텍스트

            # 추출한 정보를 딕셔너리로 저장
            result_dict = {
                "a_text": a_only_text,
                "span_text": span_text
            }

            # 결과 JSON 배열에 딕셔너리 추가
            results.append(result_dict)

        return results

    except TimeoutException:
        print("Failed to load the page or find the element within the given time.")

    finally:
        # WebDriver 종료
        driver.quit()

