from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_sqlite_session.tools import get_engine, get_session

Base = declarative_base()


class FilterPower(Base):
    """ table filters """
    __tablename__ = 'filters'
    issue_channel = Column(String, primary_key=True)
    issue = Column(Integer)
    channel = Column(String)
    pow2x_length = Column(Integer)
    selected = Column(String)
    num10 = Column(String)

    def __init__(self, issue, channel, pow2x, selected, num10):
        self.issue_channel = f'{issue}_{channel}_{pow2x}'
        self.issue = issue
        self.channel = channel
        self.pow2x_length = pow2x
        self.selected = selected
        self.num10 = num10

    @classmethod
    def merge_one(cls, issue, channel, pow2x, selected, num10):
        """get issues[list]"""
        session = get_session()
        ins = cls(issue, channel, pow2x, selected, num10)
        session.merge(ins)
        session.commit()
        session.close()
        print(f">>>>>> merge one: {issue} - {channel} - {pow2x} - {selected} - {num10}")


if __name__ == "__main__":
    # generate tables
    engine = get_engine()
    Base.metadata.create_all(engine)
    pass
