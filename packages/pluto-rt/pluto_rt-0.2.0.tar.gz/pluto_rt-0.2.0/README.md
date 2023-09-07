# Pluto-RT: Real-time web results for long-running processes

Any time you have a need to trigger a long-running process from a web view, you run into Python's
blocking nature - nothing will be displayed until the process is complete, and you'll hit timeouts
if you exceed the default timeout for your web application process.

To solve the long-running aspect, we turn to background workers like django-q or django-celery. But
then the user has no insight into what the background worker is doing.

Pluto-RT solves that by using Redis as a message queuing service. Messages can be placed on the
queue by the background worker and their order is remembered. As messages are retrieved from the
queue, it returns the oldest ones first.

https://user-images.githubusercontent.com/102694/233860792-652f8790-6f31-4dd8-8c37-fc479171c576.mov

The overall strategy is this:

1. Invoke your background processor (worker) with a unique queue name
1. The worker places messages onto the queue, associated with that name
1. A private internal API (htmx, really) retrieves and removes the oldest `n` messages from that queue
1. HTMX polling from the web view appends the results of each "gulp" to a display table


## Prerequisites

We assume you already have these installed and working

- A running Django project
- A running Redis server
- A base project template called `base.html` (use a custom template if not - see below)
- Your `base.html` includes HTMX
- A runnning background processor such as django-q or django-celery
- A standalone function that processes data and whose real-time output you want to display
- A `KEY_PREFIX` is defined in in your project cache settings, e.g.

```
CACHES = {
    "default": {
        ...
        "BACKEND": "django_redis.cache.RedisCache",
        "KEY_PREFIX": config.REDIS_PREFIX,  # or some fixed string for your project
        ...
    }
}
```

## Installation:

- `pip install pluto-rt`
- Add `pluto_rt` to the list of installed apps in project settings.
- To enable the internal API (required), add this to your top-level urls.py:

```
path("rt_messages/", include("pluto_rt.urls")),
```

## Usage
There are two views you'll need to control: the view that kicks off the process
and passes tasks to the background worker, and the view that consumes the results.

## Stop polling

If the the value of an element on the queue is the string "queue_exhausted"
the view will return http 286, which tells htmx to stop polling. So in your
processing function, be sure to create one last item with that value to
signal that work is done.

### Calling the process

First: Work to be done should be defined in a single function, which will be passed to the
background worker.  The calling view should generate a descriptive queue name, made relatively
unique with an ID (upload ID works well for this). It should invoke your background processor with
that function and the queue name as arguments, then redirect to the display view. For example:

```
from django.views import View

class Home(View):
    """
    On POST, receive upload ID (or something unique-ish), generate a queue_name,
    and call a background process that acceps the queue_name. Then redirect
    to the real-time results display view.
    """

    def get(self, request):
        ctx = {}
        return render(request, "home.html", ctx)

    def post(self, request):
        upload_id = request.POST.get("upload_id")
        queue_name = f"demo_run_{upload_id}"
        async_task(
            sample_ops_function,
            queue_name=queue_name,
        )
        return redirect(reverse("rt_demo", kwargs={"queue_name": queue_name}))
```

### Background worker

The invocation above refers to `sample_ops_function` which can be any function
in your project. The function *must* accept a `queue_name` argument. This demo
example just generates some random messages with random states and pushes them
onto the queue.

```
from pluto_rt.views import get_rt_queue_handle
from faker import Faker
import random


def sample_ops_function(queue_name: str):
    """
    Demo function that processes data, such as reading and
    handling rows of an ETL job (reading a spreadsheet, sending email, whatever.)
    In this case, we just generate `n` random messages and put them
    on the queue. The html template is responsible for popping those
    messages off the queue. In real-world use, this function would be some
    long-running ETL or other task that can be reasonably chunked.

    Args:
        Required queue_name (generated in the calling view and passed in)

    """
    mqueue = get_rt_queue_handle(queue_name)

    for idx in range(1, 26):
        # Do some work here, on a row or any task chunk, then emit a message

        msg = f"{idx}: {Faker().sentence()}"
        statuses = ["success", "danger", "info", "warning"]

        row_dict = {"status": random.choice(statuses), "msg": msg}
        mqueue.push(row_dict)

    row_dict = {"status": "success", "msg": "Demo complete"}
    mqueue.push(row_dict)
    mqueue.push("queue_exhausted")

```

### Displaying results

The invoking view above redirects to the real-time results display view, which would
be written something like this:

```
class DemoResults(View):
    """
    This view accepts the queue_name and renders HTML that uses
    the queue_name to call the internal API, grabbing some number of
    items, separated by some delay.
    """

    def get(self, request, queue_name: str):
        """
        Real-time results display of demo report run
        """

        ctx = {
            "queue_name": queue_name,
            "num_per_gulp": 100,
            "interval_seconds": 3,
            "upload": upload,
        }

        return render(request, "yourpage.html", ctx)
```

Then include this block in `yourpage.html` where you want the results to appear:

```
{# Real-time results are appended to table rows via htmx #}
{% include "pluto_rt/table_partial.html" %}
```

Note: If you just need a simple results page with no customization, you can
skip creating your own template with the include, instead render your view
directly to template `pluto_rt/table.html` (which is badly named for backwards
compatibility).


## Distribution and license

Creating this as a private ES github repo first, for re-usability,
with intention to secure permission to open source it in the future.

When this is pip-installed, it will install the wheel, which means you need to recompile the wheel after making changes. After final commit, change the version in pyproject.toml, then run

`python3 -m build`

Then commit the changes and publish the update to pypi with:

`twine upload dist/pluto_rt-0.1.2.tar.gz`

(replacing the actual build number).

## Versions

0.1.0 Initial version

0.2.0 Sep 1, 2023: Replaced defunct QR3 lib with our own queueing code (made pluto self-sufficient).
    Introduced support for including template partials rather than full-page only.