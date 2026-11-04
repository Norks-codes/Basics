# Project Control Tower

A one-file companion to the project's Excel tracker. It reads the tracker and tells you what needs you today, what to chase, and what to ask your team to do and check. You can update items here and download the same workbook back with your changes written in.

- **One file:** `index.html`. Double-click it and it opens in your browser. There's no install, no terminal and no password.
- **Private by design:** your tracker is read inside your browser and saved only on your computer. The file makes **no network calls**, and there is no project data in this repository.
- **Excel stays the master copy.** The tool writes your changes into the workbook's cells directly, so its colours, dropdowns, formulas and Summary tab stay exactly as they were.

## Get it running

1. On GitHub, open `control-tower/index.html` and click **Download raw file**.
2. Double-click the downloaded file. It opens in Edge, Chrome or Safari.
3. Drop your tracker `.xlsx` onto the page.

Keep the file somewhere permanent, such as Documents. Your browser remembers your data for that file on that computer.

## The tabs

| Tab | What it's for |
|---|---|
| **Today** | Your list for today: today's plan and meetings, items where *you* act next that are overdue or due soon, and plan tasks not yet ticked. Also **Chase the Bank** (one drafted reminder email per Bank counterpart), the **10:00 check-in** agenda, the next 7 days and recent changes. |
| **Team prompts** | A ready-to-send message for Delali (or Salia): today's plan tasks, earlier tasks to confirm, their overdue items, tracker fixes (no named person, still "To confirm", no date, not updated), write-ups due, and your own notes. Edit it, then copy it into Teams, WhatsApp or email. |
| **Tracker** | Every item, with filters (type, Action Plan part, owner, flag). Click a row to edit it. Quick buttons: Done, Chased today, +2 working days, +1 week, and "Ask Delali about this". |
| **Interviews & sessions** | Progress counts against the targets, plus flags for missing briefs, overdue write-ups and countries not yet nominated. |
| **Plan & health** | Milestones, a red/amber/green view of the nine Action Plan results, the Management decisions, and the day-by-day plan with tick boxes. |
| **Data** | Load the latest Excel, download the updated Excel, copy your changes as a message, settings, backup, and the list of rules the checks use. |

## The daily loop

1. **Morning:** download the latest tracker from SharePoint and drop it on the page. A preview shows exactly what changed since last time. If Delali changed something you also edited here, that change is unticked so your version is kept, unless you tick it.
2. **During the day:** tick plan tasks, mark items Done, log chases and add items.
3. **Send changes back,** in one of two ways:
   - **Download updated Excel** and upload it to SharePoint. Do this only after loading Delali's latest copy, so you don't overwrite her work.
   - **Copy changes as a message** and send it to Delali, so she can apply the changes in the shared file. This is safer when you both edit on the same day.

## Workbook format

The tool finds each tab by name and each column by its heading in row 1, so the column order can change.

- **Tracker:** ID, Item, Type, Action Plan part, Owner, Next step, Due date, Status, Days overdue, Last updated, Notes and links
- **Interviews:** #, Interviewee, Organisation, Pathway, Route and owner, Stage, Interview date, Brief done, Write-up done, Next step, Notes
- **Sessions:** #, Session, Type, Hub or department, Country, Convened by, Status, Date, Write-up done, Notes
- **Plan** (optional): ID, Date, Week, Who, Task, Done, Notes. Who can be a person, `Meeting` or `Milestone`.
- **Lists** (optional): supplies the dropdown values.

## How the checks work

The tool uses only these rules. You can also read them on the Data tab.

- **Overdue / due soon:** the same red and amber rules the Excel uses.
- **No named person:** the owner is blank, "Several", "TBD" or "Bank, to confirm".
- **Still "To confirm":** this status should only last until the first check-in.
- **Not updated:** "Last updated" is more than 3 working days ago. Editing an item here sets it to today.
- **Slipped:** the notes say "Originally needed by …".
- **Critical path:** the notes say so, and one overdue critical item turns its Action Plan part red.
- **Who acts next:** the owner, plus anyone the next step names, as in "Miriam to …" or "Delali drafts …".
- **Write-ups:** due within 24 hours of an interview or session.

## For developers

Edit `src/app.html`, then run `python3 build.py`. This inlines `vendor/jszip.min.js` (MIT licence) and writes `index.html`. To test the tool as if it were another date, add `?today=YYYY-MM-DD` to the URL.
