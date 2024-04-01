from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import re
import time

options = webdriver.ChromeOptions()
options.binary_location = '/usr/local/bin/chrome-linux'

service = webdriver.ChromeService(executable_path='/usr/local/bin/chromedriver')

driver = webdriver.Chrome(service=service, options=options)

def crawling(prece):
    try:

        # 검색할 판례 번호
        prece = prece

        # 웹페이지 로드
        driver.get(f'https://law.go.kr/precSc.do?menuId=7&subMenuId=47&tabMenuId=213&query={prece}')

        # 특정 요소가 로드될 때까지 기다림
        wait = WebDriverWait(driver, 20)
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'tbl_wrap')))

        # 페이지의 HTML 소스를 가져옴
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # 검색한 판례와 일치하는 텍스트를 가진 요소를 찾음
        search_result = soup.find_all(string=re.compile(prece))
        for result in search_result:
            parent_a_tag = result.find_parent('a')
            if parent_a_tag and 'onclick' in parent_a_tag.attrs:
                onclick_attr = parent_a_tag['onclick']
                # 'onclick' 속성에서 숫자 추출
                numbers = re.findall(r'\d+', onclick_attr)
                if numbers:
                    print("Found number:", numbers[0])
                    licPrec = numbers[0]
                    break

        print("prec check : " + licPrec)

        # 검색 결과 중 첫 번째 결과의 'onclick' 속성을 가진 <a> 태그 클릭
        first_result = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, f"//a[contains(@onclick, \"lsEmpViewWideAll('{licPrec}')\")]"))
        )
        first_result.click()

        # 클릭 후 페이지가 완전히 로드될 때까지 기다림
        time.sleep(5)

        # 새로운 페이지의 HTML 소스를 가져옴
        new_html = driver.page_source
        soup = BeautifulSoup(new_html, 'html.parser')

        # 데이터 추출
        title = ""
        subtitle = ""
        yo_content = ""

        # input 태그의 id가 precSeq이고 value가 prece인 태그 하위의 input 태그의 name이 precNm인 것의 value
        title_input = soup.find('input', {'id': 'precSeq', 'value': f'{licPrec}'})
        if title_input:
            title = title_input.find_next_sibling('input', {'name': 'precNm'})['value']

        # div의 class가 subtit1인 것의 문자
        subtitle_div = soup.find('div', {'class': 'subtit1'})
        if subtitle_div:
            subtitle = subtitle_div.get_text(strip=True)

        # h4의 id가 yo인 것 및 p class="pty4"의 내용
        yo_h4 = soup.find('h4', {'id': 'yo'})
        if yo_h4:
            p_pty4 = yo_h4.find_next('p', {'class': 'pty4'})
            if p_pty4:
                yo_content = p_pty4.get_text(strip=True)

        # JSON으로 묶어서 출력
        data_json = {
            'title': title,
            'subtitle': subtitle,
            'contents': {
                'yo': yo_content
            }
        }

        return data_json

    except TimeoutException:
        print("Failed to load the page or find the element within the given time.")

    finally:
        # WebDriver 종료
        driver.quit()

# # 함수 호출
# prece = "99다63183"
# result_data = scrape_korean_legal_info(prece)
# print(json.dumps(result_data, ensure_ascii=False, indent=2))

