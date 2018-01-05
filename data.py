from sqlalchemy import (create_engine,Table,Column,Integer,String,MetaData)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


engine = create_engine("mysql://root:YES@localhost/orders")

Base = declarative_base()

class Order(Base):
    __tablename__ = "order"
    Id = Column(Integer,primary_key=True,autoincrement=True)
    uid = Column(String(40))
    validTime = Column(Integer)
    length = Column(Integer)

    @property
    def serial(self):
        return {
            "uid":self.uid,
            "validTime":self.validTime,
            "length":self.length
        }
Base.metadata.bind=engine
Base.metadata.create_all()
Session = sessionmaker(bind=engine)
ses = Session()