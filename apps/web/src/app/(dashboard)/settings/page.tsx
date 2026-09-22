import React from 'react';
import { Info, Settings, SlidersHorizontal, Database } from 'lucide-react';

const configurationGroups = [
  {
    icon: Database,
    title: 'Storage and retention',
    description: 'Configured when the worker starts. Restart the stack after changing these values.',
    variables: ['DOWNLOAD_DIR', 'PROCESSED_DIR', 'STORAGE_QUOTA_BYTES', 'OUTPUT_RETENTION_HOURS'],
  },
  {
    icon: SlidersHorizontal,
    title: 'Runtime limits',
    description: 'Managed through the deployment environment so every worker uses the same policy.',
    variables: ['MAX_FILE_SIZE', 'CLEANUP_INTERVAL_SECONDS', 'RATE_LIMIT_REQUESTS', 'RATE_LIMIT_WINDOW'],
  },
];

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-slate-900 dark:text-slate-100 flex items-center gap-2.5">
          <Settings className="w-7 h-7 text-indigo-600 dark:text-indigo-400" />
          <span>Settings</span>
        </h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Understand how this Unividown deployment is configured.
        </p>
      </div>

      <div role="status" className="max-w-3xl flex gap-3 rounded-2xl border border-indigo-200 bg-indigo-50 p-5 text-indigo-950 dark:border-indigo-900 dark:bg-indigo-950/40 dark:text-indigo-100">
        <Info className="mt-0.5 h-5 w-5 shrink-0" aria-hidden="true" />
        <div>
          <h2 className="font-semibold">Configuration is deployment-managed</h2>
          <p className="mt-1 text-sm text-indigo-800 dark:text-indigo-200">
            This page is read-only. Unividown does not currently provide a settings API, so no control is shown as saved unless it changes the running service.
          </p>
        </div>
      </div>

      <div className="grid max-w-3xl gap-4 md:grid-cols-2">
        {configurationGroups.map(({ icon: Icon, title, description, variables }) => (
          <section key={title} className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
            <div className="flex items-center gap-2 text-slate-900 dark:text-slate-100">
              <Icon className="h-5 w-5 text-indigo-600 dark:text-indigo-400" aria-hidden="true" />
              <h2 className="font-semibold">{title}</h2>
            </div>
            <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">{description}</p>
            <ul className="mt-4 space-y-2" aria-label={`${title} environment variables`}>
              {variables.map((variable) => (
                <li key={variable}>
                  <code className="rounded bg-slate-100 px-2 py-1 text-xs text-slate-700 dark:bg-slate-800 dark:text-slate-200">
                    {variable}
                  </code>
                </li>
              ))}
            </ul>
          </section>
        ))}
      </div>
    </div>
  );
}
