import { Button, Space, Switch, Typography } from "antd";
import { NavLink } from "react-router-dom";
import useSession from "../../../hooks/useSession";
import { toast } from "react-toastify";
import { API } from "../../../data/constants";
import { logout } from "../../../services/sessionService";
import AppContainer from "../../../components/AppContainer";

const { Text } = Typography;

export default function Navigation() {
  const { session } = useSession();

  async function onIrcSwitch(e: boolean) {
    const ircLink = `${API}/${e ? 'start': 'stop'}`

    const res = await fetch(ircLink, {
      credentials:"include"
    })

    if (res.ok) {
      toast(e? "Irc is ON!" : "Irc is OFF!")
      return
    }

    toast("Something went wrong!", {
      type: "error"
    })
  }

  return (
    <div style={{ backgroundColor: "rgb(21, 34, 50)" }}>
      <AppContainer>
        <div style={{ display: "flex", alignItems: "center", paddingBlock: 20 }}>
          <NavLink to="/">
            <Text style={{ color: "white" }} strong>
              Home
            </Text>
          </NavLink>

          <div
            style={{
              display: "flex",
              justifyContent: "end",
              alignItems: "center",
              flex: 1,
            }}
          >
            <Space size={"large"}>
              <Switch
                checkedChildren="IRC ON"
                unCheckedChildren="IRC OFF"
                onChange={onIrcSwitch}
                disabled={!session.is_admin}
                checked={session.is_irc_running}
              />

              {session.is_admin ? <Button type="text" onClick={logout}>
                <Text style={{color: "white"}} strong>
                  Logout
                </Text>
              </Button> : <NavLink to="/login-form">
                <Text style={{ color: "white" }} strong>
                  Login
                </Text>
              </NavLink>}
            </Space>
          </div>
        </div>
      </AppContainer>
    </div>
  );
}
