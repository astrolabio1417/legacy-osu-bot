import { useEffect, useState } from "react";
import { IRoom } from "../types/roomInterface";
import { API } from "../data/constants";

export default function useRoomListing() {
  const [roomList, setRoomList] = useState<IRoom[]>([]);

  useEffect(() => {
    async function fetchRooms() {
      const res = await fetch(`${API}/room`);

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
