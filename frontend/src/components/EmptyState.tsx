import type { ReactNode } from "react";

interface Props {
  title: string;
  description: string;
  action?: ReactNode;
}

export default function EmptyState({ title, description, action }: Props) {
  return (
    <div className="card empty-state">
      <h3>{title}</h3>
      <p>{description}</p>
      {action}
    </div>
  );
}