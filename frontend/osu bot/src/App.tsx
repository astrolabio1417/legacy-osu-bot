import { ConfigProvider } from "antd";
import Home from "./container/RoomContainer";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import "./app.css";

function App() {
  return (
    <ConfigProvider
      theme={{
        token: {
          fontFamily:
            "-apple-system,BlinkMacSystemFont,'Oxygen','Segoe UI',Roboto,'Helvetica Neue',Arial,'Noto Sans',sans-serif,'Apple Color Emoji','Segoe UI Emoji','Segoe UI Symbol','Noto Color Emoji'",
        },
      }}
    >
      <div style={{ marginLeft: 10, marginRight: 10 }}>
        <Home />
        <ToastContainer
          position="bottom-center"
          autoClose={5000}
          hideProgressBar={false}
          newestOnTop={false}
          closeOnClick
          rtl={false}
          pauseOnFocusLoss
          draggable
          pauseOnHover
          theme="light"
        />
      </div>
    </ConfigProvider>
  );
}

export default App;
