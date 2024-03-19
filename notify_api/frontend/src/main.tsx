import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.tsx";
import dayjs from "dayjs";
import "dayjs/locale/zh-cn";
import duration from "dayjs/plugin/duration";
import relativeTime from "dayjs/plugin/relativeTime";

import "./index.css";

const changeTheme = () => {
  const mrTheme = (window as any).mrTheme?.name;
  const THEMES: {
    [key: string]: string;
  } = {
    DEFAULT: "light",
    DARK: "dark",
    LIGHT: "light",
    BLUE: "light",
    GREEN: "light",
    INDIGO: "light",
    DEEP_DARK: "dark",
  };

  if (mrTheme) {
    document.documentElement.setAttribute("data-theme", THEMES[mrTheme]);
  } else {
    document.documentElement.setAttribute("data-theme", "dark");
  }
};

changeTheme();

// 监听postMessage
window.addEventListener("message", (event) => {
  if (event.data === "injectTheme") {
    changeTheme();
  }
});

dayjs.locale("zh-cn"); // 全局使用
dayjs.extend(duration);
dayjs.extend(relativeTime);
ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
