import * as Dialog from "@radix-ui/react-dialog";
import * as Form from "@radix-ui/react-form";
import { ReactNode, useEffect, useState } from "react";
import { INotifyChannel } from "../types";
import { get_user, get_channel } from "../request";

export const EditNotifyConfig = (props: {
  notifyapi: INotifyChannel;
  trigger: ReactNode;
  onSave: (notifyapi: INotifyChannel) => Promise<void>;
}) => {
  const [open, setOpen] = useState(false);
  const [users, setUsers] = useState<{ name: string; value: number }[]>([]);
  const [channels, setChannels] = useState<{ name: string; value: string }[]>([]);

  const [checkedUsers, setCheckedUsers] = useState<number[]>(props.notifyapi.users);
  const [checkedChannels, setCheckedChannels] = useState<string[]>(props.notifyapi.channels);

  const [isUserError, setIsUserError] = useState(false);
  const [isChannelError, setIsChannelError] = useState(false);

  useEffect(() => {
    if (open) {
      get_user()
        .then((res) => res.json())
        .then((res) => {
          if (res.errorCode === 0 && res.data) {
            const users = res.data;
            setUsers(users);
          }
        });
      get_channel()
        .then((res) => res.json())
        .then((res) => {
          if (res.errorCode === 0 && res.data) {
            const channels = res.data;
            setChannels(channels);
          }
        });
    }
  }, [open]);

  return (
    <Dialog.Root modal open={open} onOpenChange={setOpen}>
      <Dialog.Trigger asChild>{props.trigger}</Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Overlay className="animate-fade animate-duration-300">
          <div className="bg-gray-950 fixed inset-0 opacity-60" />
        </Dialog.Overlay>
        <Dialog.Content className="card md:w-2/3 max-w-[800px] w-[calc(100vw-2em)] fixed rounded-lg top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 flex-shrink-0 shadow-2xl bg-base-100">
          <div className="card-body">
            <Dialog.Title>
              <div className="card-title text-center">
                {props.notifyapi.id ? "编辑 推送配置" : "添加 推送配置"}
              </div>
            </Dialog.Title>

            <Dialog.Close />
            <Form.Root
              onSubmit={(e) => {
                e.preventDefault();
                const form = e.currentTarget;
                const formData = new FormData(form);
                const notifyapi: INotifyChannel = {
                  id: props.notifyapi.id,
                  name: formData.get("name") as string,
                  users: checkedUsers,
                  channels: checkedChannels,
                  default_img: formData.get("default_img") as string,
                };
                let hasError = false;
                if (checkedUsers.length === 0) {
                  setIsUserError(true);
                  hasError = true;
                } else {
                  setIsUserError(false);
                }
                if (checkedChannels.length === 0) {
                  setIsChannelError(true);
                  hasError = true;
                } else {
                  setIsChannelError(false);
                }
                if (!hasError){
                  props.onSave(notifyapi);
                  form.reset();
                  setOpen(false);
                }
              }}
            >
              <Form.Field name="name" className="form-control">
                <Form.Label className="label">名称：</Form.Label>
                <Form.ValidityState>
                  {(validity) => (
                    <>
                      <Form.Control asChild>
                        <input
                          type="text"
                          placeholder="名称"
                          defaultValue={props.notifyapi.name}
                          className={
                            "input input-sm md:input-md input-bordered" +
                            (validity?.valueMissing ? " input-error" : "")
                          }
                          required // 确保字段是必填的
                        />
                      </Form.Control>
                      <label className="label">
                        {(() => {
                          if (validity?.valueMissing) {
                            return (
                              <label className="label-text-alt text-error">名称是必须的。</label>
                            );
                          } else {
                            return (
                              <label className="label-text-alt">
                                用于显示的友好名称。
                              </label>
                            );
                          }
                        })()}
                      </label>
                    </>
                  )}
                </Form.ValidityState>
              </Form.Field>
              <div className="my-2">
                <div>推送用户：</div>
                <div className="max-h-[20vh] overflow-y-auto">
                  <div className="grid grid-cols-4">
                    {users.map((user) => {
                      return (
                        <label
                          key={user.name}
                          className="cursor-pointer p-0 m-2 label mr-4 justify-start"
                        >
                          <input
                            checked={checkedUsers.includes(user.value)}
                            type="checkbox"
                            name="bindUsers"
                            className="checkbox-sm md:checkbox-md checkbox mr-2"
                            onChange={(e) => {
                              const checked = e.target.checked;
                              if (checked) {
                                if (!checkedUsers.includes(user.value)) {
                                  setCheckedUsers([...checkedUsers, user.value]);
                                }
                              } else {
                                setCheckedUsers(checkedUsers.filter((i) => i !== user.value));
                              }
                            }}
                          />
                          <span className="label-text text-xs md:text-sm">{user.name}</span>
                        </label>
                      );
                    })}
                  </div>
                </div>
                {isUserError && <label className="label-text-alt text-error">至少需要选择一个推送用户。</label>}
              </div>
              <div className="my-2">
                <div>推送通道：</div>
                <div className="max-h-[20vh] overflow-y-auto">
                  <div className="grid grid-cols-4">
                    {channels.map((channel) => {
                      return (
                        <label
                          key={channel.name}
                          className="cursor-pointer p-0 m-2 label mr-4 justify-start"
                        >
                          <input
                            checked={checkedChannels.includes(channel.value)}
                            type="checkbox"
                            name="bintChannels"
                            className="checkbox-sm md:checkbox-md checkbox mr-2"
                            onChange={(e) => {
                              const checked = e.target.checked;
                              if (checked) {
                                if (!checkedChannels.includes(channel.value)) {
                                  setCheckedChannels([...checkedChannels, channel.value]);
                                }
                              } else {
                                setCheckedChannels(
                                  checkedChannels.filter((i) => i !== channel.value)
                                );
                              }
                            }}
                          />
                          <span className="label-text text-xs md:text-sm">{channel.name}</span>
                        </label>
                      );
                    })}
                  </div>
                </div>
                {isChannelError && <label className="label-text-alt text-error">至少需要选择一个推送通道。</label>}
              </div>
              <Form.Field name="default_img" className="form-control">
                <Form.Label className="label">推送图片：</Form.Label>
                <Form.ValidityState>
                  {() => (
                    <>
                      <Form.Control asChild>
                        <input
                          type="text"
                          placeholder="https://example.com/image.png"
                          defaultValue={props.notifyapi.default_img}
                          className={
                            "input input-sm md:input-md input-bordered"
                          }
                        />
                      </Form.Control>
                      <label className="label">
                        <label className="label-text-alt">
                          此渠道推送默认图片，外部调用时可覆盖。
                        </label>
                      </label>
                    </>
                  )}
                </Form.ValidityState>
              </Form.Field>
              <Form.Submit asChild>
                <button className="bg-buttomBackgroundColor hover:bg-buttomHoverBackgroundColor mt-6 w-full btn btn-primary">保存</button>
              </Form.Submit>
            </Form.Root>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
};
