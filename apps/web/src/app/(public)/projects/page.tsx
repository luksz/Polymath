import Link from "next/link";
import { contentApi } from "@/lib/api/content";

export const metadata = { title: "Projects" };

export default async function ProjectsPage() {
  let projects = [];
  try {
    projects = await contentApi.listPosts({ kind: "project" });
  } catch {
    // content-svc may not be running locally
  }

  return (
    <div className="mx-auto max-w-2xl px-6 py-20">
      <h1 className="text-3xl font-bold tracking-tight">Projects</h1>
      <p className="mt-3 text-muted-foreground">
        Things I've built or am building.
      </p>

      <div className="mt-12 grid gap-4 sm:grid-cols-2">
        {projects.length === 0 ? (
          <p className="text-sm text-muted-foreground col-span-2">No projects yet.</p>
        ) : (
          projects.map((project) => (
            <Link
              key={project.id}
              href={`/blog/${project.slug}`}
              className="group rounded-lg border border-border p-5 hover:border-foreground/30 transition-colors space-y-2"
            >
              {project.cover_image_url && (
                <img
                  src={project.cover_image_url}
                  alt={project.title}
                  className="w-full h-32 object-cover rounded-md"
                />
              )}
              <h2 className="font-semibold group-hover:underline underline-offset-4">
                {project.title}
              </h2>
              {project.summary && (
                <p className="text-sm text-muted-foreground">{project.summary}</p>
              )}
            </Link>
          ))
        )}
      </div>
    </div>
  );
}
