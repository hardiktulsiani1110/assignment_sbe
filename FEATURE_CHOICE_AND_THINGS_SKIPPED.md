# Things Overlooked and Feature Choice Reasons

## Because of the time constraint and scope, some of the things are skipped which would have been necessary in an ideal production scenario
- APIs are sync, ideally should be async with async query execution so that it can utilize the event loop to handle concurrent requests
- We are not storing the session token in db currently, ideally we should store it in db as it is the standard practice.
- We are not using caching here. Redis can be used for caching which will avoid hitting our db every time for fetch.
- Proper docstrings, api documentation and pydantic model documentation is not followed


## Product Feature choice reasons
- choosing Task Filtering: This is something which is very vital to a task management system and is heavily used. Things have to be dynamic, and we can add as many conditions as we want. Seemed a necessary feature plus nice implementation if we follow the proper OOPS way.
- choosing Task Dependencies: This is something which is complex to implement, because it will involve using graphs (Directed Acyclic Graph). We will also have to check for cycle. and we have to check for pre_tasks and post_tasks status as well for tracking blocking status. It seemed a very great challenge, plus I love graph anyways.