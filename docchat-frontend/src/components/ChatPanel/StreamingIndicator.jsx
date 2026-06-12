export default function StreamingIndicator() {
  return (
    <div
      className="flex items-center gap-1 px-4 py-2 self-start"
      role="status"
      aria-label="Generating response"
    >
      {[0, 1, 2].map((i) => (
        <span
          key={i}
          className="inline-block w-2 h-2 rounded-full bg-accent"
          style={{
            animation: `pulse-dot 1.4s ease-in-out ${i * 0.16}s infinite`,
          }}
          aria-hidden="true"
        />
      ))}
    </div>
  );
}
