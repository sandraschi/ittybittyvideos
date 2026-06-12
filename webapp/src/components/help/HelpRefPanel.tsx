import { type ReactNode } from "react";
import { ALL_GROUPS, type ExternalRef } from "@/data/external-links";

function RefLinks({ item }: { item: ExternalRef }) {
  const links: { href: string; label: string }[] = [];
  if (item.homepage) links.push({ href: item.homepage, label: "Homepage" });
  if (item.docs) links.push({ href: item.docs, label: "Docs" });
  if (item.repo) links.push({ href: item.repo, label: "GitHub" });
  if (item.api) links.push({ href: item.api, label: "API" });
  if (links.length === 0) return null;
  return (
    <span className="flex flex-wrap gap-x-3 gap-y-1 mt-1">
      {links.map(({ href, label }) => (
        <a
          key={href}
          href={href}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-400 hover:text-blue-300 text-xs underline-offset-2 hover:underline"
        >
          {label} ↗
        </a>
      ))}
    </span>
  );
}

export function HelpLinksCatalog() {
  return (
    <div className="space-y-6">
      <p className="text-zinc-400 leading-relaxed">
        Official homepages and repositories for every integrated provider. Full markdown copy lives in{" "}
        <code className="text-blue-400 text-xs">docs/EXTERNAL-REFERENCES.md</code> in the repo.
      </p>
      {ALL_GROUPS.map(({ title, items }) => (
        <section key={title} className="rounded-lg border border-zinc-800 bg-zinc-900/80 p-5 space-y-3">
          <h2 className="text-lg font-semibold text-zinc-100">{title}</h2>
          <ul className="space-y-3">
            {items.map((item) => (
              <li key={item.name} className="border-b border-zinc-800/80 pb-3 last:border-0 last:pb-0">
                <p className="font-medium text-zinc-200">{item.name}</p>
                <RefLinks item={item} />
                {item.note && <p className="text-xs text-zinc-500 mt-1">{item.note}</p>}
              </li>
            ))}
          </ul>
        </section>
      ))}
    </div>
  );
}

export function ExternalHref({
  href,
  children,
}: {
  href: string;
  children: ReactNode;
}) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="text-blue-400 hover:text-blue-300 underline-offset-2 hover:underline"
    >
      {children}
    </a>
  );
}
