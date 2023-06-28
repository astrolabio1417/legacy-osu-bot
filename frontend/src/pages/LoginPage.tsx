import { Button, Form, Input, Typography } from "antd";
import { API } from "../data/constants";
import { toast } from "react-toastify";

const { Title } = Typography;

export default function LoginPage() {

  async function onSubmit(data: {"username": string, "password": string}) {
    const res = await fetch(`${API}/auth`, {
      method: "post",
      body: JSON.stringify(data),
      credentials: "include",
      headers: {
        "accept": "application/json",
        "content-type": "application/json"
      }
    })
    const jsonRes = await res.json();
    const {message} = jsonRes ?? {};

    if (res.ok) {
      toast("Login Success");
      return
    }
    
    toast(message ?? "Login Failed", {
      type: "error"
    })
  }

  return (
    <div>
      <Title level={2}>Login Form</Title>
      <Form onFinish={onSubmit}>
        <Form.Item label="username" name="username">
          <Input />
        </Form.Item>
        <Form.Item label="password" name="password">
          <Input.Password />
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit">
            Login
          </Button>
        </Form.Item>
      </Form>
    </div>
  );
}
