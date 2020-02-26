from functools import wraps
import threading
import time
import uuid

from flask import Blueprint, abort, current_app, g, request
from werkzeug.exceptions import HTTPException, InternalServerError
from flask.helpers import url_for


tasks_bp = Blueprint('tasks', __name__)
tasks = {}


def async_task(f):
    """
    This decorator transforms a sync route to asynchronous by running it
    in a background thread.
    See: https://github.com/miguelgrinberg/flack/commit/0c372464b341a2df60ef8d93bdca2001009a42b5#diff-af29c7f310450880dcc634c68dbaf433
    """
    @wraps(f)
    def wrapped(*args, **kwargs):
        def task(app, environ, **task_kwargs):
            with app.request_context(environ):
                try:
                    # Pass response_url and context data.
                    tasks[uid]['result'] = f(*args, **kwargs)
                    app.logger.info('Success!')
                except HTTPException as e:
                    app.logger.info('Http Exception')
                    tasks[uid]['result'] = current_app.handle_http_exception(e)
                except Exception as e:
                    print(repr(e))
                    # The function raised an exception, so we set a 500 error
                    tasks[uid]['result'] = InternalServerError()
                    if current_app.debug:
                        # We want to find out if something happened so reraise
                        raise
                finally:
                    # We record the time of the response, to help in garbage
                    # collecting old tasks
                    tasks[uid]['ended_at'] = time.time()

        uid = uuid.uuid4().hex

        task_thread = threading.Thread(
            target=task,
            args=(current_app._get_current_object(), request.environ)
        )
        tasks[uid] = {'task': task_thread}
        tasks[uid]['task'].start()

        return '', 200, {'Location': url_for('tasks.get_status', id=uid)}
    return wrapped


@tasks_bp.route('/status/<id>', methods=['GET'])
def get_status(id):
    """
    Return status about an asynchronous task. If this request returns a 202
    status code, it means that task hasn't finished yet. Else, the response
    from the task is returned.
    """
    current_app.logger.info(tasks)
    task = tasks.get(id)
    if task is None:
        abort(404)
    if 'result' not in task:
        return '', 202, {'Location': url_for('tasks.get_status', id=id)}
    return task['result']