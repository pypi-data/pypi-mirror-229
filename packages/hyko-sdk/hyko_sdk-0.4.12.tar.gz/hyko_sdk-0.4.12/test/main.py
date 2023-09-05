from hyko_sdk import SDKFunction
from pydantic import BaseModel
import asyncio


func = SDKFunction(
    description="",
    requires_gpu=False,
)


# @func.on_startup
# async def test_start():
#     print("starting 1")
#     await asyncio.sleep(10)
#     raise Exception("Something happened here")
#     print("startup 1 done")


@func.on_startup
async def test_start_2():
    print("starting 2")
    await asyncio.sleep(10)
    print("startup 2 done")


class Inputs(BaseModel):
    pass

class Params(BaseModel):
    pass

class Outputs(BaseModel):
    pass


@func.on_execute
async def exec(inputs: Inputs, params: Params) -> Outputs:
    return Outputs()

