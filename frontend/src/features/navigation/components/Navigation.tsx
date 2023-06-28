import { Space, Switch, Typography } from "antd";
import { NavLink } from "react-router-dom";
import useSession from "../../../hooks/useSession";
import { SwitchChangeEventHandler } from "antd/es/switch";

const { Text } = Typography;

export default function Navigation() {
  const { session } = useSession();

  async function onIrcSwitch(e: boolean) {
    console.log("====================================");
    console.log(e);
    console.log("====================================");
  }

  return (
    <div style={{ height: 64, backgroundColor: "rgb(21, 34, 50)" }}>
      <div style={{ maxWidth: 1520, marginInline: "auto", padding: "20px 0" }}>
        <div style={{ display: "flex" }}>
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
              {!session.is_admin ? (
                <></>
              ) : (
                <>
                  <NavLink to="/login-form">
                    <Text style={{ color: "white" }} strong>
                      Login
                    </Text>
                  </NavLink>
                  <Switch
                    checkedChildren="IRC ON"
                    unCheckedChildren="IRC OFF"
                    onChange={onIrcSwitch}
                    checked={session.is_irc_running}
                  />
                </>
              )}
            </Space>
          </div>
        </div>
      </div>
    </div>
  );
}
