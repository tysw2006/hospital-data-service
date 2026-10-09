import requests

# 복사한 일반 인증키(Decoding)를 아래 문자열 안에 넣으세요
API_KEY = "27c6e6f62379b43e3c01acf13f97cbe55daee491561962f5b6e31e9e866c24a9"

# 병원 기본정보 API (서울 지역, 내과 예시)
URL = "https://apis.data.go.kr/B551182/hospInfoServicev2/getHospBasisList"
params = {
    "serviceKey": API_KEY,
    "pageNo": "1",
    "numOfRows": "5",
    "sidoCd": "110000",   # 서울특별시 코드
    "dgsbjtCd": "01",     # 내과 코드
    "_type": "json"       # 다루기 쉬운 JSON 포맷으로 요청
}

response = requests.get(URL, params=params)

print(f"응답 상태: {response.status_code}")
print("병원 데이터:")
print(response.text)