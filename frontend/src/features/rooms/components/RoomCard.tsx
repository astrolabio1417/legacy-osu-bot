import { Button, Card, List, Modal, Space } from "antd";
import { IRoom, IRoomForm } from "../../../types/roomInterface";
import { deleteRoom, updateRoom } from "../../../services/roomService";
import { useState } from "react";
import RoomForm from "./RoomForm";

export default function RoomCard(props: IRoom) {
  const room = props ?? {};
  const {
    name,
    bot_mode,
    play_mode,
    room_size,
    score_mode,
    team_mode,
    is_created,
    room_id,
    users,
    is_connected,
    id,
    beatmap,
  } = room ?? {};
  const [showModal, setShowModal] = useState(false);
  const [loading, setLoading] = useState(false);

  async function onDelete(id: string) {
    setLoading(true);
    await deleteRoom(id);
    setLoading(false);
  }

  return (
    <List.Item>
      <Card title={<>{name}</>}>
        <div style={{ display: "flex", flexDirection: "column" }}>
          <span
            style={{
              color: is_connected ? "green" : "red",
            }}
          >
            <b>{is_connected ? "Connected" : "Not Connected"}</b>
          </span>
          <span>
            <b>ID:</b> {id}
          </span>
          <span>
            <b>Room ID:</b> {room_id}
          </span>
          <span>
            <b>Bot:</b> {bot_mode}
          </span>
          <span>
            <b>Play:</b> {play_mode}
          </span>
          <span>
            <b>Score:</b> {score_mode}
          </span>
          <span>
            <b>Team:</b> {team_mode}
          </span>
          <span>
            <b>Size:</b> {room_size}
          </span>
          <span>
            <b>Genre:</b> {beatmap.genre}
          </span>
          <span>
            <b>Language:</b> {beatmap.language}
          </span>
          <span>
            <b>Rank Status:</b> {beatmap.rank_status}
          </span>
          <span>
            <b>Star: </b> {beatmap.star[0]} - {beatmap.star[1]}
          </span>
          <span>
            <b>bpm: </b> {beatmap.bpm[0]} - {beatmap.bpm[1]}
          </span>
          <span>
            <b>cs: </b> {beatmap.cs[0]} - {beatmap.cs[1]}
          </span>
          <span>
            <b>length: </b> {beatmap.length[0]} - {beatmap.length[1]}
          </span>
          <span>
            <b>Users:</b> {users.length ? users?.join(", ") : "..."}
          </span>
          <span>
            <b>Skip Votes: </b>{" "}
            {props.skips.length ? props.skips?.join(", ") : "..."}
          </span>

          <Space wrap style={{ marginTop: 15 }}>
            <Button
              type="default"
              disabled={!is_connected || !is_created}
              onClick={() => {
                setShowModal(true);
              }}
            >
              Update
            </Button>
            <Button
              type="primary"
              danger
              disabled={!is_connected || !is_created}
              loading={loading}
              onClick={() => onDelete(id)}
            >
              Delete
            </Button>
          </Space>
        </div>
      </Card>
      <Modal
        title={`Update Room #${id}`}
        open={showModal}
        onOk={() => setShowModal(false)}
        onCancel={() => setShowModal(false)}
        footer={false}
      >
        <RoomForm
          onFinished={async (values: IRoomForm) => await updateRoom(values, id)}
          initialValues={room}
        />
      </Modal>
    </List.Item>
  );
}
