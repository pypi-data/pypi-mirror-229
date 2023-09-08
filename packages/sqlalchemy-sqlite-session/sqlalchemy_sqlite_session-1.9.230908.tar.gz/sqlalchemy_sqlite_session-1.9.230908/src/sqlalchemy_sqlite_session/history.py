from sqlalchemy import Column, String, Integer, Float
from sqlalchemy.orm import declarative_base
from sqlalchemy_sqlite_session.tools import get_engine, get_session
import json


Base = declarative_base()


def database_toast(issue: int, name_cn: str, name: str, key: str, value: str):
    """数据表属性 写入成功提示"""
    print(f">>> 合并数据成功，期号: {issue}，表名: {name_cn}-{name}: {key} - {value}")


class History3D(Base):
    """ history_3d """
    __tablename__ = 'history_3d'

    issue = Column(Integer, primary_key=True)
    content = Column(String, nullable=False)

    def __init__(self, issue, content):
        self.issue = issue
        self.content = content

    @classmethod
    def get_one(cls, issue):
        """get issues[list]"""
        session = get_session()
        i = session.query(cls).get(issue)
        session.close()
        result = eval(i.content)
        return result
    
    @classmethod
    def insert_one(cls, issue, content):
        session = get_session()
        ins = cls(issue, content)
        session.merge(ins)
        session.commit()
        session.close()

class HistoryP3(Base):
    """ history_p3 """
    __tablename__ = 'history_p3'

    issue = Column(Integer, primary_key=True)
    content = Column(String, nullable=False)

    def __init__(self, issue, content):
        self.issue = issue
        self.content = content

    @classmethod
    def get_one(cls, issue):
        """get issues[list]"""
        session = get_session()
        i = session.query(cls).get(issue)
        session.close()
        result = eval(i.content)
        return result
    
    @classmethod
    def insert_one(cls, issue, content):
        session = get_session()
        ins = cls(issue, content)
        session.merge(ins)
        session.commit()
        session.close()


if __name__ == "__main__":
    # engine = get_engine()
    # Base.metadata.create_all(engine)
    pass

