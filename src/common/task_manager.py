from concurrent.futures import ProcessPoolExecutor
from queue import Queue


def execute_iter_callback(parallel, iter_task_callback, done_callback):
    with ProcessPoolExecutor(max_workers=parallel) as executor:
        for task_callback in iter_task_callback:
            future = executor.submit(task_callback)
            future.add_done_callback(lambda fut: done_callback(fut.result()))
        executor.shutdown()
    #end-with
#end-def


def execute_iter_callback_and_get_data(parallel, iter_task_callback):
    myqueue = Queue()

    def done_callback(fut):
        myqueue.put(fut.result())

    with ProcessPoolExecutor(max_workers=parallel) as executor:
        for task_callback in iter_task_callback:
            future = executor.submit(task_callback)
            future.add_done_callback(lambda fut: done_callback(fut.result()))
        executor.shutdown()
    #end-with

    data = []
    while not myqueue.empty():
        data.append(myqueue.get())
    return data
#end-def