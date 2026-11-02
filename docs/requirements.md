# TaskFlow API: Requirements

## Goal
A REST service for creating and managing tasks, with a check for
whether a task's due date falls on a public holiday.

## Task fields
| Field | Rules |
|---|---|
| id | integer, assigned by the database |
| title | required, 1-100 characters, not only whitespace |
| description | optional, max 500 characters |
| status | one of: todo, in_progress, done (default: todo) |
| due_date | optional, ISO date (YYYY-MM-DD) |
| created_at / updated_at | set by the server |

## Acceptance criteria
- WHEN a client POSTs a valid task, THE SYSTEM SHALL store it and return 201 with the task.
- WHEN a client POSTs an invalid task, THE SYSTEM SHALL return 422 and store nothing.
- WHEN a client GETs an existing task, THE SYSTEM SHALL return 200 with the task.
- WHEN a client requests a task id that does not exist, THE SYSTEM SHALL return 404.
- WHEN a client updates a task, THE SYSTEM SHALL change only the supplied fields, refresh updated_at, and return 200.
- WHEN a client deletes a task, THE SYSTEM SHALL remove it and return 204.
- WHEN a client lists tasks, THE SYSTEM SHALL support filtering by status and pagination (limit, offset).
- WHEN a client asks for a holiday check on a task with a due date, THE SYSTEM SHALL call the external holiday API and report whether the date is a public holiday.
- WHEN the external API is slow, down, or returns bad data, THE SYSTEM SHALL return 502/504 with a clear message, and the rest of the service SHALL keep working.
- WHEN the task has no due date, THE SYSTEM SHALL return 400 for the holiday check, without calling the external API.
- THE SYSTEM SHALL read all configuration from environment variables.
- THE SYSTEM SHALL log each request and every error.
- THE SYSTEM SHALL expose interactive OpenAPI docs at /docs.

## Edge cases (decided up front)
- Title of only spaces: rejected (422).
- Title of exactly 100 characters: accepted. 101: rejected.
- Invalid status value, e.g. "finished": 422.
- Non-integer id, e.g. /tasks/abc: 422.
- limit=0 or negative, or limit over 100: 422.
- Empty PATCH body: 422, nothing to update.
- Deleting an already-deleted task: 404 (not 204).
- Due date in the past: allowed (people log old tasks).

## Out of scope
Authentication, users, tags, soft delete, rate limiting.