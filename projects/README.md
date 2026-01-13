# Projects

This folder contains project-specific workspaces. Each project gets its own subfolder.

## Structure

```
projects/
├── TEMPLATE.md              # Copy this when starting new projects
├── README.md                # This file
└── [project-name]/
    └── project.md           # Project overview and status
```

## Creating a New Project

```bash
mkdir projects/[project-name]
cp projects/TEMPLATE.md projects/[project-name]/project.md
# Edit project.md with project details
```

## Guidelines

1. **One project.md per project** - Single source of truth
2. **Keep it lean** - Delete empty sections
3. **Update frequently** - Current State reflects reality
4. **Actionable items** - Next Actions completable in one session
5. **Supporting files welcome** - Add research.md, notes.md alongside as needed
