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
          md: 2,
          lg: 2,
          xl: 3,
          xxl: 4,
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
