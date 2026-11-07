/**
 * KEREM.OS AERO guestbook processor.
 * Accepts ONLY GitHub issue event fields; no network, user scripts, shell commands,
 * issue-body evaluation, arbitrary labels, simulated telemetry, or secrets.
 * This replaces the older fake PING_NODE4/RUN_SAFETY_EVAL processor.
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const readmePath = path.join(root, 'README.md');
const PREFIX = '[AERO-HELLO]';
const title = String(process.env.ISSUE_TITLE || '');
const login = String(process.env.ISSUE_USER || '');
const num = Number(process.env.ISSUE_NUMBER);
const createdAt = String(process.env.ISSUE_CREATED_AT || '');
if (!title.startsWith(PREFIX)) throw new Error('Unrecognized guestbook command');
if (!/^[A-Za-z0-9-]{1,39}$/.test(login)) throw new Error('Invalid GitHub login');
if (!Number.isSafeInteger(num) || num < 1) throw new Error('Invalid issue number');
const date = new Date(createdAt);
if (!Number.isFinite(date.getTime())) throw new Error('Invalid GitHub event timestamp');

// All user-provided content is treated as text and stripped of Markdown controls.
const message = (title.slice(PREFIX.length).trim() || 'Hello from GitHub')
  .normalize('NFKC')
  .replace(/[^\p{L}\p{N}\p{M} .,!?_-]/gu, '')
  .replace(/\s+/g, ' ')
  .slice(0, 68)
  .trim() || 'Hello from GitHub';
const stamp = date.toISOString().slice(0, 16).replace('T', ' ');
const issueUrl = `https://github.com/KeremKalyoncu/KeremKalyoncu/issues/${num}`;
const userUrl = `https://github.com/${login}`;
const newRow = `| \`${stamp}\` | [@${login}](${userUrl}) | [${message}](${issueUrl}) |`;

const original = fs.readFileSync(readmePath, 'utf8');
const START = '<!-- AERO_GUESTBOOK_START -->';
const END = '<!-- AERO_GUESTBOOK_END -->';
const begin = original.indexOf(START);
const end = original.indexOf(END, begin + START.length);
if (begin === -1 || end === -1 || begin >= end) throw new Error('Guestbook markers missing or malformed');
const oldBody = original.slice(begin + START.length, end);
const previous = oldBody.split(/\r?\n/).filter(line => /^\| `20\d{2}-\d{2}-\d{2} /.test(line));
// Keep the most recent four verified issues, dedupe re-delivery.
const seen = new Set();
const rows = [newRow, ...previous].filter(row => {
  const match = row.match(/issues\/(\d+)/);
  const key = match ? match[1] : row;
  if (seen.has(key)) return false;
  seen.add(key);
  return true;
}).slice(0, 4);
const table = `\n| UTC | Visitor | Message |\n| :--- | :--- | :--- |\n${rows.join('\n')}\n`;
const next = original.slice(0, begin + START.length) + table + original.slice(end);
if (next !== original) {
  fs.writeFileSync(readmePath, next, 'utf8');
  console.log(`Recorded genuine GitHub issue #${num} for @${login}`);
}
