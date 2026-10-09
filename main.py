from fastapi import FastAPI
from database import get_db_connection # 방금 만든 파일에서 DB 연결 함수를 가져옵니다.
from fastapi.middleware.cors import CORSMiddleware # CORS 도구 불러오기
from typing import Optional

app = FastAPI()

# CORS 방패 내리기 (프론트엔드의 접근을 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 로컬 개발 중이므로 일단 모든 주소의 접근을 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "공공 의료데이터 API 서버가 정상적으로 실행되었습니다!"}

# 브라우저에서 /hospitals 주소로 접속했을 때 실행될 코드
@app.get("/hospitals")
def get_hospitals():
    # 1. DB 연결
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 2. 병원 테이블에서 데이터 가져오기 (테스트용으로 10개만)
            sql = "SELECT hosp_id, hosp_name, address, phone FROM hospitals LIMIT 10"
            cursor.execute(sql)
            hospitals_data = cursor.fetchall()
            
            # 3. 가져온 데이터를 JSON 형태로 브라우저에 응답
            return {
                "status": "success",
                "total_count": len(hospitals_data),
                "data": hospitals_data
            }
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        conn.close() # 통신이 끝나면 DB 연결 문을 닫아줍니다.

@app.get("/hospitals/search")
def search_hospitals(region: Optional[str] = None, dept: Optional[str] = None):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 1. 3개의 테이블을 이어붙이는(JOIN) 기본 SQL 스케치
            sql = """
                SELECT DISTINCT h.hosp_id, h.hosp_name, h.address, h.phone 
                FROM hospitals h
                LEFT JOIN hospital_departments hd ON h.hosp_id = hd.hosp_id
                LEFT JOIN departments d ON hd.dept_cd = d.dept_cd
                WHERE 1=1
            """
            params = []

            # 2. '지역' 조건이 들어오면 주소에서 해당 지역명 필터링 추가
            if region:
                sql += " AND h.address LIKE %s"
                params.append(f"%{region}%")
            
            # 3. '진료과' 조건이 들어오면 진료과 이름에서 필터링 추가
            if dept:
                sql += " AND d.dept_name LIKE %s"
                params.append(f"%{dept}%")

            sql += " LIMIT 50" # 테스트를 위해 최대 50개까지만 가져오도록 제한

            cursor.execute(sql, params)
            hospitals_data = cursor.fetchall()
            
            return {
                "status": "success",
                "total_count": len(hospitals_data),
                "data": hospitals_data
            }
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()
