from fastapi import FastAPI, File, UploadFile
from typing import List  # ネストされたBodyを定義するために必要
from starlette.middleware.cors import CORSMiddleware  # CORSを回避するために必要
from db import session  # DBと接続するためのセッション
from model import ExcelFileTable, ExcelFile  # 今回使うモデルをインポート
from controllers import *
import shutil
import os
from convert import InformationInput, Convert
from minio import Minio

app = FastAPI()

ALLOWED_EXTENSIONS = set(['pdf'])
UPLOAD_FOLDER = './convert/upload'
FORMAT_PATH = '../docker/minio/develop/format.xlsx'

# CORSを回避するために設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

minioClient = Minio('127.0.0.1:9000',
                access_key=os.getenv(key='MINIO_ACCESS_KEY', default='minio'),
                secret_key=os.getenv(key='MINIO_SECRET_KEY', default='minio123'),
                secure=False)


# ----------APIの定義------------
#minioからformat.xlsxを取得 GET
@app.get("/download")
async def format_file_set():
    dl = minioClient.fget_object("export", "develop", "format.xlsx")
    return {"dl": dl}

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    if file and allowed_file(file.filename):
        filename = file.filename
        fileobj = file.file
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        with open(filename,'wb') as upload_dir:
            shutil.copyfileobj(fileobj, upload_dir)
        filepath = shutil.move("./" + filename , filepath)
        convert = Convert.Convert(filepath)
        convert.tableExtraction()
        convert.convertExcel()
        info = InformationInput.InformationInput(convert.getExpath())
        info.iterCols()
        info.addDataByColumn()
        info.createExcel()
        name, path = info.getPathName()
        return {"アップロードされたファイル": name, "ファイルのパス": path}
    if file and not allowed_file(file.filename):
        return {"warning": "許可されたファイルタイプではありません"}

app.add_api_route('/', index)