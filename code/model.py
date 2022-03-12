# -*- coding: utf-8 -*-
# モデルの定義
from sqlalchemy import Column, Integer, String
from pydantic import BaseModel
from db import Base
from db import ENGINE

# excelテーブルのモデルExcelFileTableを定義
class ExcelFileTable(Base):
    __tablename__ = 'excel'
    id = Column(Integer, primary_key=True, autoincrement=True)
    filepath = Column(String(255), nullable=False)
    name = Column(String(30), nullable=False)


# POSTやPUTのとき受け取るRequest Bodyのモデルを定義
class ExcelFile(BaseModel):
    id: int
    filepath: str
    name: int


def main():
    # テーブルが存在しなければ、テーブルを作成
    Base.metadata.create_all(bind=ENGINE)


if __name__ == "__main__":
    main()
