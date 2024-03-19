export const request = {
  post: (url: string, data: any) => {
    const token = localStorage.getItem("accessToken");
    const headers = new Headers({
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    });
    return fetch(url, {
      method: "POST",
      headers,
      body: JSON.stringify(data),
    });
  },
  get: (
    url: string,
    query?: string | Record<string, string> | URLSearchParams | string[][] | undefined
  ) => {
    let newUrl = url;
    const token = localStorage.getItem("accessToken");
    const headers = new Headers({
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    });
    if (query) {
      const queryString = new URLSearchParams(query).toString();
      newUrl = `${url}?${queryString}`;
    }
    return fetch(newUrl, {
      method: "GET",
      headers,
    });
  },
};

export const saveConfig = (config: any) => {
  return request.post("/api/plugins/notifyapi/save_config", config);
};

export const getConfig = () => {
  return request.get("/api/plugins/notifyapi/get_config");
};

export const delConfig = (id: string) => {
  return request.get("/api/plugins/notifyapi/del_config", { id });
}

export const get_user = () => {
  return request.get("/api/plugins/notifyapi/get_user");
};

export const get_channel = () => {
  return request.get("/api/plugins/notifyapi/get_notify_channel");
};

export const testSendNotify = (data: any) => {
  return request.post("/api/plugins/notifyapi/send_notify", data);
}
