
from pydantic import BaseModel
from graphene import ObjectType

__all__ = ('BaseObjectArgs', 'BaseObjectType')


class BaseObjectArgs(BaseModel):
    def get(self, key):
        return getattr(self, key, None)


class BaseObjectType(ObjectType):
    _args: BaseObjectArgs = None

    def __init__(self, *args, **kwargs):
        if kwargs.get('_args') is not None:
            _args = kwargs.pop('_args')
            if not isinstance(_args, BaseObjectArgs):
                raise TypeError("BaseObjectType args is not BaseObjectArgs")
            self._args = _args
        super().__init__(*args, **kwargs)


if __name__ == '__main__':
    from graphene import Enum
    import enum
    from typing import Optional

    class DAOsFilterEnum(Enum):
        all = 0
        owner = 1
        following = 2
        following_and_owner = 3
        member = 4


    class ExampleArgs(BaseObjectArgs):
        dao_id: str
        filter: Optional[enum.Enum]

    try:
        bot = ExampleArgs(a='v')
    except Exception as e:
        print(e)

    try:
        base = BaseObjectArgs(a='v')
    except Exception as e:
        print(e)

    try:
        bot = ExampleArgs(dao_id=1)
    except Exception as e:
        print(e)

    try:
        bot = ExampleArgs(dao_id='1', filter=DAOsFilterEnum.owner)
        a = BaseObjectType(_args=bot)

    except Exception as e:
        print(e)
