from rtorrent.rpc import RPCObject
from rtorrent.rpc.method import check_success
from rtorrent.rpc.caller import RPCCaller
from rtorrent.rpc import BaseMulticallBuilder
import rtorrent.file

from rtorrent.rpc.processors import *

class Torrent(RPCObject):
    def __init__(self, context, info_hash):
        super(Torrent, self).__init__(context)
        self.info_hash = info_hash

    def rpc_call(self, key, *args):
        call = super().rpc_call(key, *args)
        # inject required info_hash argument as first argument
        call.get_args().insert(0, self.info_hash)
        return call

    def get_file_metadata(self):
        builder = rtorrent.file.FileMulticallBuilder(self.context, self)

        for key, rpc_method in rtorrent.file.File.get_rpc_methods().items():
            if rpc_method.is_retriever():
                getattr(builder, key)()

        return builder.call()

    def __str__(self):
        return "Torrent(info_hash={0})".format(self.info_hash)


class TorrentMulticallBuilder(BaseMulticallBuilder):
    def __init__(self, context, view):
        super(TorrentMulticallBuilder, self).__init__(context)
        if view is None:
            view = 'main'
        self.keys.insert(0, 'get_info_hash')
        self.args.insert(0, [view])
        self.multicall_rpc_method = 'd.multicall'
        self.rpc_object_class = Torrent
        self.metadata_cls = TorrentMetadata


class TorrentMetadata(object):
    def __init__(self, results):
        self.results = results

    def __getattr__(self, item):
        return lambda: self.results[item]


_VALID_TORRENT_PRIORITIES = ['off', 'low', 'normal', 'high']

Torrent.register_rpc_method('get_info_hash', 'd.get_hash')
Torrent.register_rpc_method('get_name', 'd.get_name')
Torrent.register_rpc_method('get_completed_bytes', 'd.get_completed_bytes')
Torrent.register_rpc_method('get_size_bytes', 'd.get_size_bytes')
Torrent.register_rpc_method('get_state', 'd.get_state')
Torrent.register_rpc_method('get_complete', 'd.get_complete')
Torrent.register_rpc_method('load_start', 't.load_start')
Torrent.register_rpc_method("set_priority", "d.set_priority",
                            pre_processors=[valmap(_VALID_TORRENT_PRIORITIES,
                                                   range(0, 4), 1)],
                            post_processors=[check_success])
Torrent.register_rpc_method("get_priority", "d.get_priority",
                            post_processors=[lambda x:
                                             _VALID_TORRENT_PRIORITIES[x]])
Torrent.register_rpc_method("is_accepting_seeders", "d.accepting_seeders",
                            boolean=True)
Torrent.register_rpc_method('get_upload_rate',
                            ['d.up.rate', 'd.get_up_rate'])
Torrent.register_rpc_method('get_download_rate',
                            ['d.down.rate', 'd.get_down_rate'])
Torrent.register_rpc_method('get_skip_rate',
                            ['d.skip.rate', 'd.get_skip_rate'])
Torrent.register_rpc_method('get_upload_total',
                            ['d.up.total', 'd.get_up_total'])
Torrent.register_rpc_method('get_download_total',
                            ['d.down.total', 'd.get_down_total'])
Torrent.register_rpc_method('get_skip_total',
                            ['d.skip.total', 'd.get_skip_total'])
Torrent.register_rpc_method('get_timestamp_started', 'd.timestamp.started',
                            post_processors=[to_datetime])
Torrent.register_rpc_method('get_timestamp_finished', 'd.timestamp.finished',
                            post_processors=[to_datetime])
Torrent.register_rpc_method('get_size_bytes',
                            ['d.size_bytes', 'd.get_size_bytes'])
Torrent.register_rpc_method('get_size_chunkss',
                            ['d.size_chunks', 'd.get_size_chunks'])
Torrent.register_rpc_method('get_size_files',
                            ['d.size_files', 'd.get_size_files'])
Torrent.register_rpc_method('get_size_pex',
                            ['d.size_pex', 'd.get_size_pex'])
Torrent.register_rpc_method('get_chunk_size',
                            ['d.chunk_size', 'd.get_chunk_size'])
