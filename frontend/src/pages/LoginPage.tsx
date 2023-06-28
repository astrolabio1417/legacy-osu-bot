import { Button, Form, Input, Typography } from "antd";
import { login } from "../services/sessionService";
import { useNavigate } from "react-router-dom";
import { useState } from "react";

const { Title } = Typography;

export default function LoginPage() {
  const navigation = useNavigate()
  const [loading, setLoading] = useState<boolean>(false)

  async function onSubmit(data: {"username": string, "password": string}) {
    setLoading(true)
    const isLoggedOn = await login(data.username, data.password)
    setLoading(false)
    if (!isLoggedOn) return
    navigation("/")
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
          <Button loading={loading} type="primary" htmlType="submit">
            Login
          </Button>
        </Form.Item>
      </Form>
    </div>
  );
}
