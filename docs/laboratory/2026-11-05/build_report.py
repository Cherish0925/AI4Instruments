"""Build figures and offline HTML from the analysis and bilingual Markdown.

python build_report.py IOP_vs_direct_records_20261105.zip
Requires numpy, matplotlib and markdown2, plus analyze.py outputs in this folder.
"""
import argparse
import base64
import csv
import html
import io
import json
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import markdown2
import numpy as np

from analyze import Archive

ROOT = Path(__file__).resolve().parent
REPOSITORY = "https://github.com/Cherish0925/AI4Instruments/blob/main/docs/laboratory/2026-11-05/"
COLORS = {"direct": "#8a969d", "iop": "#236955", "accent": "#ae6847", "ink": "#243531"}


def figures(archive, findings, pairs):
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "axes.labelcolor": COLORS["ink"], "text.color": COLORS["ink"],
                         "svg.fonttype": "none", "svg.hashsalt": "iop-lab-feedback-2026-11-05"})
    steps = findings["timing"]["steps"]
    labels = ["Hardware check", "Unpowered", "V1=5: V2 sweep", "V1=5: threshold", "V1=5: 2D scan",
              "Amplifier off: V1 sweep", "V1=12: thresholds", "V1=12: 2D scan", "Working line: up/down",
              "8-minute drift", "Power sweep", "Working line: -20 dBm"]
    fig, ax = plt.subplots(figsize=(10.4, 6.4))
    y = np.arange(len(steps))
    for offset, side in ((-.18, "direct"), (.18, "iop")):
        ax.barh(y + offset, [s[f"{side}_s"] for s in steps], .32,
                label="Direct" if side == "direct" else "IOP", color=COLORS[side])
    ax.set(yticks=y, yticklabels=labels, xlabel="Task duration (seconds)")
    ax.invert_yaxis()
    ax.set_axisbelow(True)
    ax.grid(axis="x", alpha=.16)
    ax.legend(frameon=False, loc="lower right")
    ax.set_title("Measured task durations", loc="left", pad=16, fontweight="bold")
    fig.tight_layout()
    fig.savefig(ROOT / "timing.svg", metadata={"Date": None})
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10.4, 4.3))
    for key, label, color in (("s21_rms_db", "S21", COLORS["iop"]), ("s12_rms_db", "S12", COLORS["accent"])):
        values = np.sort([float(r[key]) for r in pairs])
        ax.step(values, 100 * np.arange(1, len(values) + 1) / len(values), where="post", lw=2,
                color=color, label=f"{label}: median {np.median(values):.3f} dB")
    ax.axhline(95, color="#909090", lw=.7, linestyle=":")
    ax.set(xlabel="RMS amplitude difference (dB)", ylabel="Cumulative share of 514 pairs (%)",
           xlim=(0, 2), ylim=(0, 102))
    ax.grid(alpha=.15)
    ax.legend(frameon=False, loc="lower right")
    ax.set_title("Paired differences over 1.0-1.25 GHz", loc="left", pad=16, fontweight="bold")
    fig.tight_layout()
    fig.savefig(ROOT / "spectra.svg", metadata={"Date": None})
    plt.close(fig)

    relative = "sweep2d_v1_5/v2_5p0/v1_5p00_v2_5p00_v3_1p70.csv"
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.1), sharex=True)
    for side in ("direct", "iop"):
        a = np.loadtxt(io.StringIO(archive.text(f"{side}/data_band2/{relative}")), delimiter=",", skiprows=1)
        for ax, col, title in zip(axes, (3, 7), ("S21", "S12")):
            ax.plot(a[:, 0] / 1e6, a[:, col], color=COLORS[side], lw=1.8, label=side.upper() if side == "iop" else "Direct")
            ax.set(xlim=(1100, 1200), xlabel="Frequency (MHz)", ylabel="Amplitude (dB)", title=title)
            ax.grid(alpha=.15)
    axes[1].legend(frameon=False)
    fig.suptitle("Saved acquisition: V1=5 V, V2=5 V, VDD=1.7 V", x=.06, ha="left", fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, .93))
    fig.savefig(ROOT / "acquisition.svg", metadata={"Date": None})
    plt.close(fig)
    for name in ("timing.svg", "spectra.svg", "acquisition.svg"):
        path = ROOT / name
        path.write_text("\n".join(line.rstrip() for line in path.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")


CSS = """
:root{--ink:#243531;--green:#236955;--muted:#65736d;--paper:#f7f6f2;--line:#dedfd7;--gold:#d1ae6d}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.85 -apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans CJK SC','Microsoft YaHei',sans-serif}
a{color:var(--green);text-underline-offset:4px}button{font:inherit;cursor:pointer}button:focus-visible,a:focus-visible{outline:3px solid var(--gold);outline-offset:4px}
aside{position:fixed;inset:0 auto 0 0;width:246px;background:#203e34;color:#eef0e8;padding:33px 24px;display:flex;flex-direction:column;z-index:10}
.brand{display:flex;align-items:center;gap:12px;font-size:18px;letter-spacing:.02em;font-weight:650}.brand img{width:39px;height:39px}.side-note{font-size:12px;color:#b5c8bb;margin:17px 0 38px;letter-spacing:.06em}
nav{display:grid;gap:7px}nav button{background:none;border:0;color:#c9d7cf;text-align:left;padding:11px 12px;border-radius:6px;display:flex;align-items:center;gap:14px;line-height:1.5;font-size:14px}nav button span{font-size:11px;color:#91af9e;font-variant-numeric:tabular-nums}nav button[aria-current=page]{background:#f1f1e8;color:#203e34}nav button[aria-current=page] span{color:#537260}nav button:hover{background:#365448;color:white}
.side-bottom{margin-top:auto;font-size:12px;color:#b5c8bb}.side-bottom a{color:#e0c78d}main{margin-left:246px;padding:0 56px 50px;max-width:1510px}
header{height:86px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--line);gap:12px}header .eyebrow{font-size:12px;color:var(--muted);letter-spacing:.11em;text-transform:uppercase}.controls{display:flex;align-items:center;gap:17px;font-size:12px}.controls button{background:none;border:0;color:var(--muted);padding:5px}
article{max-width:1040px;margin:auto}section{padding-top:34px;animation:appear .16s ease}section[hidden]{display:none!important}h1{font-size:clamp(26px,3.1vw,43px);line-height:1.22;letter-spacing:-.025em;margin:17px 0 15px;font-weight:650}h2{font-size:26px;line-height:1.4;margin:0 0 23px;font-weight:620}h3{font-size:20px;line-height:1.5;margin:36px 0 12px;font-weight:620}p{margin:15px 0}strong{font-weight:650}.intro{color:var(--muted);font-size:14px;margin-bottom:27px}.chapter{font-size:11px;letter-spacing:.13em;color:var(--green);margin-bottom:14px}
.metrics{display:grid;grid-template-columns:repeat(3,1fr);border-top:1px solid var(--line);border-bottom:1px solid var(--line);margin:28px 0 31px;padding:22px 0;gap:20px}.metric+.metric{border-left:1px solid var(--line);padding-left:22px}.metric b{font-weight:500;font-size:32px;line-height:1.2;font-variant-numeric:tabular-nums;color:var(--green);display:block}.metric span{display:block;font-size:12px;color:var(--muted);margin-top:9px;line-height:1.5}
.table-wrap{overflow-x:auto;border:1px solid var(--line);border-radius:6px;margin:25px 0;background:#fff}table{width:100%;border-collapse:collapse;min-width:580px;font-size:14px;line-height:1.7}th,td{padding:13px 16px;text-align:left;vertical-align:top;border-bottom:1px solid #e7e8e2}th{background:#eef0e9;color:#3e574a;font-size:12px;font-weight:650}tr:last-child td{border-bottom:0}td code{font-size:12px}code{font-family:'SFMono-Regular',Consolas,monospace;font-size:.88em;overflow-wrap:anywhere;background:#e9ece5;border-radius:3px;padding:1px 4px}pre{overflow:auto;background:#e9ece5;border-left:3px solid #54846b;padding:18px;line-height:1.7}pre code{padding:0}img{max-width:100%;height:auto}p:has(>img){background:white;border:1px solid var(--line);border-radius:6px;padding:14px;margin:28px 0}
.pagination{display:flex;justify-content:space-between;align-items:center;gap:14px;margin-top:40px;padding-top:22px;border-top:1px solid var(--line)}.pagination button{border:1px solid #c3cec2;border-radius:5px;background:white;padding:8px 18px;color:var(--green);font-size:13px}.pagination button:disabled{opacity:.35;cursor:default}.pagination output{font-size:12px;letter-spacing:.12em;color:var(--muted)}.exports{display:flex;flex-wrap:wrap;gap:9px;margin:20px 0}.exports button{border:1px solid #c3cec2;border-radius:4px;background:white;color:var(--green);font-size:12px;padding:8px 12px}
@keyframes appear{from{opacity:.4}to{opacity:1}}@media(prefers-reduced-motion:reduce){section{animation:none}}
@media(min-width:1600px){main{margin-left:calc(246px + (100vw - 1600px)/2)}}
@media(max-width:1050px){aside{width:209px;padding:25px 16px}main{margin-left:209px;padding:0 28px 36px}.brand{font-size:16px}.controls{gap:10px}header .eyebrow{letter-spacing:.02em}}
@media(max-width:740px){aside{position:sticky;top:0;width:100%;height:auto;padding:11px 17px;gap:10px}.brand{font-size:15px}.brand img{width:27px;height:27px}.side-note,.side-bottom{display:none}nav{display:flex;gap:5px;overflow:auto;scrollbar-width:none}nav button{flex-shrink:0;padding:7px 9px;font-size:12px;gap:7px}main{margin:0;padding:0 20px 25px}header{height:57px}header .eyebrow{font-size:10px}.controls{font-size:11px}body{font-size:15px;line-height:1.85}section{padding-top:25px}h2{font-size:23px}h3{font-size:19px}h1{font-size:30px}.metrics{gap:10px;padding:17px 0}.metric+.metric{padding-left:10px}.metric b{font-size:26px}.metric span{font-size:10px}.table-wrap{margin:21px 0}p:has(>img){padding:4px}.chapter{font-size:10px}}
@media print{aside,header,.pagination,.exports{display:none}main{margin:0;padding:0;max-width:none}section,section[hidden]{display:block!important;break-before:page;padding-top:0}section:first-child{break-before:auto}body{background:white;font-size:10pt}h1{font-size:25pt}h2{font-size:19pt}h3{font-size:13pt}.table-wrap{overflow:visible;border:0}table{min-width:0;font-size:9pt}th,td{padding:6px 8px}p:has(>img){break-inside:avoid}a{color:inherit}section{animation:none}}
"""


def render(language, findings, pairs, links):
    cn = language == "zh-CN"
    markdown = (ROOT / ("README.zh-CN.md" if cn else "README.md")).read_text(encoding="utf-8")
    chunks = re.split(r"^## ", markdown, flags=re.M)[1:]
    names = ["结论", "执行用时", "测量与数据", "实验结构", "实现顺序", "来源与重算"] if cn else ["Findings", "Execution", "Measurements", "Experiment model", "Implementation", "Sources"]
    sections = []
    for index, chunk in enumerate(chunks):
        body = markdown2.markdown("## " + chunk, extras=["tables", "fenced-code-blocks"])
        body = body.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")
        for filename in ("timing.svg", "spectra.svg", "acquisition.svg"):
            data = base64.b64encode((ROOT / filename).read_bytes()).decode()
            body = body.replace(f'src="{filename}"', f'src="data:image/svg+xml;base64,{data}"')
        body = re.sub(r'href="([^"#:]*)"', lambda m: f'href="{REPOSITORY}{m[1]}"', body)
        hero = ""
        if index == 0:
            hero = f'<div class="chapter">LABORATORY NOTES · 2026.11.05</div><h1>{"IOP 实验反馈分析" if cn else "IOP laboratory feedback"}</h1>'
            hero += f'<p class="intro">IOP Runtime 0.8.4 · Windows 11<br>CETC 3672B · GW Instek GPP-4323</p>'
            metrics = [("514", "逐一配对的双向谱" if cn else "Matched spectral pairs"),
                       ("+34.0%", "完整任务的额外用时" if cn else "Longer total task time"),
                       ("19,339", "单步实验记录" if cn else "Single-operation runs")]
            hero += '<div class="metrics">' + ''.join(f'<div class="metric"><b>{v}</b><span>{t}</span></div>' for v,t in metrics) + '</div>'
        if index == 5:
            body += '<div class="exports">' + ''.join(f'<button data-export="{key}">{label}</button>' for key, label in
                (("findings", "下载统计 JSON" if cn else "Download findings JSON"),
                 ("spectrum_pairs", "下载逐谱 CSV" if cn else "Download spectra CSV"),
                 ("measurement_operations", "下载测量关联 CSV" if cn else "Download measurement links CSV"))) + '</div>'
        sections.append(f'<section id="chapter-{index+1}" {"" if index==0 else "hidden"}>{hero}{body}</section>')
    logo = Path(__file__).resolve().parents[3] / "src/ai4instruments/iop/ui/mark.svg"
    logo_uri = "data:image/svg+xml;base64," + base64.b64encode(logo.read_bytes()).decode()
    title = "IOP 实验反馈分析" if cn else "IOP laboratory feedback analysis"
    bundle = json.dumps({"findings": findings, "spectrum_pairs": pairs, "measurement_operations": links}, ensure_ascii=False).replace("</", "<\\/")
    nav = ''.join(f'<button data-chapter="{i}" {"aria-current=page" if i==0 else ""}><span>{i+1:02}</span>{html.escape(n)}</button>' for i,n in enumerate(names))
    script = """
const pages=[...document.querySelectorAll('section')],buttons=[...document.querySelectorAll('[data-chapter]')];let current=0;
function show(n,scroll=true){current=Math.max(0,Math.min(pages.length-1,n));pages.forEach((p,i)=>p.hidden=i!==current);buttons.forEach((b,i)=>{if(i===current)b.setAttribute('aria-current','page');else b.removeAttribute('aria-current')});document.querySelector('#counter').value=String(current+1).padStart(2,'0')+' / 06';document.querySelector('#previous').disabled=current===0;document.querySelector('#next').disabled=current===pages.length-1;history.replaceState(null,'','#'+(current+1));if(scroll)window.scrollTo({top:0});}
buttons.forEach(b=>b.onclick=()=>show(+b.dataset.chapter));document.querySelector('#previous').onclick=()=>show(current-1);document.querySelector('#next').onclick=()=>show(current+1);document.querySelector('#print').onclick=()=>window.print();
document.addEventListener('keydown',e=>{if(e.target.closest('button,a,input,textarea,select'))return;if(e.key==='ArrowRight')show(current+1);if(e.key==='ArrowLeft')show(current-1)});show((Number(location.hash.slice(1))||1)-1,false);
const embedded=JSON.parse(document.querySelector('#iop-laboratory-data').textContent);
for(const b of document.querySelectorAll('[data-export]'))b.onclick=()=>{const key=b.dataset.export,value=embedded[key];let text,name,type;if(key==='findings'){text=JSON.stringify(value,null,2);name='findings.json';type='application/json'}else{const fields=[...new Set(value.flatMap(Object.keys))];const quote=x=>'"'+String(x??'').replaceAll('"','""')+'"';text=[fields.map(quote).join(','),...value.map(r=>fields.map(k=>quote(r[k])).join(','))].join('\\r\\n');name=key==='spectrum_pairs'?'spectra.csv':'measurement-operations.csv';type='text/csv'}const url=URL.createObjectURL(new Blob([text],{type}));const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)};
"""
    document = f'''<!doctype html><html lang="{language}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><meta name="description" content="IOP Runtime 0.8.4 laboratory feedback: matched measurements, execution costs and experiment lifecycle."><style>{CSS}</style></head><body>
<aside><div class="brand"><img src="{logo_uri}" alt="">IOP Runtime</div><div class="side-note">{'实验记录 · 2026 年 11 月' if cn else 'LABORATORY · NOVEMBER 2026'}</div><nav aria-label="{'章节' if cn else 'Chapters'}">{nav}</nav><div class="side-bottom">AI4Instruments<br><a href="https://github.com/Cherish0925/AI4Instruments">GitHub ↗</a></div></aside>
<main><header><div class="eyebrow">{'真实实验 · 执行与测量' if cn else 'Execution & measurement'}</div><div class="controls"><a href="{REPOSITORY}{'report.en.html' if cn else 'report.zh-CN.html'}">{'English' if cn else '中文'}</a><button id="print">{'打印 / PDF' if cn else 'Print / PDF'}</button></div></header><article>{''.join(sections)}<div class="pagination"><button id="previous">{'上一章' if cn else 'Previous'}</button><output id="counter" aria-live="polite">01 / 06</output><button id="next">{'下一章' if cn else 'Next'}</button></div></article></main>
<script type="application/json" id="iop-laboratory-data">{bundle}</script><script>{script}</script></body></html>'''
    (ROOT / f"report.{language if cn else 'en'}.html").write_text(document, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    args = parser.parse_args()
    findings = json.loads((ROOT / "findings.json").read_text(encoding="utf-8"))
    with (ROOT / "spectra.csv").open(encoding="utf-8") as file:
        pairs = list(csv.DictReader(file))
    with (ROOT / "measurement-operations.csv").open(encoding="utf-8") as file:
        links = list(csv.DictReader(file))
    figures(Archive(args.archive), findings, pairs)
    for language in ("zh-CN", "en"):
        render(language, findings, pairs, links)
    print("Wrote 3 figures and 2 standalone reports.")


if __name__ == "__main__":
    main()
