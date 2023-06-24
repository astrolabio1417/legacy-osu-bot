import { useEffect, useState } from "react";
import { API } from "../data/constants";
import { IEnumsResponse } from "../types/enumsInterface";

export default function useEnums() {
  const [enums, setEnums] = useState<IEnumsResponse | null>(null);

  useEffect(() => {
    async function fetchEnums() {
      const res = await fetch(`${API}/enums`);

      if (!res.ok) return;

      const enumsJson = await res.json();
      setEnums(enumsJson);
    }

    fetchEnums();
  }, []);

  return { enums, setEnums };
}
