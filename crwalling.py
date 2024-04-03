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

from flaskAPI import page_init

chrome_options = Options()
chrome_options.add_argument('--headless') # 창 없이 백그라운드로 실행

def crawling(licPrec, searchText):

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:

        # 웹페이지 로드
        driver.get(f'https://law.go.kr/precSc.do?menuId=7&subMenuId=47&tabMenuId=213&query={searchText}')

        # 특정 요소가 로드될 때까지 기다림
        wait = WebDriverWait(driver, 20)
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'tbl_wrap')))

        # 페이지의 HTML 소스를 가져옴
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # # 검색한 판례와 일치하는 텍스트를 가진 요소를 찾음
        # search_result = soup.find_all(string=re.compile(prece))
        # for result in search_result:
        #     parent_a_tag = result.find_parent('a')
        #     if parent_a_tag and 'onclick' in parent_a_tag.attrs:
        #         onclick_attr = parent_a_tag['onclick']
        #         # 'onclick' 속성에서 숫자 추출
        #         numbers = re.findall(r'\d+', onclick_attr)
        #         if numbers:
        #             print("Found number:", numbers[0])
        #             licPrec = numbers[0]
        #             break

        # 검색 결과 중 정확한 판결 번호 결과의 'onclick' 속성을 가진 <a> 태그 클릭
        first_result = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, f"//a[contains(@onclick, \"lsEmpViewWideAll('{licPrec}')\")]"))
        )
        first_result.click()

        # 클릭 후 페이지가 완전히 로드될 때까지 기다림
        time.sleep(5)

        # 새로운 페이지의 HTML 소스를 가져옴
        new_html = driver.page_source
        soup = BeautifulSoup(new_html, 'html.parser')

        data = {
            "title": "",
            "subtitle": "",
            "yo_content": "",
            "texts": []  # 원고, 피고, 원심판결, 주문, 이유에 따른 텍스트를 저장할 리스트
        }

        # input 태그의 id가 precSeq이고 value가 licPrec인 태그 하위의 input 태그의 name이 precNm인 것의 value
        title_input = soup.find('input', {'id': 'precSeq', 'value': f'{licPrec}'})
        if title_input:
            data["title"] = title_input.find_next_sibling('input', {'name': 'precNm'}).get('value', '')

        # div의 class가 subtit1인 것의 문자
        subtitle_div = soup.find('div', {'class': 'subtit1'})
        if subtitle_div:
            data["subtitle"] = subtitle_div.get_text(strip=True)

        # h4의 id가 yo인 것 및 p class="pty4"의 내용
        yo_h4 = soup.find('h4', {'id': 'yo'})
        if yo_h4:
            p_pty4 = yo_h4.find_next('p', {'class': 'pty4'})
            if p_pty4:
                data["yo_content"] = p_pty4.get_text(strip=True)

        # 문서 내의 모든 h5 태그에 대해 순회
        h5s = soup.find_all('h5')
        for h5 in h5s:
            if h5:
                h5_text = h5.text.replace(" ", "")
        
                # "원고" 키워드가 포함된 경우
                if "원고" in h5_text:
                    p = h5.find_next('p', {'class': 'pty4_dep1'})
                    if p:
                        data["texts"].append({"category": "원고", "text": p.text})

                # "피고" 키워드가 포함된 경우
                elif "피고" in h5_text:
                    p = h5.find_next('p', {'class': 'pty4_dep1'})
                    if p:
                        data["texts"].append({"category": "피고", "text": p.text})

                # "주문" 키워드가 포함된 경우
                elif "주문" in h5_text:
                    p = h5.find_next('p', {'class': 'pty4_dep1'})
                    if p:
                        data["texts"].append({"category": "주문", "text": p.text})

                elif "이유" in h5_text:
                    p = h5.find_next('p', {'class': 'pty4_dep1'})
                    if p:
                        
                        summary_content = page_init(p.text)

                        data["texts"].append({"category": "AI요약", "text": summary_content})

                elif "청구취지" in h5_text:
                    p = h5.find_next('p', {'class': 'pty4_dep1'})
                    if p:
                        data["texts"].append({"category": "청구취지", "text": p.text})
                

        return data

    except TimeoutException:
        print("Failed to load the page or find the element within the given time.")

    finally:
        # WebDriver 종료
        driver.quit()



