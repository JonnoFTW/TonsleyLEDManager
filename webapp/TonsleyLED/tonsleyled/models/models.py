from sqlalchemy import (
    Column,
    Integer,
    Text,
    text,
    String,
    Date,
    Time,
    ForeignKey,
    Boolean,
    DateTime
    )
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import engine_from_config
import transaction
from sqlalchemy.ext.hybrid import hybrid_property
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

    def cleanup(request):
        session.close()

    request.add_finished_callback(cleanup)
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


class LedGroup(ABase):
    __tablename__ = 'led_group'

    id = Column(Integer, primary_key=True)
    name = Column(String(45), nullable=False)
    time_from = Column(Time)
    time_to = Column(Time)
    days_of_week = Column(String(7))
    repeats = Column(Integer)
    enabled = Column(Integer)
    default = Column(Integer)
    date_from = Column(Date)


class LedGroupUser(ABase):
    __tablename__ = 'led_group_users'

    led_group_id = Column(ForeignKey(u'led_group.id'), primary_key=True, nullable=False, index=True)
    led_user_id = Column(ForeignKey(u'led_user.id'), primary_key=True, nullable=False, index=True)
    access_level = Column(Integer, nullable=False, server_default=text("'0'"))

    led_group = relationship(u'LedGroup')
    led_user = relationship(u'LedUser')


class LedPlugin(ABase):
    __tablename__ = 'led_plugin'

    id = Column(Integer, primary_key=True)
    name = Column(String(45), nullable=False)
    code = Column(Text, nullable=False)
    user_id = Column(ForeignKey(u'led_user.id'), index=True)

    user = relationship(u'LedUser')


class LedSchedule(ABase):
    __tablename__ = 'led_schedule'

    led_group_id = Column(ForeignKey(u'led_group.id'), primary_key=True, nullable=False, index=True)
    led_plugin_id = Column(ForeignKey(u'led_plugin.id'), primary_key=True, nullable=False, index=True)
    duration = Column(Integer)
    enabled = Column(Integer)
    position = Column(Integer)
    message = Column(Text)

    led_group = relationship(u'LedGroup')
    led_plugin = relationship(u'LedPlugin')


class LedUser(ABase):
    __tablename__ = 'led_user'

    id = Column(Integer, primary_key=True)
    email = Column(String(8), nullable=False)
    access_level = Column(Integer, nullable=False, server_default=text("'0'"))

    @hybrid_property
    def admin(self):
        return self.access_level == 2

    def __repr__(self):
        return "<LedUser id:{} FAN:{}, access:{}>".format(self.id, self.email, self.access_level)


class LedLog(Base):
    __tablename__ = 'led_log'

    id = Column(Integer, primary_key=True)
    datetime = Column(DateTime, nullable=False)
    email = Column(String(8), nullable=False)
    action = Column(String(255), nullable=False)
