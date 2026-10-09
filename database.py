import pymysql

def get_db_connection():
    return pymysql.connect(
        host='127.0.0.1',
        port=3308,            # 우리가 설정한 MySQL 포트
        user='hosp_user',
        password='hosp_password',
        db='medical_data',
        charset='utf8mb4',
        # DictCursor: DB에서 가져온 데이터를 딕셔너리 형태로 만들어줍니다. (JSON 변환에 아주 유리함)
        cursorclass=pymysql.cursors.DictCursor 
    )