# Standard library
import asyncio
import time

# Third party
import aioredis


######
# MAIN
######


class RedisBucket(object):
    def __init__(self, rate_limit, bucket_key, redis):
        # Per-second rate limit
        self._rate_per_sec = rate_limit / 60

        # Redis
        self._redis = redis
        self._bucket_key = bucket_key
    
    async def _has_capacity_async(self, amount):
        async with aioredis.lock.Lock(self._redis, f"{self._bucket_key}:lock"):
            pipeline = self._redis.pipeline()

            pipeline.get(f"{self._bucket_key}:last_checked")
            pipeline.get(f"{self._bucket_key}:capacity")

            current_time = asyncio.get_event_loop().time()

            last_checked, capacity = await pipeline.execute()

            if not last_checked or not capacity:
                last_checked = current_time
                capacity = self._rate_per_sec
            
            time_passed = current_time - float(last_checked)
            new_capacity = min(self._rate_per_sec, float(capacity) + time_passed * self._rate_per_sec)

            pipeline.set(f"{self._bucket_key}:last_checked", current_time)

            if new_capacity < amount:
                pipeline.set(f"{self._bucket_key}:capacity", new_capacity)
                await pipeline.execute()
                return False
            
            pipeline.set(f"{self._bucket_key}:capacity", new_capacity - amount)
            await pipeline.execute()

            return True

    async def wait_for_capacity(self, amount):
        while not await self._has_capacity_async(amount):
            await asyncio.sleep(1 / self._rate_per_sec)