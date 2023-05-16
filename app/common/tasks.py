from rocketry import Rocketry
from rocketry.conds import minutely

rocketry = Rocketry()


@rocketry.task(minutely)
async def task_test() -> None:
    print('test task')
