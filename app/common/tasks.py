from rocketry import Rocketry


rocketry = Rocketry(execution='thread')


# @rocketry.task(minutely)
async def task_test() -> None:
    print('test task')
