# 베이스 이미지로 Python 3.9 사용
FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# 필요 패키지 복사
COPY requirements.txt requirements.txt

# 필요한 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 전체 복사
COPY . .

# Flask API가 실행될 포트 설정 (Flask 기본 포트는 5000)
EXPOSE 5000

# Gunicorn을 사용하여 애플리케이션 실행
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]