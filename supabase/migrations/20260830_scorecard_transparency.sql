-- Persist scoring provenance and backend-owned rubric copy on existing deployments.
alter table scorecards
    add column if not exists sources jsonb not null default '[]',
    add column if not exists dimension_definitions jsonb not null default '[]';
