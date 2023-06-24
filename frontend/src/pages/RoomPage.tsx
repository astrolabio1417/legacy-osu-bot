import { Button, Divider, Modal } from "antd";
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
      <Divider orientation="left">
        <h2>Room Listing</h2>
      </Divider>

      <div style={{ marginBottom: 30 }}>
        <Button type="dashed" size="large" onClick={handleModalOpen}>
          Create New Room
        </Button>
      </div>

      <RoomListing list={roomList ?? []} />

      <Modal
        title="Basic Modal"
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
