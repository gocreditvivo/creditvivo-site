import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const inputPath = "C:\\Users\\miste\\.codex\\attachments\\905ca5a1-0147-41f8-8462-82ac76906561\\pasted-text.txt";
const outputDir = "C:\\Users\\miste\\OneDrive\\Desktop\\pho eatery case\\Business_Public_Record_Audit_Samples";
const outputPath = path.join(outputDir, "DPOR_1206_NAIL_TECH_LICENSES_FROM_PASTED_TEXT_2026-07-08.xlsx");
const asOf = new Date("2026-07-08T00:00:00");

const raw = await fs.readFile(inputPath, "utf8");
const lines = raw.split(/\r?\n/).filter((line) => line.trim().length > 0);
const header = lines[0].split("\t");
const rows = lines.slice(1).map((line) => line.split("\t"));

function parseDate(value) {
  if (!value) return null;
  const [mm, dd, yyyy] = value.split("/");
  if (!yyyy) return null;
  return new Date(`${yyyy}-${mm.padStart(2, "0")}-${dd.padStart(2, "0")}T00:00:00`);
}

function occupationLabel(board, occupation) {
  if (board === "12" && occupation === "06") return "Individual Nail Technician";
  if (board === "12" && occupation === "08") return "Nail Technician Salon";
  if (board === "12" && occupation === "02") return "Cosmetology Salon";
  return "Other / verify";
}

const dataHeader = [
  ...header,
  "OCCUPATION LABEL",
  "STATUS AS OF 2026-07-08",
  "AUDIT NOTE",
];

const dataRows = rows.map((row) => {
  const normalized = Array.from({ length: header.length }, (_, i) => row[i] ?? "");
  const expiration = parseDate(normalized[15]);
  const status = expiration && expiration >= asOf ? "Current / not expired" : "Expired or missing date";
  const label = occupationLabel(normalized[0], normalized[1]);
  const note =
    label === "Individual Nail Technician"
      ? "This is an individual worker license record, not proof of a salon/shop license."
      : "Verify record type against DPOR license category.";
  return [...normalized, label, status, note];
});

const currentCount = dataRows.filter((row) => row[21] === "Current / not expired").length;
const expiredCount = dataRows.length - currentCount;
const occupationCounts = dataRows.reduce((acc, row) => {
  acc[row[20]] = (acc[row[20]] ?? 0) + 1;
  return acc;
}, {});

const workbook = Workbook.create();

const summary = workbook.worksheets.add("Summary");
summary.showGridLines = false;
summary.getRange("A1:F1").merge();
summary.getRange("A1").values = [["DPOR Pasted License File Review"]];
summary.getRange("A1").format = {
  fill: "#1F4E79",
  font: { bold: true, color: "#FFFFFF", size: 16 },
};
summary.getRange("A3:B11").values = [
  ["As-of date", "2026-07-08"],
  ["Source file", inputPath],
  ["Rows parsed", dataRows.length],
  ["Columns in source", header.length],
  ["Occupation code found", "12-06"],
  ["Record type", "Individual Nail Technician"],
  ["Current / not expired", currentCount],
  ["Expired / missing date", expiredCount],
  ["Main conclusion", "This file shows individual nail technician licenses, not the salon/shop license."],
];
summary.getRange("A3:A11").format = {
  fill: "#EAF2F8",
  font: { bold: true },
};
summary.getRange("A3:B11").format.borders = { preset: "all", style: "thin", color: "#D9E2EC" };
summary.getRange("A13:D13").values = [["Code", "Meaning", "Rows", "Why it matters"]];
summary.getRange("A13:D13").format = {
  fill: "#375623",
  font: { bold: true, color: "#FFFFFF" },
};
summary.getRange("A14:D16").values = [
  ["12-06", "Individual Nail Technician", occupationCounts["Individual Nail Technician"] ?? 0, "Worker license only; does not prove the shop/salon is licensed."],
  ["12-08", "Nail Technician Salon", 0, "This is the key salon license list to check for a nail salon business."],
  ["12-02", "Cosmetology Salon", 0, "Some salons may appear here instead of the nail-only salon list."],
];
summary.getRange("A14:D16").format.borders = { preset: "all", style: "thin", color: "#D9E2EC" };
summary.getRange("A18:F18").merge();
summary.getRange("A18").values = [[
  "Plain English: yes, the pasted file shows license/certificate information and it appears not expired as of 2026-07-08. But it is not the correct proof for Katie's Nail Spa as a business location because this is the individual nail technician list. For the salon/shop license, pull DPOR 1208 Nail Technician Salon and also check 1202 Cosmetology Salon."
]];
summary.getRange("A18").format = { fill: "#FFF2CC", font: { bold: true }, wrapText: true };
summary.getRange("A18").format.rowHeight = 72;
summary.getRange("A:B").format.autofitColumns();
summary.getRange("B:B").format.columnWidth = 46;
summary.getRange("B:B").format.wrapText = true;
summary.getRange("D:D").format.columnWidth = 48;

const records = workbook.worksheets.add("Parsed Records");
records.getRangeByIndexes(0, 0, 1, dataHeader.length).values = [dataHeader];
records.getRangeByIndexes(1, 0, dataRows.length, dataHeader.length).values = dataRows;
records.getRangeByIndexes(0, 0, 1, dataHeader.length).format = {
  fill: "#1F4E79",
  font: { bold: true, color: "#FFFFFF" },
};
records.freezePanes.freezeRows(1);
records.getRangeByIndexes(0, 0, dataRows.length + 1, dataHeader.length).format.borders = {
  preset: "inside",
  style: "thin",
  color: "#E5E7EB",
};
records.getRange("A:W").format.autofitColumns();
records.getRange("F:F").format.columnWidth = 26;
records.getRange("G:G").format.columnWidth = 18;
records.getRange("T:T").format.columnWidth = 30;
records.getRange("W:W").format.columnWidth = 58;
records.getRange("W:W").format.wrapText = true;

await fs.mkdir(outputDir, { recursive: true });

const preview = await workbook.render({
  sheetName: "Summary",
  autoCrop: "all",
  scale: 1,
  format: "png",
});
await fs.writeFile(path.join(outputDir, "DPOR_1206_NAIL_TECH_LICENSES_FROM_PASTED_TEXT_2026-07-08_preview.png"), new Uint8Array(await preview.arrayBuffer()));

const xlsx = await SpreadsheetFile.exportXlsx(workbook);
await xlsx.save(outputPath);

console.log(JSON.stringify({
  outputPath,
  rows: dataRows.length,
  currentCount,
  expiredCount,
  occupationCounts,
}, null, 2));
