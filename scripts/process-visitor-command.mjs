import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, '..');

const issueTitle = process.env.ISSUE_TITLE || '[OPS-COMMAND]: PING_NODE4';
const rawUser = process.env.ISSUE_USER || 'octocat';

// Sanitize user name to prevent markdown / injection
const issueUser = rawUser.replace(/[^a-zA-Z0-9-_]/g, '').substring(0, 30) || 'anonymous';

function getCommandResponse(title, user) {
  const upper = title.toUpperCase();
  const latency = Math.floor(Math.random() * 25) + 22; // 22ms - 46ms
  const now = new Date().toISOString().replace('T', ' ').substring(0, 16) + ' UTC';

  if (upper.includes('PING_NODE4')) {
    return {
      time: now,
      user: `@${user}`,
      cmd: 'PING_NODE4',
      result: `PONG (${latency}ms) · Note 4 Edge Node [Termux] Online · ~1.18W Nominal`
    };
  } else if (upper.includes('RUN_SAFETY_EVAL')) {
    return {
      time: now,
      user: `@${user}`,
      cmd: 'RUN_SAFETY_EVAL',
      result: `EVAL_OK · Turkish Straits Sector: Wind < 16kt · Wave 0.6m · Status: GO (SAFE)`
    };
  } else if (upper.includes('CALLSIGN')) {
    const parts = title.split(':');
    const callsign = (parts[1] || 'OPERATOR').replace('CALLSIGN', '').trim() || 'STATION-ALPHA';
    const cleanCallsign = callsign.replace(/[^a-zA-Z0-9-_\s]/g, '').substring(0, 20);
    return {
      time: now,
      user: `@${user}`,
      cmd: `CALLSIGN [${cleanCallsign}]`,
      result: `ACKNOWLEDGED · Frequency 156.800 MHz (VHF CH 16) · Welcome to Command Station`
    };
  } else {
    return {
      time: now,
      user: `@${user}`,
      cmd: 'SYS_QUERY',
      result: `COMMAND_PROCESSED (${latency}ms) · All systems operational`
    };
  }
}

function updateReadmeLog(newEntry) {
  const readmePath = path.join(rootDir, 'README.md');
  if (!fs.existsSync(readmePath)) {
    console.error('README.md not found.');
    return;
  }

  let content = fs.readFileSync(readmePath, 'utf8');

  const startMarker = '<!-- VISITOR_LOG_START -->';
  const endMarker = '<!-- VISITOR_LOG_END -->';

  const startIndex = content.indexOf(startMarker);
  const endIndex = content.indexOf(endMarker);

  if (startIndex === -1 || endIndex === -1) {
    console.warn('Visitor log markers not found in README.md.');
    return;
  }

  const existingBlock = content.substring(startIndex + startMarker.length, endIndex).trim();
  const existingRows = existingBlock.split('\n').filter(line => line.startsWith('| `'));

  // Format new row
  const newRow = `| \`${newEntry.time}\` | **${newEntry.user}** | \`${newEntry.cmd}\` | \`${newEntry.result}\` |`;

  // Prepend new row and limit to 5 entries
  const allRows = [newRow, ...existingRows].slice(0, 5);

  const updatedTable = `\n| \`UTC TIME\` | \`OPERATOR\` | \`COMMAND\` | \`TELEMETRY TELETYPE OUTPUT\` |\n| :--- | :--- | :--- | :--- |\n${allRows.join('\n')}\n`;

  const newContent = content.substring(0, startIndex + startMarker.length) + updatedTable + content.substring(endIndex);
  fs.writeFileSync(readmePath, newContent, 'utf8');
  console.log(`[Visitor-Ops] Successfully logged command from ${newEntry.user} to README.md!`);
}

const entry = getCommandResponse(issueTitle, issueUser);
updateReadmeLog(entry);
