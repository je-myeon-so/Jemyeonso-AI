import os
import pdfplumber
from fastapi import UploadFile
import tempfile
import shutil

# PDF에서 텍스트 추출하는 함수
def extract_text_from_pdf(file_path):
    try:
        with pdfplumber.open(file_path) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        return text.strip()
    except Exception as e:
        print(f"PDF 텍스트 추출 오류: {e}")
        return None

# FastAPI의 UploadFile에서 텍스트 추출
async def file_extract(upload_file: UploadFile):
    if not upload_file.filename.lower().endswith('.pdf'):
        return None
    
    # 임시 파일 생성
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    try:
        # 업로드된 파일 내용을 임시 파일에 저장
        shutil.copyfileobj(upload_file.file, temp_file)
        temp_file.close()
        
        # 임시 파일에서 텍스트 추출
        text = extract_text_from_pdf(temp_file.name)
        return text
    except Exception as e:
        print(f"파일 처리 오류: {e}")
        return None
    finally:
        # 임시 파일 삭제
        os.unlink(temp_file.name)
        # 파일 스트림 위치 리셋
        await upload_file.seek(0)
