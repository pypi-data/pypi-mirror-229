from selenium_driverless.scripts.switch_to import SwitchTo as AsyncSwitchTo
import asyncio
import inspect


class SwitchTo(AsyncSwitchTo):
    def __init__(self, driver, loop):
        super().__init__(driver=driver)
        if not loop:
            loop = asyncio.new_event_loop()
        self._loop = loop
        self._loop.create_task(self._init())

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.__aexit__(*args, **kwargs)

    def __getattribute__(self, item):
        item = super().__getattribute__(item)
        if item is None:
            return item
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            if inspect.iscoroutinefunction(item):
                def syncified(*args, **kwargs):
                    return self._loop.run_until_complete(item(*args, **kwargs))
                return syncified
            if inspect.isawaitable(item):
                return self._loop.run_until_complete(item)
        return item
