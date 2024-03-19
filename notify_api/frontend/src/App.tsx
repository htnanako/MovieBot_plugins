import "./App.css";
import { Icon } from "@iconify/react";
import { useEffect, useState } from "react";
import DeleteButton from "./components/DeleteButton";
import { EditNotifyConfig } from "./components/EditNotifyConfig";
import { INotifyChannel } from "./types";
import { getConfig, saveConfig, delConfig, get_channel, get_user, testSendNotify } from "./request";


function App() {
  const [notifyapis, setNotifyapis] = useState<INotifyChannel[]>([]);
  const [allusers, setUsers] = useState<any[]>([]);
  const [allchannels, setChannels] = useState<any[]>([]);

  // 获取通知渠道列表
  const fetchNotifyChannels = async () => {
    const res = await get_channel().then((res) => res.json());
    if (res.errorCode === 0 && res.data) {
      const allchannels = res.data;
      setChannels(allchannels);
    }
  }
  // 获取用户列表
  const fetchUsers = async () => {
    const res = await get_user().then((res) => res.json());
    if (res.errorCode === 0 && res.data) {
      const allusers = res.data;
      setUsers(allusers);
    }
  }

  const fetchNotifyapis = async () => {
    const res = await getConfig().then((res) => res.json());
    if (res.errorCode === 0 && res.data) {
      const notifyapis = res.data;
      notifyapis.sort((a: INotifyChannel, b: INotifyChannel) => {
        return a.id! - b.id!;
      });
      setNotifyapis(notifyapis);
    }
  };

  useEffect(() => {
    fetchNotifyapis();
    fetchUsers();
    fetchNotifyChannels();
  }, []);

  const relodNotifyapis = () => {
    fetchNotifyapis();
  };

  const saveNotifyapi = (notifyapi: INotifyChannel) => {
    return saveConfig(notifyapi);
  };

  const deleteNotifyapi = (id: number) => {
    return delConfig(id.toString());
  };

  return (
    <div className="px-2 md:px-4 pb-4 space-y-4">
      <div className="mb-1 text-2xl font-semibold leading-tight">通知调度中心</div>
      {/* 列表 */}
      {notifyapis.length === 0 && (
        // empty
        <div className="rounded-2xl shadow-2xl bg-base-100 p-4 flex flex-col justify-between">
          <div className="text-lg text-center font-bold">这里什么都还没有呢....</div>
        </div>
      )}
      {notifyapis.map((notifyapi) => {
        return (
          <div
            key={notifyapi.id}
            className="rounded-2xl shadow-2xl bg-base-100 p-4 flex flex-col justify-between"
          >
            <div className="space-y-1">
              <div className="text-lg font-bold">名称: {notifyapi.name}</div>
              <div className="opacity-90 text-sm truncate">ID: {notifyapi.id}</div>
              <div className="opacity-90 text-sm truncate">推送用户: {notifyapi.users.map((userId) => {
                  const userObj = allusers.find((u) => u.value === userId);
                  return userObj ? userObj.name : "";
                }).join(", ")}
              </div>
              <div className="opacity-90 text-sm truncate">推送通道: {notifyapi.channels.map((channelId) => {
                  const channelObj = allchannels.find((c) => c.value === channelId);
                  return channelObj ? channelObj.name : "";
                }).join(", ")}
              </div>
              <div className="opacity-90 text-sm truncate">推送图片: {notifyapi.default_img || '无'}</div>
            </div>
            <div className="flex items-center space-x-2 mt-2">
              <div
                className="btn btn-sm btn-circle"
                title="发送测试"
                onClick={async () => {
                  try {
                    const res = await testSendNotify({
                      id: notifyapi.id,
                      title: "这是一个测试标题",
                      content: "这是一条测试内容",
                    });
                    const resJson = await res.json();
                    if (res.status === 200) {
                      alert('通知发送成功！');
                    } else {
                      alert('通知发送失败: ' + resJson.message);
                    }
                  } catch (error) {
                    alert('通知发送出错: ' + error);
                  }
                }
                }
              >
                <Icon icon="material-symbols:send" className="w-5 h-5" />
              </div>
              <EditNotifyConfig
                trigger={
                  <div className="btn btn-sm btn-circle" title="编辑">
                    <Icon icon="material-symbols:edit" className="w-5 h-5" />
                  </div>
                }
                notifyapi={notifyapi}
                onSave={async (notifyapi: INotifyChannel) => {
                  await saveNotifyapi(notifyapi);
                  relodNotifyapis();
                }}
              />
              <DeleteButton
                onDelete={async () => {
                  await deleteNotifyapi(notifyapi.id!);
                  relodNotifyapis();
                }}
              >
                <div className="btn btn-sm btn-circle" title="删除">
                  <Icon icon="material-symbols:delete" className="w-5 h-5" />
                </div>
              </DeleteButton>
              <div
                className="btn btn-sm btn-circle"
                title="复制接口信息，仅在https访问时可用。"
                onClick={async () => {
                  const currentUrl = window.location.origin;
                  const copyText = currentUrl + "/api/plugins/notifyapi/send_notify?id=" + notifyapi.id + "&title={title}&content={content}&pic_url={pic_url}&link_url={link_url}&access_key={access_key}";
                  try {
                    await navigator.clipboard.writeText(copyText);
                    alert('接口信息已复制到剪贴板！');
                  } catch (err) {
                    alert('复制接口信息失败, 请确保你使用https访问本页面！\n请手动复制。\n' + copyText);
                  }
                }
                }
              >
                <Icon icon="material-symbols:content-copy" className="w-5 h-5" />
              </div>
            </div>
          </div>
        );
      })}
      {/* 添加按钮 */}
      <div className="flex">
        <EditNotifyConfig
          trigger={<button className="bg-buttomBackgroundColor hover:bg-buttomHoverBackgroundColor btn btn-primary flex-1">添加</button>}
          notifyapi={{ name: "", users: [], channels: [], default_img: "" }}
          onSave={async (notifyapi: INotifyChannel) => {
            await saveNotifyapi(notifyapi);
            relodNotifyapis();
          }}
        />
      </div>
    </div>
  );
}

export default App;
