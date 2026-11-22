// Shared helpers that reproduce the "Video Editing Guideline.docx" house format:
// US Letter, 1" margins, Calibri 11, numbered 16pt bold section headings ending " :",
// "1.1" numbered points, framed example images, dark-header tables.
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell,
  AlignmentType, LevelFormat, WidthType, ShadingType, BorderStyle, PageBreak,
  Footer, Header, PageNumber,
} = require("docx");

const ACCENT = "C8862B"; // warm gold (house format)

function runs(text, base = {}) {
  const out = [];
  const re = /(\*\*\*[^*]+\*\*\*|\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)/g;
  let last = 0, m;
  while ((m = re.exec(text))) {
    if (m.index > last) out.push(new TextRun({ text: text.slice(last, m.index), ...base }));
    const t = m[0];
    if (t.startsWith("***")) out.push(new TextRun({ text: t.slice(3, -3), bold: true, italics: true, ...base }));
    else if (t.startsWith("**")) out.push(new TextRun({ text: t.slice(2, -2), bold: true, ...base }));
    else if (t.startsWith("`")) out.push(new TextRun({ text: t.slice(1, -1), font: "Consolas", color: "8A4B08", ...base }));
    else out.push(new TextRun({ text: t.slice(1, -1), italics: true, ...base }));
    last = m.index + t.length;
  }
  if (last < text.length) out.push(new TextRun({ text: text.slice(last), ...base }));
  return out;
}

const H = (text) => new Paragraph({
  numbering: { reference: "guide", level: 0 }, keepNext: true,
  spacing: { before: 360, after: 160 },
  children: [new TextRun({ text: text + " :", bold: true, size: 32 })],
});
const P = (text) => new Paragraph({ numbering: { reference: "guide", level: 1 }, spacing: { after: 120 }, children: runs(text) });
const SUB = (text) => new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 80 }, children: runs(text) });
const NOTE = (text) => new Paragraph({ indent: { left: 1080 }, spacing: { after: 240 }, children: runs(text, { italics: true, size: 18, color: "666666" }) });
const TXT = (text, opts = {}) => new Paragraph({ spacing: { after: 120 }, indent: opts.indent ? { left: opts.indent } : undefined, children: runs(text, opts.run || {}) });
const QUOTE = (text) => new Paragraph({
  indent: { left: 1440, right: 720 }, spacing: { before: 60, after: 120 },
  border: { left: { style: BorderStyle.SINGLE, size: 18, color: ACCENT, space: 10 } },
  children: runs(text, { italics: true, color: "333333" }),
});
const spacer = () => new Paragraph({ spacing: { after: 120 }, children: [] });
const pageBreak = () => new Paragraph({ children: [new PageBreak()] });

function img(file, wIn, hIn) {
  const data = fs.readFileSync(file);
  const type = file.toLowerCase().endsWith(".png") ? "png" : "jpg";
  const name = path.basename(file);
  return new ImageRun({ type, data, transformation: { width: Math.round(wIn * 96), height: Math.round(hIn * 96) },
    altText: { title: name, description: name, name } });
}
// a row of images with a fixed aspect (w/h)
function imgRow(files, wIn, aspect, indent = 1080) {
  const kids = [];
  files.forEach((f, i) => { if (i) kids.push(new TextRun({ text: "  " })); kids.push(img(f, wIn, wIn / aspect)); });
  return new Paragraph({ indent: { left: indent }, spacing: { before: 120, after: 60 }, keepNext: true, children: kids });
}

const border = { style: BorderStyle.SINGLE, size: 4, color: "BFBFBF" };
const borders = { top: border, bottom: border, left: border, right: border };
function table(widths, rows, opts = {}) {
  const total = widths.reduce((a, b) => a + b, 0);
  return new Table({
    width: { size: total, type: WidthType.DXA }, columnWidths: widths,
    indent: { size: opts.indent ?? 360, type: WidthType.DXA },
    rows: rows.map((r, ri) => new TableRow({
      tableHeader: ri === 0, cantSplit: true,
      children: r.map((c, ci) => {
        let fill = ri === 0 ? "1F1F1F" : (ri % 2 === 0 ? "F6F3EE" : "FFFFFF");
        let text = c;
        if (opts.swatch && ci === 0 && ri > 0) { fill = c.replace("#", ""); text = ""; }
        return new TableCell({
          borders, width: { size: widths[ci], type: WidthType.DXA },
          shading: { fill, type: ShadingType.CLEAR, color: "auto" },
          margins: { top: 60, bottom: 60, left: 100, right: 100 },
          children: [new Paragraph({ children: runs(text, { size: 18, ...(ri === 0 ? { bold: true, color: "FFFFFF" } : {}) }) })],
        });
      }),
    })),
  });
}

function titleBlock(title, subtitle, intro) {
  return [
    new Paragraph({ spacing: { after: 60 }, children: [new TextRun({ text: title, bold: true, size: 44 })] }),
    new Paragraph({ spacing: { after: 120 }, border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: ACCENT, space: 6 } },
      children: [new TextRun({ text: subtitle, size: 20, color: "555555" })] }),
    ...intro.map((t) => TXT(t)),
  ];
}

async function build(out, children, docTitle) {
  const doc = new Document({
    creator: "Zoomby Show", title: docTitle,
    styles: { default: { document: { run: { font: "Calibri", size: 22 } } } },
    numbering: { config: [
      { reference: "guide", levels: [
        { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 540 } }, run: { bold: true, size: 32 } } },
        { level: 1, format: LevelFormat.DECIMAL, text: "%1.%2", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 1080, hanging: 540 } } } },
      ] },
      { reference: "bullets", levels: [
        { level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 1440, hanging: 300 } } } },
      ] },
    ] },
    sections: [{
      properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
      headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT,
        children: [new TextRun({ text: docTitle, size: 16, color: "999999" })] })] }) },
      footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
        children: [new TextRun({ children: [PageNumber.CURRENT], size: 18, color: "888888" })] })] }) },
      children,
    }],
  });
  const b = await Packer.toBuffer(doc);
  fs.writeFileSync(out, b);
  console.log("wrote", out, b.length);
}

module.exports = { runs, H, P, SUB, NOTE, TXT, QUOTE, spacer, pageBreak, img, imgRow, table, titleBlock, build };
