# -*- coding: utf-8 -*-

"""
author: S.M. Sabbir Amin
date: 30 Aug 2023
email: sabbir.amin@goava.com, sabbiramin.cse11ruet@gmail.com

"""
import typing
import redis
import strawberry
from flask import Flask
from strawberry.flask.views import GraphQLView


@strawberry.type
class CommonString:
    response: typing.Optional[str]


class CommonDict:
    response: dict


@strawberry.input
class KeyVal:
    key: str
    value: str


class Server:
    def __init__(self,
                 host: str = 'localhost',
                 port: int = 5055,
                 debug=True,
                 REDIS_HOST: str = 'localhost',
                 REDIS_PORT: int = 6379,
                 REDIS_DB: int = 0,
                 REDIS_PASSWORD: str = '',
                 REDIS_DECODE_RESPONSE: bool = True
                 ):
        self.app = Flask(__name__)
        self.host = host
        self.port = port
        self.debug = debug
        self.REDIS_HOST = REDIS_HOST if REDIS_HOST else 'localhost'
        self.REDIS_PORT = REDIS_PORT if REDIS_PORT else 6379
        self.REDIS_DB = REDIS_DB if REDIS_DB else 0
        self.REDIS_PASSWORD = REDIS_PASSWORD if REDIS_PASSWORD else ''
        self.REDIS_DECODE_RESPONSE = REDIS_DECODE_RESPONSE if REDIS_DECODE_RESPONSE else True
        print('Connecting Redis, host:', self.REDIS_HOST, ', port:', self.REDIS_PORT)
        rr = redis.StrictRedis(host=self.REDIS_HOST,
                               port=self.REDIS_PORT,
                               db=self.REDIS_DB,
                               password=self.REDIS_PASSWORD,
                               decode_responses=self.REDIS_DECODE_RESPONSE)

        @strawberry.type
        class Query:
            @strawberry.field
            def set(self,
                    name: str,
                    value: str,
                    ex: typing.Optional[int] = None,
                    px: typing.Optional[int] = None,
                    nx: typing.Optional[bool] = False,
                    xx: typing.Optional[bool] = False,
                    keepttl: typing.Optional[bool] = False,
                    get: typing.Optional[bool] = False,
                    exat: typing.Optional[int] = None,
                    pxat: typing.Optional[int] = None
                    ) -> CommonString:
                resp = rr.set(
                    name=name,
                    value=value,
                    ex=ex,
                    px=px,
                    nx=nx,
                    xx=xx,
                    keepttl=keepttl,
                    get=get,
                    exat=exat,
                    pxat=pxat
                )
                return CommonString(response=resp)

            @strawberry.field
            def get(self, name: str) -> CommonString:
                resp = rr.get(name=name)
                return CommonString(response=resp)

            @strawberry.field
            def getex(self,
                      name: str,
                      ex: typing.Optional[int] = None,
                      px: typing.Optional[int] = None,
                      exat: typing.Optional[int] = None,
                      pxat: typing.Optional[int] = None,
                      persist: bool = False
                      ) -> CommonString:
                resp = rr.getex(name=name, ex=ex, px=px, exat=exat, pxat=pxat, persist=persist)
                return CommonString(response=resp)

            @strawberry.field
            def info(self) -> CommonString:
                info_dict = rr.info()
                print(info_dict)
                return CommonString(response=str(info_dict))

            @strawberry.field
            def mset(self, mappings: typing.List[KeyVal]) -> bool:
                mappings = {m.key: m.value for m in mappings}
                resp = rr.mset(mappings)
                return resp

            @strawberry.field
            def mget(self, keys: typing.List[str]) -> typing.List[str]:
                resp = rr.mget(keys=keys)
                return resp

            @strawberry.field
            def incrby(self, name: str, amount: int = 1) -> str:
                return rr.incrby(name=name, amount=amount)

            @strawberry.field
            def decrby(self, name: str, amount: int = 1) -> str:
                return rr.decrby(name=name, amount=amount)

            @strawberry.field
            def incrbyfloat(self, name: str, amount: float = 1.0) -> str:
                return rr.incrbyfloat(name=name, amount=amount)

            @strawberry.field
            def keys(self, pattern: str) -> typing.List[str]:
                return rr.keys(pattern=pattern)

            @strawberry.field
            def delete(self, names: typing.List[str]) -> str:
                return rr.delete(*names)

            @strawberry.field
            def exists(self, names: typing.List[str]) -> str:
                return rr.exists(*names)

            @strawberry.field
            def append(self, key: str, value: str) -> str:
                return rr.append(key=key, value=value)

            @strawberry.field
            def expire(
                    self,
                    name: str,
                    time: int,
                    nx: typing.Optional[bool] = False,
                    xx: typing.Optional[bool] = False,
                    gt: typing.Optional[bool] = False,
                    lt: typing.Optional[bool] = False) -> str:
                return rr.expire(
                    name=name,
                    time=time,
                    nx=nx,
                    xx=xx,
                    gt=gt,
                    lt=lt
                )

            @strawberry.field
            def expireat(
                    self,
                    name: str,
                    when: int,
                    nx: typing.Optional[bool] = False,
                    xx: typing.Optional[bool] = False,
                    gt: typing.Optional[bool] = False,
                    lt: typing.Optional[bool] = False) -> str:
                return rr.expireat(
                    name=name,
                    when=when,
                    nx=nx,
                    xx=xx,
                    gt=gt,
                    lt=lt
                )

            @strawberry.field
            def getdel(self, name: str) -> str:
                return rr.getdel(name=name)

            ## Redis Sets
            @strawberry.field
            def sadd(self, name: str, values: typing.List[str]) -> int:
                return rr.sadd(name, *values)

            @strawberry.field
            def scard(self, name: str) -> int:
                return rr.scard(name=name)

            @strawberry.field
            def sdiff(self, keys: typing.List[str],
                      ) -> typing.List[str]:
                answers = rr.sdiff(keys)
                return answers

            @strawberry.field
            def sdiffstore(self,
                           keys: typing.List[str],
                           dest: str) -> int:
                return rr.sdiffstore(dest=dest,
                                     keys=keys)

            @strawberry.field
            def sinter(self,
                       keys: typing.List[str]) -> typing.List[str]:
                return rr.sinter(keys)

            @strawberry.field
            def sinterstore(self,
                            keys: typing.List[str],
                            dest: str
                            ) -> int:
                return rr.sinterstore(dest=dest, keys=keys)

            @strawberry.field
            def sismember(self,
                          name: str,
                          value: str
                          ) -> int:
                return rr.sismember(name=name, value=value)

            @strawberry.field
            def smembers(self,
                         name: str
                         ) -> typing.List[str]:
                return rr.smembers(name=name)

            @strawberry.field
            def sismember(self,
                          name: str,
                          value: str
                          ) -> int:
                return rr.sismember(name=name, value=value)

            @strawberry.field
            def smove(self,
                      src: str,
                      dst: str,
                      value: str
                      ) -> int:
                return rr.smove(src=src, dst=dst, value=value)

            @strawberry.field
            def spop(self,
                     name: str,
                     count: typing.Optional[int]
                     ) -> int:
                return rr.spop(name=name, count=count)

        self.schema = strawberry.Schema(Query)
        self.app.add_url_rule(
            "/graphql",
            view_func=GraphQLView.as_view("graphql_view", schema=self.schema),
        )

    def run(self):
        self.app.run(
            host=self.host,
            port=self.port,
            debug=self.debug
        )
