import { Button, Modal } from "antd";
import { useState } from "react";
import { createRoom } from "../services/roomService";
import { RoomForm, RoomListing } from "../features/rooms";
import useRoomListing from "../hooks/useRoomListing";

export default function RoomPage() {
  const { roomList } = useRoomListing();
  const [isModalOpen, setIsModalOpen] = useState(false);

  function handleModalClose() {
    setIsModalOpen(false);
  }

  function handleModalOpen() {
    setIsModalOpen(true);
  }

  return (
    <div>
      <h1>Room Listing</h1>

      <div style={{ marginBottom: 30 }}>
        <Button type="dashed" size="large" onClick={handleModalOpen}>
          Create New Room
        </Button>
      </div>

      <RoomListing list={roomList ?? []} />

      <Modal
        title="Create Room"
        open={isModalOpen}
        onOk={handleModalClose}
        onCancel={handleModalClose}
        footer={false}
      >
        <RoomForm onFinished={createRoom} />
      </Modal>
    </div>
  );
}
