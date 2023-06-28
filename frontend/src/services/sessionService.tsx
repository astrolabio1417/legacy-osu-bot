import { toast } from "react-toastify";
import { API } from "../data/constants";

export async function logout() {
    const res = await fetch(`${API}/session/logout`, {
        method: "post",
        credentials: "include"
    })

    if (res.ok) {
        toast("You have been logged out!")
        return true
    }

    toast("Something went wrong", {
        type: "error"
    })
    return false
}

export async function login(username: string, password: string) {
    const res = await fetch(`${API}/session/login`, {
        method: "post",
        body: JSON.stringify({username, password}),
        credentials: "include",
        headers: {
          "accept": "application/json",
          "content-type": "application/json"
        }
      })
      const jsonRes = await res.json();
      const {message} = jsonRes ?? {};
  
      if (res.ok) {
        toast("Login Success");
        return true
      }
      
      toast(message ?? "Login Failed", {
        type: "error"
      })
      return false
}