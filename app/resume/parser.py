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
            clean_text = text.strip()
        if not clean_text:
            print(f"PDF에서 텍스트가 추출되지 않았습니다: {file_path}")
            return None  # 빈 PDF인 경우
        return clean_text
    except Exception as e:
        print(f"PDF 텍스트 추출 오류: {e}")
        return None