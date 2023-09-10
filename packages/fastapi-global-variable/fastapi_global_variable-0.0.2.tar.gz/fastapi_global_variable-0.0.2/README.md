# FastAPI event

## How to use

1. Inject the `event_emitter` into Service dependencies to use

```python

# user_service.py
from fastapi_event import get_event_emitter


class UserService:
    def __init__(self, event_emitter=get_event_emitter()):
       self.event_emitter = event_emitter

    async def deactivate_user(self, user: UserEntity):
        await self.user_repo.update_by_id(user.id, data={'deactivated_at': datetime.datetime.utcnow()})

        await self.event_emitter.emit(UserEvent.DEACTIVATED, user.id)
```

2. Create `observer` file to listen `event` and handle it

```python
# users/observers/user_observer.py
from fastapi_event import observer, event

@observer('user:*')
class UserObserver:
    def __init__(self, notification_service: NotificationService = Depends()):
        self.notification_service = notification_service

    @event(UserEvent.DEACTIVATED)
    async def handle_user_deactivated_for_related_user_tasks(self, user_id: UUID):
        # Add logic here
```

If we need to update user related jobs in another module, we should create the `UserObserver` in that module followed by `modular based` too
Such as, we need to update caches of user posts

```python
# posts/observers/user_observer.py
from fastapi_event import observer, event

@observer('user:*')
class UserObserver:
    @event(UserEvent.DEACTIVATED)
    async def handle_user_deactivated_for_related_post_tasks(self, user_id: UUID):
        await queue.add_to_queue(PostTask.CACHE_COUNT_COMMENT, user_id)

```

## Caveat

Currently, the @observer has a limitation that when I inject a service
and that service's dependencies are injected with an event_emitter, it will encounter an erjor.

Right now, to fix this issue we should move the affected service to a separate one without injecting the event_emitter,
or directly importing the repository to execute the queries.

It happens because we need to collect all the `observer` class before injecting the `event_emitter` dependency inside that service.

Example:

Let's say we have a feature called `deactivated user`. We will emit the `deactivate_user` event then handle it in the `observer`
Inside the `observer` after hanlding what needes to be done, we will push notification to user to force them logout
To do that, we want to inject the `NotificationService`, inside the `NotificationService` dependencies we have some other tasks
that need to inject the `MediaService`.

**The issue happens here**. The `MediaService` dependencies we inject the `event_emitter` that will lead to the rest `observers`
will never collect any `__Observer` class anymore.

```python
# media_service.py
from fastapi_event import get_event_emitter

class MediaService:
    def __init__(self, event_emitter=get_event_emitter()),
):
        self.media_service = media_service

    async def create(self):
        # Logic

# notification_service.py
class NotificationService:
    def __init__(self, media_service: MediaService = Depends()):
        self.media_service = media_service

    async def emit(self):
        # Logic

# users/observers/user_observer.py
from fastapi_event import observer, event

@observer('user:*')
class UserObserver:
    def __init__(self, notification_service: NotificationService = Depends()):
        self.notification_service = notification_service

    @event(UserEvent.DEACTIVATED)
    async def handle_user_deactivated_for_related_user_tasks(self, user_id: UUID):
        # Add logic here

```

To temporarily resolve this issue, we have 2 ways:

- Try to not inject `MediaService` inside the `NotificationService`
- Move the `NotificationService` method inside the `UserObserver` and inject the `notification_repo` directly

## How to test in testpypi

1. Increase the version in `pyproject.toml`
2. Run command

```bash
$ . ./build_and_test.sh
```

## How to publish new version

1. Increase the version in `pyproject.toml`
2. Run command

```bash
$ . ./build_and_publish.sh
```
