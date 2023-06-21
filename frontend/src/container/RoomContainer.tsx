import { Button, Divider, Modal } from "antd";
import RoomForm from "../components/RoomForm";
import RoomListing from "../components/RoomListing";
import useRoomListing from "../hooks/useRoomListing";
import { useState } from "react";
import { createRoom } from "../api/RoomAPI";

export default function Home() {
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
