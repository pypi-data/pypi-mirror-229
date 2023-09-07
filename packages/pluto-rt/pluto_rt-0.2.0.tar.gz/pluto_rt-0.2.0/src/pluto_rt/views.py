from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from redis.connection import Connection, SSLConnection, urlparse
from pluto_rt.ops import Queue


def get_rt_queue_handle(queue_name: str):
    """Get or create a handle on a redis message queueing connection,
    for reading or writing.

    Identifier should include a function descriptor and ID like
    "equipment_upload_357" or "dragonfly_report_74"
    """
    rs = urlparse(settings.CACHES["default"]["LOCATION"])
    prefix = settings.CACHES["default"]["KEY_PREFIX"]
    mqueue = Queue(
        f"{prefix}_{queue_name}",
        host=rs.hostname,
        username=rs.username,
        password=rs.password,
        port=rs.port,
        # SSL connection to AWS. So this works for localhost or server:
        connection_class=SSLConnection if rs.scheme == "rediss" else Connection,
    )

    return mqueue


def rt_messages(request: HttpRequest, queue_name: str) -> HttpResponse:
    """Private/internal API response generator.

    Query redis for a named queue, and return the last `count` messages from that queue.
    Messages are deleted from the queue (via .pop()) as they are retrieved.

    Works with any python data structure, but pluto-rt usage assumes messages are stored
    as a list of dicts in the following format:

        {
            "status": "info|success|warning|error",
            "msg": "This is an example"
        }

    The consumer converts that list of dicts to table rows in an htmx template fragment.

    qr3.qr provides a direct interface onto redis queues, and provides the following methods
    common to Python queue data structures:

        mqueue = Queue('foobar')
        mqueue.push(someobj)
        mqueue.clear()
        mqueue.elements()
        mqueue.peek()
        mqueue.pop()
        mqueue.push()

    If the the value of an element on the queue is the string "queue_exhausted"
    this view will return http 286, which tells htmx to stop polling.

    Args:
        queue_name: Required queue name
    Query params:
        count: Optional number of messages to retrieve "per gulp"

    Returns:
        Last `n` messages in the queue, generally as a list of dictionaries, in JSON.
    """

    count = request.GET.get("count")
    count = int(count) if count else 5
    mqueue = get_rt_queue_handle(queue_name)

    items = list()
    for _ in range(count):
        temp_obj = mqueue.pop()

        # If sender tells us the queue is done, return 286
        # which instructs htmx to stop polling
        if temp_obj == "queue_exhausted":
            response = HttpResponse()
            response.status_code = 286
            return response

        if temp_obj:
            items.append(temp_obj)

    return render(request, "pluto_rt/rows.html", {"items": items})
