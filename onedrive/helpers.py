import onedrivesdk
from onedrivesdk.helpers import GetAuthCodeServer

Item = onedrivesdk.Item
Client = onedrivesdk.OneDriveClient
Collection = onedrivesdk.ChildrenCollectionPage


def connect(client_id: str, client_secret: str, redirect_url: str = 'http://localhost:8080') -> Client:
    '''
    Get the authenticated client
    '''
    scopes = ['wl.signin', 'wl.offline_access', 'onedrive.readwrite']
    client = onedrivesdk.get_default_client(
        client_id=client_id, scopes=scopes)
    print(client)
    auth_url = client.auth_provider.get_auth_url(redirect_url)
    code = GetAuthCodeServer.get_auth_code(auth_url, redirect_url)
    client.auth_provider.authenticate(code, redirect_url, client_secret)
    return client


def get_by_name(name: str, collection: Collection):
    found = list(filter(lambda x: x.name == name, collection))
    if len(found) == 0:
        raise Exception("item not found")
    return found[0]


def ls(collection: Collection):
    for each in collection:
        print('name:', each.name, 'id:', each.id)


def is_dir(item: Item):
    return item.folder is not None


async def children(item_id: Item.id, client: Client):
    MAX = 1_000  # test to be the maximum number
    return await client.item(drive='me', id=item_id).children.request(top=MAX).get_async()


async def cd_to(dir: str, cur_collect: Collection, client: Client):
    print('cd to {}'.format(dir))
    if dir is '/':
        return await children('root', client)
    return await children(get_by_name(dir, cur_collect).id, client)


async def cd(path: str, client: Client):
    tokens = path.split('/')
    collec = None
    paths, last = tokens[:-1], tokens[-1]
    for token in paths:
        if token is '':
            collec = await cd_to('/', collec, client)
        else:
            collec = await cd_to(token, collec, client)
    return await children(get_by_name(last, collec).id, client)
