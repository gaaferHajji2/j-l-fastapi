For handling **FastAPI + Redis** in async mode in 2026, the landscape has consolidated. The old `aioredis` library has been merged into the official `redis-py` client.

Here are the best packages depending on your use case:

### 1. The Standard Choice: `redis-py` (with `asyncio`)
**Package:** `redis`
**Why:** It is the official Redis client. Since version 4.2+, it has built-in, stable async support. It is the most maintained, documented, and "senior-standard" choice for general-purpose caching, session storage, and simple pub/sub.

*   **Installation:**
    ```bash
    pip install redis[hiredis]
    ```
    *(Note: `hiredis` is a C-based parser that makes serialization/deserialization significantly faster.)*

*   **How to use with FastAPI:**
    ```python
    import redis.asyncio as redis
    from fastapi import FastAPI, Depends

    app = FastAPI()

    # Dependency to get Redis connection
    async def get_redis():
        # In production, use a connection pool
        client = redis.Redis.from_url("redis://localhost:6379", decode_responses=True)
        try:
            yield client
        finally:
            await client.close()

    @app.get("/cache/{key}")
    async def read_cache(key: str, redis_client: redis.Redis = Depends(get_redis)):
        value = await redis_client.get(key)
        if value is None:
            return {"message": "Not found"}
        return {"key": key, "value": value}
    ```

### 2. The Developer Experience Choice: `redis-om`
**Package:** `redis-om`
**Why:** If you love Pydantic (which you do, since you use FastAPI), `redis-om` is a game-changer. It provides an **Object Mapper** for Redis. It allows you to define Redis models using Pydantic, handle indexing, and perform complex queries without writing raw Redis commands.

*   **Best for:** When you need to store structured objects in Redis and query them (e.g., filtering users by age, status, etc.).
*   **Installation:**
    ```bash
    pip install redis-om
    ```

*   **Example:**
    ```python
    from redis_om import Model, Field
    import typing

    class User(Model):
        first_name: str = Field(index=True)
        last_name: str = Field(index=True)
        age: int = Field(index=True)

        class Meta:
            database = redis.Redis.from_url("redis://localhost:6379")

    # Querying like an ORM
    users = await User.find(User.age > 25).all()
    ```

### 3. The Background Task/Queue Choice: `arq` or `taskiq`
If you are using Redis not just for caching but for **job queues** (background tasks), do not use raw `redis-py`. Use a dedicated async queue library.

*   **`arq`**: Lightweight, built specifically for asyncio and Redis. Very popular in the FastAPI community.
*   **`taskiq`**: A newer, more flexible async task queue that supports Redis, RabbitMQ, and other brokers. It has better integration with FastAPI dependencies.

---

### Senior Engineer Recommendations & Best Practices

1.  **Use Connection Pools:**
    Never create a new `redis.Redis()` instance per request. Create a **single connection pool** at startup and reuse it.
    ```python
    from fastapi import FastAPI
    import redis.asyncio as redis

    app = FastAPI()

    @app.on_event("startup")
    async def startup():
        app.state.redis = redis.Redis.from_url(
            "redis://localhost:6379",
            decode_responses=True,
            max_connections=50  # Adjust based on load
        )

    @app.on_event("shutdown")
    async def shutdown():
        await app.state.redis.close()
    ```

2.  **Use `hiredis`:**
    Always install `hiredis` alongside `redis`. It speeds up parsing of Redis responses by ~3-5x.

3.  **Handle Exceptions Gracefully:**
    Redis can go down. Wrap your Redis calls in try-except blocks or use a fallback mechanism (e.g., if Redis fails, read directly from the database).

4.  **Serialization:**
    If you’re storing complex objects, use `orjson` for serialization before saving to Redis, especially if you’re not using `redis-om`.
    ```python
    import orjson
    await redis_client.set("key", orjson.dumps(data))
    data = orjson.loads(await redis_client.get("key"))
    ```

### Summary: Which one should you choose?

| Use Case | Recommended Package |
| :--- | :--- |
| **General Caching / Sessions / Simple Key-Value** | `redis` (redis-py) |
| **Structured Data / Querying / ORM-like experience** | `redis-om` |
| **Background Jobs / Task Queue** | `arq` or `taskiq` |
| **Pub/Sub Messaging** | `redis` (redis-py) |

For most FastAPI applications, start with **`redis` (redis-py)** for caching and **`arq`** for background tasks. If you find yourself writing too much boilerplate to serialize/deserialize objects, switch to **`redis-om`**.