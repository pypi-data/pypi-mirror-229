from barkr.connections.base import ConnectionMode
from barkr.connections.mastodon import MastodonConnection
from barkr.connections.cohost import CohostConnection
from barkr.main import Barkr

h = Barkr(
    [
        MastodonConnection(
            "Mastodon",
            modes=[ConnectionMode.READ, ConnectionMode.WRITE],
            access_token="PGjHSnUb65x8FsHPQ3kxH0gBgbEHQnr77WmeYn0YB_c",
            instance_url="https://tech.lgbt",
        ),
        CohostConnection(
            "Cohost",
            modes=[ConnectionMode.READ, ConnectionMode.WRITE],
            project="testAndresitorresm",
            cookie="s%3AX7LmBkVFBubA7732xv2nSZ-W38dproun.n9wm%2FOOYodvv30FDUapGJjeQh%2FnEwMHC7hAeHhDWitU"
        )
    ]
)
h.start()
