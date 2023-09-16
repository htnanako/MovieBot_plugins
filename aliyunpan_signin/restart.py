import requests

def restart_docker(portainer_url, access_token, env='2',container_name="xiaoya"):
    """
    使用Portainer的API重启Docker容器。
    
    参数:
    - portainer_url: Portainer API的基础URL。
    - access_token: Portainer的Access token。
    - container_name: 需要重启的Docker容器的名称。
    
    返回:
    - 表示成功或失败的消息。
    """
    
    # 使用Access token设置头部信息，不带"Bearer"前缀
    headers = {
        "X-Api-Key": access_token
    }

    # 1. 使用令牌获取所有容器的列表
    containers = requests.get(f"{portainer_url}/api/endpoints/{env}/docker/containers/json?all=true", headers=headers).json()

    # 2. 查找容器并重启
    for container in containers:
        if container_name in container['Names'][0]:
            container_id = container['Id']
            restart_response = requests.post(f"{portainer_url}/api/endpoints/{env}/docker/containers/{container_id}/restart", headers=headers)
            
            if restart_response.status_code == 204:
                return f"容器「{container_name}」成功重启!"
            else:
                return f"容器「{container_name}」重启失败!"
    return f"未找到容器「{container_name}」"

