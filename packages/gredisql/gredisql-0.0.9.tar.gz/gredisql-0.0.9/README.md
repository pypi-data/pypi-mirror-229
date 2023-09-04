## GredisQL
A GraphQL interface for Redis Database. 

## How To Install
```python
pip install gredisql
```
If you find this project interesting, you can always appreciate it by giving it a Star. :D 

## A Background of `GredisQL`
![background_image](/img/gredisql-bg.png)

##  Motivation
1. I was bored, been sick for a while, had to lie on the bed. So I needed to create something. 
2. Redis has Web interface ( actually a REST interface), so I urged to build one in GraphQL. 
3. There are some pretty amazing GraphQL libraries around python echo system, I wanted to try them. 
4. Last but not least, jump into quick coding session, engage and nurture the human mind. LOL

## Design Philosophy
1. All the data `mutation` and `query` are not separated here by action and most probably all the actions are performed via `query` operation.
2. Technically `all` the requests sent to the GraphQL `server` was in `POST`, so I was initially okay with the implementation. 
3. `Strawberry-Graphql` is kind of server agnostic so either you can use `ASGI` or `WSGI` counterpart. 
4. Currently limiting the implementation with `WSGI` server, but I've plan to adopt `ASGI` in the journey, to support `subscription`. 
5. Not `all` Redis commands are found in the implementation, I'll try to cover it in the process. 

## Inspiration and Tools I used
1. `redis==5.0.0` is used to communicate with the Redis database. 
2. `strawberry-graphql` is used to do the heavy lifting. Also, I tried `ariadne` which is also another cool tool to try with.

## Features and Future Plans
1. [X] String Commands.
2. [X] List Commands. 
3. [X] Set Commands. 

And many more to come in the future iteration.

## Quick Starting the GraphQL Server
```python
if __name__ == "__main__":
    from gredisql.core import Server

    server = Server()
    server.run()
```
You can specify the `host`, `port` and `debug` mode in while instantiating the `GraphQL` server. 
Simply write, 
```python

if __name__ == "__main__":

    REDIS_HOST = 'redis-4343.c8.us-east-1-4.ec2.cloud.redislabs.com'
    REDIS_PORT = 16292
    REDIS_PASSWORD = 'your-secret-password'

    from gredisql.core import Server

    server = Server(
         REDIS_HOST=REDIS_HOST,
         REDIS_PORT=REDIS_PORT,
         REDIS_PASSWORD=REDIS_PASSWORD
    )
    server.run()

```
Now navigate to `http://localhost:5055/graphql` and voilà. 
