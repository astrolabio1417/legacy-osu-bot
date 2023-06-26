import { IRoom } from "../../../types/roomInterface";
import { List } from "antd";
import RoomCard from "./RoomCard";

export default function RoomListing(prop: IRoomListing) {
  return (
    <div>
      <List
        grid={{
          gutter: 16,
          xs: 1,
          sm: 1,
          md: 1,
          lg: 1,
          xl: 2,
          xxl: 3,
        }}
        dataSource={prop.list}
        renderItem={(room) => <RoomCard {...room} />}
      />
    </div>
  );
}

interface IRoomListing {
  list: IRoom[];
}
