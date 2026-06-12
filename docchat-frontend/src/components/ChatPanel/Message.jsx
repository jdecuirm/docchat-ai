import AIBubble from "./AIBubble";
import UserBubble from "./UserBubble";

export default function Message({ message }) {
  return message.role === "user" ? (
    <UserBubble message={message} />
  ) : (
    <AIBubble message={message} />
  );
}
