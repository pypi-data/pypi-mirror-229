def get_url(base_path: str, detail_path: str, resource_id: str = ''):
    """根据给定的路径信息构建一个 URL"""
    url = base_path + detail_path
    if resource_id is not None:
        url += f'/{resource_id}'
    return url
