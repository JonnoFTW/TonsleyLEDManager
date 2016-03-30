from sqlalchemy import (
    Column,
    Integer,
    Text,
    String,
    Date,
    Time,
    ForeignKey, Boolean)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import engine_from_config
import transaction
from sqlalchemy.orm import (
    relationship,
    sessionmaker,
    scoped_session)

from cgi import escape
import json
from zope.sqlalchemy import ZopeTransactionExtension, register

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
DBase = declarative_base()


def create_session(request):
    sessionmaker = request.registry['db_sessionmaker']
    session = sessionmaker()
    register(session, transaction_manager=request.tm)
    return session


def pyramid_tm_hook(request=None):
    return transaction.TransactionManager()


def includeme(config):
    config.add_settings({'tm.manager_hook': pyramid_tm_hook})
    settings = config.get_settings()
    config.include('pyramid_tm')
    engine = engine_from_config(settings, 'sqlalchemy.')
    maker = sessionmaker()
    maker.configure(bind=engine)
    config.registry['db_sessionmaker'] = maker
    config.add_request_method(create_session, 'db_session', reify=True)

Base = DBase

class ABase(DBase):
    __abstract__ = True

    def __json__(self, request=None, seen=None):
        if seen is None:
            seen = set()
        fields = {}
        if self not in seen:
            seen.add(self)
        else:
            return fields
        for field in [x for x in dir(self) if not x.startswith('_') and x not in ['metadata', 'password']]:
            val = self.__getattribute__(field)
            if isinstance(val, basestring):
                val = escape(val)
            elif isinstance(val, Base):
                val = val.__json__(request, seen)
            elif isinstance(val, list) and len(val) > 0 and isinstance(val[0], Base):
                val = [i.__json__(request, seen) for i in val]
            fields[field] = val
        # a json-encodable dict
        return fields

    def _as_dict(self):
        return self.__json__()

    def _to_json_str(self):
        return json.dumps(self._as_dict())


class LedSchedule(Base):
    __tablename__ = 'led_schedule'

    id = Column(Integer, primary_key=True)
    name = Column(String(45), nullable=False)
    length = Column(Integer, nullable=False)
    code = Column(Text, nullable=False)
    user_id = Column(ForeignKey(u'led_user.id'), index=True)
    position = Column(Integer)
    enabled = Column(Boolean, server_default="'1")
    time_from = Column(Time, nullable=True)
    time_to = Column(Time, nullable=True)
    days_of_week = Column(Integer, nullable=True)
    repeats = Column(Integer, nullable=True)
    date_from = Column(Date, nullable=True)
    user = relationship(u'LedUser')


class LedUser(Base):
    __tablename__ = 'led_user'

    id = Column(Integer, primary_key=True)
    email = Column(String(128), nullable=False)
    password = Column(String(128), nullable=False)
    access_level = Column(Integer, nullable=False, server_default="'0'")
