import * as AlertDialog from "@radix-ui/react-alert-dialog";
import { ReactNode } from "react";

interface IDeleteButtonProps {
  onDelete: () => void;
  children: ReactNode;
}

const DeleteButton: React.FC<IDeleteButtonProps> = ({ onDelete, children }) => {
  const handleDelete = () => {
    onDelete();
  };

  return (
    <AlertDialog.Root>
      <AlertDialog.Trigger asChild>{children}</AlertDialog.Trigger>
      <AlertDialog.Portal>
        <AlertDialog.Overlay className="animate-fade animate-duration-300">
          <div className="bg-gray-950 fixed inset-0 opacity-60" />
        </AlertDialog.Overlay>
        <AlertDialog.Content className="card md:w-2/3 max-w-[450px] w-[calc(100vw-2em)] fixed rounded-lg top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 flex-shrink-0 shadow-2xl bg-base-100">
          <div className="card-body">
            <AlertDialog.Title>
              <h3 className="text-lg font-semibold">确认删除？</h3>
            </AlertDialog.Title>
            <AlertDialog.Description>
              <p className="text-sm">此操作不可逆，请确认！</p>
            </AlertDialog.Description>
            <div className="flex items-center justify-end space-x-2 mt-4">
              <AlertDialog.Cancel asChild>
                <button className="btn btn-sm md:btn-md btn-ghost">取消</button>
              </AlertDialog.Cancel>
              <AlertDialog.Action asChild>
                <button className="btn btn-sm md:btn-md btn-error" onClick={handleDelete}>
                  确认删除
                </button>
              </AlertDialog.Action>
            </div>
          </div>
        </AlertDialog.Content>
      </AlertDialog.Portal>
    </AlertDialog.Root>
  );
};

export default DeleteButton;
