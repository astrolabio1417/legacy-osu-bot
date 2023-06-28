import { toast } from "react-toastify";
import { IRoomForm } from "../types/roomFormInterface";
import { API } from "../data/constants";

export async function createRoom(values: IRoomForm) {
  const res = await fetch(`${API}/room`, {
    method: "POST",
    credentials: "include",
    body: JSON.stringify(values),
    headers: {
      "content-type": "application/json",
    },
  });

  if (!res.ok) {
    toast("Submission Failed", {
      type: "error",
    });

    return false;
  }

  toast("Room Created");

  return true;
}

export async function deleteRoom(id: string) {
  const res = await fetch(`${API}/room/${id}`, {
    credentials: "include",
    method: "delete",
  });

  if (!res.ok) {
    toast("Deletion Failed", {
      type: "error",
    });

    return;
  }

  toast("Deletion Success");
}

export async function updateRoom(values: IRoomForm, id: string) {
  const res = await fetch(`${API}/room/${id}`, {
    credentials: "include",
    method: "put",
    body: JSON.stringify(values),
    headers: {
      "content-type": "application/json",
    },
  });

  if (!res.ok) {
    toast("Update Failed", {
      type: "error",
    });

    return false;
  }

  toast("Update Success");
  return true;
}
