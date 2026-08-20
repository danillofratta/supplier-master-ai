interface Props {
  status: string;
}

export function StatusBadge({ status }: Props) {
  const normalized = status
    .toLowerCase()
    .replaceAll("_", "-");

  return (
    <span
      className={`status-badge status-${normalized}`}
    >
      {status.replaceAll("_", " ")}
    </span>
  );
}
