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
import boto3

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

#s3_endpoint_url = os.getenv('AWS_S3_ENDPOINT_URL', None)
#print("-------------",s3_endpoint_url)
s3 = boto3.client("s3",'us-east-1', endpoint_url="http://127.0.0.1:9000",
                         aws_access_key_id="minio",
                         aws_secret_access_key="minio123")
# ----------APIの定義------------
#minioからformat.xlsxを取得 GET
@app.post('/Upload/')
async def upload_file(file: UploadFile = File(...)):
    res = s3.list_objects_v2(Bucket='bucket-name')
    return {'ret': res}

@app.get("/download")
async def format_file_set():
    #res = s3.list_objects_v2(Bucket='localo-pdf2excel')
    contents = s3.list_objects(Bucket="localo-pdf2excel")
    return {'res': contents}

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