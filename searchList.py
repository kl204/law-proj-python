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

        result_list = []  # 결과를 저장할 리스트

        container8 = soup.find('div', {'id': 'container8'})

        west = container8.find('div', {'id': 'west'})

        WideListDIV = west.find('div', {'id': 'WideListDIV'})

        cont_wrap = WideListDIV.find('div', {'class': 'cont_wrap'})

        tbl_wrap = cont_wrap.find('div', {'class': 'tbl_wrap'})

        for td in tbl_wrap.find_all('td', class_='s_tit'):
            a_tag = td.find('a')
            if not a_tag:
                continue

            # a 태그의 텍스트와 span 태그를 제외한 순수 텍스트를 가져옴
            a_text = a_tag.text.strip()  # a 태그의 전체 텍스트
            span_text = a_tag.find('span').text if a_tag.find('span') else ''  # span 태그의 텍스트, 없으면 빈 문자열
            a_only_text = a_text.replace(span_text, '').strip()  # a 태그에서 span 텍스트를 제외한 순수 텍스트

            licPrec = None  # 초기값 설정
            if 'onclick' in a_tag.attrs:
                onclick_attr = a_tag['onclick']
                # 'onclick' 속성에서 숫자 추출
                numbers = re.findall(r'\d+', onclick_attr)
                if numbers:
                    licPrec = numbers[0]  # 첫 번째 숫자 추출

            # 추출한 정보를 딕셔너리로 저장하고 리스트에 추가
            result_dict = {
                "a_text": a_only_text,
                "span_text": span_text,
                "licPrec": licPrec
            }
            result_list.append(result_dict)

        return result_list

    except TimeoutException:
        return 'TimeOut Error!!'

    finally:
        # WebDriver 종료
        driver.quit()

