from httpcore import TimeoutException
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

chrome_options = Options()
chrome_options.add_argument('--headless')  # 창 없이 백그라운드로 실행
chrome_options.add_argument('--disable-gpu')  # GPU 가속 비활성화
chrome_options.add_argument('--disable-extensions')  # 확장 프로그램 비활성화
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
chrome_options.add_argument('--no-sandbox')  # 샌드박스 모드 비활성화
chrome_options.add_argument('--disable-dev-shm-usage')  # /dev/shm 파티션 사용 안 함

def crawling(licPrec, searchText):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    try:
        driver.get(f'https://law.go.kr/precSc.do?menuId=7&subMenuId=47&tabMenuId=213&query={searchText}')
        wait = WebDriverWait(driver, 10)
        first_result = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f"a[onclick*=\"{licPrec}\"]")))
        first_result.click()

        wait.until(EC.visibility_of_element_located((By.ID, 'yo_content')))  # 'yo_content'가 로드될 때까지 기다림

        new_html = driver.page_source
        soup = BeautifulSoup(new_html, 'html.parser')

        data = {"title": "", "subtitle": "", "yo_content": "", "texts": []}

        title_input = soup.find('input', {'id': 'precSeq', 'value': f'{licPrec}'})
        if title_input:
            data["title"] = title_input.find_next_sibling('input', {'name': 'precNm'}).get('value', '')

        subtitle_div = soup.find('div', {'class': 'subtit1'})
        if subtitle_div:
            data["subtitle"] = subtitle_div.get_text(strip=True)

        yo_content = soup.find('h4', {'id': 'yo'})
        if yo_content:
            data["yo_content"] = yo_content.find_next('p', {'class': 'pty4'}).get_text(strip=True)


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
                        data["texts"].append({"category": "이유", "text": p.text})

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



