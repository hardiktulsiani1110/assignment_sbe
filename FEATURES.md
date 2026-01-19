# Features

- User role is categorized into three types: manager, member and admin
- a simple login route with jwt based access token
- role-based access for routes.
- admin can create and delete users
- manager can perform tasks crud, bulk update tasks, add/remove collaborators, and add task dependencies
- member can modify task (status only)
- all authenticated users (member, admin, manager) can view all users, all tasks, and also custom perform task filtering

## checks
- Only the owner of the task can modify the task.
- Member can only modify the task status, and that too if he is one of the collaborators of the task
- while modifying task status, we check if it has any dependency and make sure the pre_required_tasks are completed only then we can set the current task status to in_progress or completed.
- while creating a dependency we make sure that the pre_task and post_task status are valid like the above point, one should not be parent or ancestor of the other, and there should be no circular dependency
