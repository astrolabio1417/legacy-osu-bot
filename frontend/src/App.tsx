import { ConfigProvider} from "antd";
import RoomPage from "./pages/RoomPage";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import "./app.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import LoginPage from "./pages/LoginPage";
import Navigation from "./features/navigation/components/Navigation";
import AppContainer from "./components/AppContainer";


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
      <BrowserRouter>
        <Navigation />
        <AppContainer>
          <Routes>
            <Route path="/" element={<RoomPage />}  />
            <Route path="/login-form" element={<LoginPage />} />
          </Routes>
        </AppContainer>

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
      </BrowserRouter>
    </ConfigProvider>
  );
}

export default App;
