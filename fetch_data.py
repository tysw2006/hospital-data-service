import requests
import pymysql

# 1. DB 연결 정보
conn = pymysql.connect(
    host='127.0.0.1',
    port=3308,
    user='hosp_user',
    password='hosp_password',
    db='medical_data',
    charset='utf8mb4'
)

API_KEY = "27c6e6f62379b43e3c01acf13f97cbe55daee491561962f5b6e31e9e866c24a9"
URL = "http://apis.data.go.kr/B551182/hospInfoServicev2/getHospBasisList"

# 다양한 테스트를 위해 여러 지역과 진료과를 설정합니다.
# 110000: 서울, 210000: 부산, 310000: 경기
regions = {"110000": "서울", "210000": "부산", "310000": "경기"}
departments = {"01": "내과", "11": "소아청소년과", "04": "외과"}

total_inserted = 0

try:
    with conn.cursor() as cursor:
        # (1) 사용할 진료과목 기준표 미리 세팅
        for dept_cd, dept_name in departments.items():
            sql_dept = "INSERT IGNORE INTO departments (dept_cd, dept_name) VALUES (%s, %s)"
            cursor.execute(sql_dept, (dept_cd, dept_name))
        
        # (2) 지역별, 진료과별로 반복하며 데이터 100개씩 긁어오기
        for sido_cd, sido_name in regions.items():
            for dept_cd, dept_name in departments.items():
                print(f"[{sido_name} - {dept_name}] 병원 데이터 수집 중...")
                
                params = {
                    "serviceKey": API_KEY,
                    "pageNo": "1",
                    "numOfRows": "100", # 각 조합당 100개씩 가져옵니다.
                    "sidoCd": sido_cd,
                    "dgsbjtCd": dept_cd,
                    "_type": "json"
                }
                
                response = requests.get(URL, params=params)
                data = response.json()
                
                try:
                    items = data['response']['body']['items']['item']
                    # 데이터가 1개일 경우 딕셔너리로 반환되는 공공데이터 API 예외 처리
                    if not isinstance(items, list): 
                        items = [items]
                except (KeyError, TypeError):
                    continue # 데이터가 없으면 다음 조건으로 넘어감

                for item in items:
                    hosp_id = item.get('ykiho')
                    hosp_name = item.get('yadmNm')
                    address = item.get('addr')
                    phone = item.get('telno')
                    
                    sql_hosp = """
                    INSERT IGNORE INTO hospitals (hosp_id, hosp_name, address, phone, sido_cd)
                    VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql_hosp, (hosp_id, hosp_name, address, phone, sido_cd))
                    
                    sql_mapping = "INSERT IGNORE INTO hospital_departments (hosp_id, dept_cd) VALUES (%s, %s)"
                    cursor.execute(sql_mapping, (hosp_id, dept_cd))
                    
                    total_inserted += 1

    conn.commit()
    print(f"\n성공! 총 {total_inserted}개의 병원 데이터가 DB에 든든하게 채워졌습니다.")

except Exception as e:
    print(f"DB 저장 중 에러 발생: {e}")
    conn.rollback()
finally:
    conn.close()