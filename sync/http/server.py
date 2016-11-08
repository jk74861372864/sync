import falcon

import sync

from sync.http import controllers
from sync.storage import init_storage


_HEADER_X_SYNC_ID = 'X-Sync-Id'


def raise_http_not_found(ex, req, resp, params):
    raise falcon.HTTPNotFound()


class SyncMiddleware(object):

    def process_request(self, req, resp):
        system_id = req.get_header(_HEADER_X_SYNC_ID)

        # The only method/path that doesn't require an X-Sync-Id
        # header.
        if req.method == 'POST' and req.path == '/':
            if system_id is not None:
                raise falcon.HTTPInvalidHeader(
                    'Unexpected header present', _HEADER_X_SYNC_ID)
            return

        if system_id is None:
            raise falcon.HTTPMissingHeader(_HEADER_X_SYNC_ID)

        init_storage(system_id, create_db=False)


api = falcon.API(middleware=[
    SyncMiddleware()])

api.add_route('/', controllers.System())
api.add_route('/node', controllers.NodeList())
api.add_route('/node/{node_id}', controllers.Node())
api.add_route('/node/{node_id}/send', controllers.NodeSend())
api.add_route('/node/{node_id}/fetch', controllers.NodeFetch())
api.add_route('/node/{node_id}/ack', controllers.NodeAck())
api.add_route('/node/{node_id}/fail', controllers.NodeFail())
api.add_route('/node/{node_id}/sync', controllers.NodeFail())

api.add_error_handler(
    sync.exceptions.DatabaseNotFoundError,
    raise_http_not_found)