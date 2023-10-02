import { useEffect, useState } from "react";
import { IRoom } from "../types/roomInterface";
import { API } from "../data/constants";

export default function useRoomListing() {
  const [roomList, setRoomList] = useState<IRoom[]>([]);

  useEffect(() => {
    let isFetching = false;

    async function fetchRooms() {
      if (isFetching) return;
      isFetching = true;

      try {
        const res = await fetch(`${API}/room`);
        if (!res.ok) return;
        const rooms: IRoom[] = await res.json();
        setRoomList(rooms);
      } catch (error) {
        console.error(error);
      } finally {
        isFetching = false;
      }
    }

    fetchRooms();
    const fetchInterval = setInterval(() => fetchRooms(), 1000);

    return () => {
      clearInterval(fetchInterval);
    };
  }, []);

  return { roomList, setRoomList };
}
