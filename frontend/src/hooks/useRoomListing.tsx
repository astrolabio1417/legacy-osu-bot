import { useEffect, useState } from "react";
import { IRoom } from "../types/roomInterface";
import { API } from "../data/constants";

export default function useRoomListing() {
  const [roomList, setRoomList] = useState<IRoom[]>([]);

  useEffect(() => {
    let isFetching = false;

    async function fetchRooms() {
      isFetching = true
      const res = await fetch(`${API}/room`);
      isFetching = false      
      if (!res.ok) return;

      const rooms: IRoom[] = await res.json();
      setRoomList(rooms);
    }

    const fetchInterval = setInterval(() => !isFetching && fetchRooms(), 1000);

    return () => {
      clearInterval(fetchInterval);
    };
  }, []);

  return { roomList, setRoomList };
}
