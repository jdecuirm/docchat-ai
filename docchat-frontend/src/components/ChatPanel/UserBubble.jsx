export default function UserBubble({ message }) {
  return (
    <div className="max-w-[80%] self-end">
      <div className="rounded-xl px-4 py-3 text-sm bg-accent text-white">
        {message.content}
      </div>
    </div>
  );
}
