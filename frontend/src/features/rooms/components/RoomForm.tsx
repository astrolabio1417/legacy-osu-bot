import {
  Button,
  Checkbox,
  Divider,
  Form,
  Input,
  InputNumber,
  Select,
  Slider,
} from "antd";
import useEnums from "../../../hooks/useEnums";
import { IRoomForm } from "../../../types/roomFormInterface";
import { useState } from "react";

interface RoomFormProps {
  initialValues?: IRoomForm;
  onFinished?: (values: IRoomForm) => Promise<boolean>;
  resetOnSubmit?: boolean;
}

export default function RoomForm(props: RoomFormProps) {
  const { enums } = useEnums();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState<boolean>(false)

  const defaultInitialValues: IRoomForm = {
    name: "",
    room_size: 16,
    bot_mode: "AUTO_HOST",
    play_mode: "OSU",
    team_mode: "HEAD_TO_HEAD",
    score_mode: "SCORE",
    beatmap: {
      star: [0, 10],
      cs: [0, 10],
      ar: [0, 10],
      bpm: [0, 200],
      length: [60, 180],
      rank_status: ["RANKED", "APPROVED", "QUALIFIED", "LOVED"],
      force_stat: false,
    },
  };

  async function onFinish(values: IRoomForm) {
    setLoading(true)
    const ok = await props.onFinished?.(values);
    setLoading(false)
    ok && props.resetOnSubmit && form.resetFields();
  }

  return (
    <div>
      <Form
        form={form}
        style={{ maxWidth: 900, margin: "auto" }}
        onFinish={onFinish}
        initialValues={props.initialValues ?? defaultInitialValues}
      >
        <div style={{ paddingBottom: 15 }}>
          <Divider orientation="left">Room Settings</Divider>
        </div>
        <Form.Item
          label="Name"
          name="name"
          rules={[
            { required: true, message: "Please input the name of the room." },
            { max: 50, message: "50 max character." },
          ]}
        >
          <Input />
        </Form.Item>

        <Form.Item label="Password" name="password">
          <Input.Password />
        </Form.Item>

        <Form.Item label="Room size" name="room_size">
          <InputNumber min={1} max={16} />
        </Form.Item>

        <Form.Item label="Bot Mode" name="bot_mode">
          <Select>
            {enums?.BOT_MODE?.map((bot) => (
              <Select.Option key={bot} value={bot}>
                {bot.replaceAll("_", " ")}
              </Select.Option>
            ))}
          </Select>
        </Form.Item>

        <Form.Item label="Play Mode" name="play_mode">
          <Select>
            {enums?.PLAY_MODE?.map((bot) => (
              <Select.Option key={bot} value={bot}>
                {bot.replaceAll("_", " ")}
              </Select.Option>
            ))}
          </Select>
        </Form.Item>

        <Form.Item label="Score Mode" name="score_mode">
          <Select>
            {enums?.SCORE_MODE?.map((bot) => (
              <Select.Option key={bot} value={bot}>
                {bot.replaceAll("_", " ")}
              </Select.Option>
            ))}
          </Select>
        </Form.Item>

        <Form.Item label="Team Mode" name="team_mode">
          <Select>
            {enums?.TEAM_MODE?.map((bot) => (
              <Select.Option key={bot} value={bot}>
                {bot.replaceAll("_", " ")}
              </Select.Option>
            ))}
          </Select>
        </Form.Item>

        <div style={{ paddingBottom: 15, paddingTop: 30 }}>
          <Divider orientation="left">Beatmap Settings</Divider>
        </div>

        <Form.Item label="Rank Status" name={["beatmap", "rank_status"]}>
          <Select mode="multiple">
            {enums?.RANK_STATUS?.map((rank) => (
              <Select.Option key={rank} value={rank}>
                {rank.replaceAll("_", " ")}
              </Select.Option>
            ))}
          </Select>
        </Form.Item>

        <Form.Item label="Star Rating" name={["beatmap", "star"]}>
          <Slider
            range
            min={0.0}
            max={10.0}
            step={0.1}
            marks={{
              0: 0,
              10: 10,
            }}
          />
        </Form.Item>
        <Form.Item label="Circle Size" name={["beatmap", "cs"]}>
          <Slider
            range
            min={0.0}
            max={10.0}
            step={0.1}
            marks={{
              0: 0,
              10: 10,
            }}
          />
        </Form.Item>
        <Form.Item label="Approach Rate" name={["beatmap", "ar"]}>
          <Slider
            range
            min={0.0}
            max={10.0}
            step={0.1}
            marks={{
              0: 0,
              10: 10,
            }}
          />
        </Form.Item>
        <Form.Item label="Length (in seconds)" name={["beatmap", "length"]}>
          <Slider
            range
            min={0}
            max={1800}
            marks={{
              0: "0m",
              1800: "30m",
            }}
          />
        </Form.Item>

        <Form.Item label="Beats Per Minute" name={["beatmap", "bpm"]}>
          <Slider
            range
            min={0}
            max={300}
            marks={{
              0: 0,
              300: 300,
            }}
          />
        </Form.Item>

        <Form.Item name={["beatmap", "force_stat"]} valuePropName="checked">
          <Checkbox>Force to use Beatmap Settings</Checkbox>
        </Form.Item>

        <Form.Item>
          <Button type="primary" htmlType="submit" loading={loading}>
            Submit
          </Button>
        </Form.Item>
      </Form>
    </div>
  );
}
