import { useEffect, useState } from "react";
import { CONFIG } from "../constants";
import { IEnumsResponse } from "../Interface";

export default function useEnums() {
  const [enums, setEnums] = useState<IEnumsResponse | null>(null);

  useEffect(() => {
    async function fetchEnums() {
      const res = await fetch(`${CONFIG.api}/enums`);

      if (!res.ok) return;

      const enumsJson = await res.json();
      setEnums(enumsJson);
    }

    fetchEnums();
  }, []);

  return { enums, setEnums };
}
