import asyncio


async def con_async(tasks, con_num=3):
    result = []
    for i in range(0, len(tasks), con_num):
        res = await asyncio.gather(*tasks[i:i + con_num], return_exceptions=True)
        result.extend(res)
    return result


def call_async(func):
    return asyncio.get_event_loop().run_until_complete(func)
