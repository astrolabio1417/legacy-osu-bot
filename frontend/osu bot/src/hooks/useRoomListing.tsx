import { useEffect, useState } from "react";
import { IRoom } from "../Interface";
import { CONFIG } from "../constants";

export default function useRoomListing() {
  const [roomList, setRoomList] = useState<IRoom[]>([]);

  useEffect(() => {
    async function fetchRooms() {
      const res = await fetch(`${CONFIG.api}/room`);

      if (!res.ok) return;

      const rooms: IRoom[] = await res.json();
      setRoomList(rooms);
    }

    const fetchInterval = setInterval(() => fetchRooms(), 1000);

    return () => {
      clearInterval(fetchInterval);
    };
  }, []);

  return { roomList, setRoomList };
}
