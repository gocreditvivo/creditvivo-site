export default function AssetStatusBadge({ status }) {
  const colors = {
    Draft: "badge slate",
    "Needs Review": "badge yellow",
    "Compliance Review": "badge orange",
    Approved: "badge green",
    Scheduled: "badge blue",
    Published: "badge indigo",
    Archived: "badge slate",
    Rejected: "badge red",
  };
  return <span className={colors[status] || colors.Draft}>{status}</span>;
}
