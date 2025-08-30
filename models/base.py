from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.ext.declarative import declared_attr

class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        name = cls.__name__[0].lower() + cls.__name__[1:]

        name = ''.join([f'_{ch.lower()}' if ch.isupper() else ch for ch in name])

        if name.endswith(('s', 'x', 'z', 'ch', 'sh')):
            return name + 'es'
        elif name.endswith('y'):
            return name + 'ies'
        else:
            return name + 's'