# Planning export templates: QA reference

This reference describes the rendered output for the four planning export
layouts configured in `data/planning_export_templates.json`. QA should render
each layout with the selected planning items as its input and verify the
inclusion, ordering, conditional fields, and exclusions below. All examples
refer to visible output; HTML tags may vary only where the template markup
specifies them.

## Common rules

### Date and time

- Dates and times use the linked event's start/end and timezone when available.
  Otherwise the formatter uses the first scheduled coverage time, then the
  planning item's `planning_date`. If the timezone is missing, Brussels time
  (`Europe/Brussels`) is used.
- The image planning layouts group entries by local date, oldest date first.
  Their date heading is uppercase, for example `FRIDAY 9 JANUARY 2026`.
- The bilingual layouts show one uppercase weekday/date heading, for example
  `FRIDAY 9 JANUARY 2026`. It is derived from the first planning item passed to
  the formatter, not necessarily the earliest item in the selection.
- A timed event with equal start and end displays `HH:MM`. A start/end range
  displays `HH:MM - HH:MM`. An all-day event (00:00 start through 23:59 end),
  or an event beginning at midnight and ending later, has no displayed time.
  If a valid schedule has no event end time, it is treated as a single time.
- Entries with no usable scheduled date are omitted from Photo and Video
  Planning. The bilingual layouts can still render the item, with no time.

### Event and planning fields

- When an event is linked, its first calendar, links, location, and contact
  records are used where the layout displays those fields. Without a linked
  event, the planning item's location and contact records are used and event
  links/calendar are unavailable.
- A location is displayed as a comma-separated address using the localized
  location name, address line, postal code and city/area, and country, omitting
  empty parts.
- Contact output consists of organisation, name, job title, email address(es),
  public phone number(s), public mobile number(s), and website, separated by
  ` - `. Non-public phone and mobile numbers must not appear.
- A French title or description is omitted when it is empty or identical to
  the Dutch value. The image planning layouts do not show descriptions or
  contacts.
- Photo/Video coverage assignment text is the assigned user's sign-off (or
  username), otherwise the desk name, otherwise the coverage status; this
  text is uppercased. Missing coverage status defaults to `ON MERIT`.
- Bilingual coverage labels are uppercase and have the form
  `BELGA <TYPE> (<STATUS>)`. Text labels include a language, e.g.
  `BELGA TEXT N (PLANNED)` or `BELGA TEXT F (ON MERIT)`; non-text labels do not,
  e.g. `BELGA PICTURE (PLANNED)`. The default status is `ON MERIT`.

## Video Planning

Configured as **Belga Image Video Planning**
(`internal_image_video_planning`).

### Include/exclude checks

- Include a planning item only when it has a `video` coverage and a scheduled
  date. Exclude it if it has only `picture` and/or `text` coverage, has no
  scheduled date, or links to an event in an Editorial calendar.
- If an item has both video and other coverage types, include it and show only
  the video coverage assignment(s).
- A linked event's `dates.start` takes precedence over coverage scheduled time
  and `planning_date`.

### Order and visible fields

- Group by local date in ascending date order. Within each date, sort all
  entries chronologically by scheduled instant, regardless of event calendar.
- Show the date heading, then for each entry: time if available, location if
  available, Dutch title if non-empty, French title if non-empty and different
  from Dutch, event link(s), then one assignment/status line per video
  coverage.
- Titles use the planning item's name, falling back to slugline. Descriptions,
  contacts, and calendar headings are not shown.
- Example: given a video coverage assigned to user sign-off `TST`, the entry
  includes `TST`; it does not include `BELGA VIDEO` or the planning description.

## Photo Planning

Configured as **Belga Image Photo Planning**
(`internal_image_photo_planning`).

### Include/exclude checks

- Include a planning item only when it has a `picture` coverage and a scheduled
  date. Exclude it if it has only `video` and/or `text` coverage, has no
  scheduled date, or links to an event in an Editorial calendar.
- If an item has multiple coverage types, include it and show only picture
  coverage assignment(s).
- A linked event's `dates.start` takes precedence over coverage scheduled time
  and `planning_date`.

### Order and visible fields

- Group by local date in ascending date order. Within each date show calendar
  groups in this order: **Sports**, then **General**. Sports events are in the
  Sports group; all other event calendar names are placed in General.
- Entries within a calendar group retain their input order; unlike Video
  Planning, this layout does not sort entries by time.
- Show the date heading, calendar heading, then for each entry: time if
  available, location if available, Dutch title if non-empty, French title if
  non-empty and different from Dutch, event link(s), then one assignment/status
  line per picture coverage.
- Titles use the planning item's name, falling back to slugline. Descriptions
  and contacts are not shown.
- Current behavior to verify: an item whose event has no calendar is collected
  under an empty calendar name, but the template only renders Sports and
  General. Such an item is therefore not displayed.
- Example: a planning item with text, picture, and video coverages appears
  under its event calendar, shows the picture assignee/status, and does not
  show the text/video coverages or planning description.

## Bilingual daily program

Configured as **Bilingual daily program**
(`bilingual_planning_advisory_tomorrow`).

### Include/exclude checks

- Render every selected planning item except those linked to an event in an
  Editorial calendar. Do not filter by coverage type; picture, video, text, or
  mixed coverage items may all appear.
- A planning item without a linked event is grouped under **Overig / Divers**.
- When a linked event has a calendar, use the first event calendar's
  capitalized qcode as the group name.

### Order and visible fields

- Show the date heading and the fixed Dutch and French introductory paragraphs.
- Calendar groups use this order when present: General, Politics, Economy,
  Regional, Justice, International, Sports, Culture; additional calendar names
  follow alphabetically.
- Within a calendar, entries with a displayed time come first and sort by the
  formatted time string; entries with no displayed time follow.
- Each entry can show, in order: time, location, Dutch title, French title if
  different, Dutch description, French description if different, each linked
  event URL, each contact line, then each coverage label.
- Titles prefer the linked event's translated name; if absent, use the planning
  item's translated name, slugline, then headline. Descriptions use the
  planning item's translated description only.
- Coverage labels show type/status and text language, but do not append the
  assigned user or desk.
- Example coverage output for two text coverages assigned to Dutch and French
  desks, plus a picture coverage, is:
  `BELGA TEXT N (PLANNED)`, `BELGA TEXT F (ON MERIT)`,
  `BELGA PICTURE (PLANNED)`.

## Bilingual daily program for internal use

Configured as **Bilingual daily program for internal use**
(`internal_bilingual_planning_advisory_tomorrow`).

### Include/exclude checks

- Render all selected planning items, including items linked to an event in an
  Editorial calendar. Do not filter by coverage type.
- The calendar group uses the first linked event calendar's capitalized qcode.
  When there is no linked event calendar, the current output has an empty
  calendar heading (unlike the public layout's **Overig / Divers** fallback).

### Order and visible fields

- Show the same date heading and Dutch/French introductory paragraphs as the
  public bilingual program.
- Use the same calendar ordering and within-calendar timed-first ordering as
  the public bilingual program.
- Show the same entry fields as the public bilingual program, including
  translated planning descriptions, event links, contact lines, and coverage
  labels.
- Titles come from the planning item's name, slugline, then headline; they do
  not prefer the linked event's name. Descriptions still come from the
  translated planning description.
- Append assignment to each coverage label: assigned user's sign-off (or
  username) in uppercase if present; otherwise the assigned desk name in
  uppercase. If neither exists, do not append `BY ...`.
- Example output includes `BELGA VIDEO (PLANNED) BY VIDEO` when the assigned
  user's sign-off is `VIDEO`, and `BELGA PICTURE (PLANNED) BY DESK NAME` when
  only the desk is assigned.

## Suggested QA matrix

For each template, use a small fixture set with a matching coverage, a
non-matching coverage, a linked Editorial-calendar event, an event without a
calendar, and a planning item without an event. Then verify these focused
cases:

| Case | Setup | Expected result |
|---|---|---|
| Coverage filter | Matching coverage only, then non-matching only, then mixed | Image layouts include matching/mixed only and print only their matching coverage; bilingual layouts include all coverage types. |
| Editorial calendar | Linked event calendar name/qcode contains `editorial` | Photo, Video, and public bilingual layouts omit the item; internal bilingual includes it. An item without a linked event is unaffected. |
| Missing schedule | No event start, no scheduled coverage, no planning date | Omitted from Photo/Video; retained in bilingual output without a time. |
| Schedule precedence | Event date differs from coverage schedule and planning date | Event date/time is used. |
| All-day and timed range | Use 00:00–23:59, a normal range, and equal start/end | All-day has no time; range is `HH:MM - HH:MM`; equal endpoints show one `HH:MM`. |
| Date/time order | Pass items out of order across two dates and multiple times | Image dates ascend; Video times ascend across calendars; Photo entries keep input order within a calendar; bilingual groups sort timed entries first. |
| Translation fallback | Event and planning titles/descriptions differ; then make French equal Dutch | Public bilingual title prefers event translation; internal uses planning title; descriptions use planning translation; duplicate French values are not repeated. |
| Contact privacy | Add public and private phone/mobile values to a contact | Display contact fields and public numbers only; private phone/mobile values are absent. |
| Coverage assignment | Set sign-off, username without sign-off, desk only, and no assignment | Image output precedence is sign-off > username > desk > status; internal bilingual appends user or desk to coverage label; public bilingual has no assignee suffix. |
| Calendar fallback | Use no event, event without calendar, Sports, and another calendar | Public bilingual no-event group is **Overig / Divers**; internal bilingual has an empty heading; Photo groups Sports before General; Video has no calendar headings. |

These are current implementation behaviors, including the no-calendar Photo
Planning omission and the internal bilingual blank calendar heading. Treat
those two cases as regression expectations unless product requirements specify
that they should change.
