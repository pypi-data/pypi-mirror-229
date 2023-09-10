from barkr.connections.mastodon import ConnectionMode, MastodonConnection
from barkr.main import Barkr

h = Barkr(
    [
        MastodonConnection(
            "Mastodon",
            modes=[ConnectionMode.READ, ConnectionMode.WRITE],
            access_token="PGjHSnUb65x8FsHPQ3kxH0gBgbEHQnr77WmeYn0YB_c",
            instance_url="https://tech.lgbt",
        )
    ]
)
h.start()
