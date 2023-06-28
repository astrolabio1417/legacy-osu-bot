import { useState, useEffect } from "react";

import { API } from "../data/constants";

const initialSessionState = {
  username: "",
  is_admin: false,
  is_irc_running: false,
};
export default function useSession() {
  const [session, setSession] = useState({ ...initialSessionState });

  useEffect(() => {
    async function fetchSession() {
      const res = await fetch(`${API}/session`, {
        credentials: "include",
      });

      if (res.ok) {
        const data: {
          username: string;
          is_admin: boolean;
          is_irc_running: boolean;
        } = await res.json();
        setSession(data);
        return;
      }

      setSession({ ...initialSessionState });
    }

    fetchSession();
  }, []);

  return { session };
}
