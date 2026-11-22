// Render a document spec (JSON list of blocks, written by prompt_sheet.py) to .docx in the house format.
// Usage: node prompt_sheet_docx.js SPEC.json OUT.docx "Header title"
// Blocks: {t:"title",title,subtitle,intro:[]} {t:"H",text} {t:"P",text} {t:"SUB",text} {t:"NOTE",text}
//         {t:"CODE",text} {t:"table",widths:[dxa...],rows:[[...]...]} {t:"pagebreak"}
const fs = require("fs");
const { Paragraph, TextRun, BorderStyle } = require("docx");
const L = require("./house_docx");

const CODE = (t) => new Paragraph({
  indent: { left: 1080 }, spacing: { before: 60, after: 160 },
  shading: { fill: "F2F2F2", type: "clear", color: "auto" },
  border: { left: { style: BorderStyle.SINGLE, size: 12, color: "8A3FE9", space: 8 } },
  children: t.split("\n").map((line, i) => new TextRun({ text: line, font: "Consolas", size: 19, break: i ? 1 : 0 })),
});

const [, , specPath, out, header] = process.argv;
const spec = JSON.parse(fs.readFileSync(specPath, "utf8"));
const kids = [];
for (const b of spec) {
  switch (b.t) {
    case "title": kids.push(...L.titleBlock(b.title, b.subtitle, b.intro || [])); break;
    case "H": kids.push(L.H(b.text)); break;
    case "P": kids.push(L.P(b.text)); break;
    case "SUB": kids.push(L.SUB(b.text)); break;
    case "NOTE": kids.push(L.NOTE(b.text)); break;
    case "CODE": kids.push(CODE(b.text)); break;
    case "table": kids.push(L.table(b.widths, b.rows), L.spacer()); break;
    case "pagebreak": kids.push(L.pageBreak()); break;
    default: throw new Error("unknown block " + b.t);
  }
}
L.build(out, kids, header || "Zoomby Show · Flow prompt sheet");
