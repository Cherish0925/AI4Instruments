"""Render the two offline HTML guides from the connector's English and Chinese installation instructions."""

from html import escape as esc
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://github.com/Cherish0925/AI4Instruments"
CSS = """
:root{color-scheme:light;--ink:#172c33;--muted:#50626b;--line:#cddad7;--paper:#fafbf8;--teal:#126354;--wash:#e6f3ec}
[hidden]{display:none!important}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.65 system-ui,-apple-system,"Segoe UI",sans-serif}a{color:var(--teal);text-underline-offset:.22em}
header{border-bottom:1px solid var(--line);padding:1rem max(5%,calc((100% - 76rem)/2));display:flex;justify-content:space-between;gap:1rem;align-items:center}header strong{letter-spacing:.02em;white-space:nowrap}header a{font-size:.83rem}
main{max-width:76rem;margin:2.7rem auto;padding:0 2rem;display:grid;grid-template-columns:12rem minmax(0,1fr);gap:3.4rem}
nav{align-self:start;position:sticky;top:2rem}nav a{display:flex;gap:.9rem;padding:.7rem .6rem;text-decoration:none;color:var(--muted);border-left:2px solid var(--line);font-size:.9rem}nav a[aria-current=page]{border-color:var(--teal);color:var(--teal);background:var(--wash);font-weight:650}nav span,.eyebrow{font:600 .67rem/1.6 ui-monospace,monospace;letter-spacing:.1em;color:var(--teal);align-self:center}
section{max-width:58rem;margin:0 0 3.7rem}h1,h2{margin:.3em 0 .65em;letter-spacing:-.035em;line-height:1.15}h1{font-size:clamp(2.15rem,4.8vw,4rem)}h2{font-size:clamp(1.7rem,3.3vw,2.9rem)}h3{margin:1.5rem 0 .4rem;font-size:1.08rem}p{max-width:76ch}figure{margin:1.8rem 0;padding:1.4rem;background:#eef3ef;border:1px solid var(--line);border-radius:.65rem}.flow{display:grid;grid-template-columns:1fr 2rem 1.15fr 2rem 1fr;align-items:center;gap:.3rem}.node{background:white;border:1px solid var(--line);padding:.8rem;border-radius:.3rem;min-width:0}.node b,.node small{display:block}.node small{font-size:.82rem;color:var(--muted)}.node.core{background:var(--teal);color:white}.node.core small{color:#e4f3ed}.arrow{text-align:center;color:var(--teal)}figcaption{font-size:.82rem;margin-top:1rem;color:var(--muted)}
table{width:100%;border-collapse:collapse;margin:1.5rem 0;font-size:.94rem}td,th{padding:.78rem .65rem;text-align:left;vertical-align:top;border-bottom:1px solid var(--line)}thead{background:var(--wash)}td:first-child{width:22%;font-weight:600}code{font: .85em/1.55 ui-monospace,monospace;overflow-wrap:anywhere;background:#eaf0ed;padding:.09em .22em;border-radius:.2rem}pre{padding:1rem;background:#193831;color:#edf7f1;border-radius:.4rem;white-space:pre-wrap}pre code{background:none;color:inherit}footer{max-width:76rem;border-top:1px solid var(--line);margin:2rem auto;padding:1rem 2rem;color:var(--muted);font-size:.82rem}.controls{display:flex;gap:1rem;justify-content:space-between}.controls button{background:white;border:1px solid var(--line);border-radius:.3rem;padding:.55rem .9rem;color:var(--ink);cursor:pointer}.controls button:disabled{visibility:hidden}
@media(max-width:760px){header{padding:.8rem 1rem}main{display:block;margin:1rem auto;padding:0 1rem}nav{position:static;display:flex;flex-wrap:wrap;margin-bottom:1.4rem;gap:.2rem}nav a{display:block;border:0;border-bottom:2px solid var(--line);padding:.32rem .45rem}nav span{display:none}.flow{grid-template-columns:1fr}.arrow{transform:rotate(90deg);line-height:1}td,th{padding:.5rem .35rem}footer{padding:1rem}}
@media print{header,nav,.controls,footer{display:none}main{display:block;margin:0;padding:0}section,section[hidden]{display:block!important;break-before:page;margin:0}section:first-child{break-before:auto}figure,tr{break-inside:avoid}}
"""
JS = """
const sections=[...document.querySelectorAll('article section')],tabs=[...document.querySelectorAll('nav a')],bar=document.querySelector('.controls'),buttons=[...bar.querySelectorAll('button')];
function show(){let i=sections.findIndex(s=>s.id===location.hash.slice(1));if(i<0)i=0;sections.forEach((s,k)=>{s.hidden=k!==i;tabs[k].toggleAttribute('data-current',k===i);if(k===i)tabs[k].setAttribute('aria-current','page');else tabs[k].removeAttribute('aria-current')});buttons[0].disabled=i===0;buttons[1].disabled=i===sections.length-1;bar.hidden=false;}
function move(n){const i=sections.findIndex(s=>!s.hidden)+n;if(sections[i])location.hash=sections[i].id;}
buttons[0].onclick=()=>move(-1);buttons[1].onclick=()=>move(1);addEventListener('hashchange',show);addEventListener('keydown',e=>{if(e.altKey||e.ctrlKey||e.metaKey)return;if(['PageUp','PageDown'].includes(e.key)){e.preventDefault();move(e.key==='PageUp'?-1:1)}});show();
"""


def html(md):
    return subprocess.check_output(
        ["pandoc", "--from=gfm", "--to=html5", "--wrap=none"], input=md, text=True
    )


def render(zh):
    folder = ROOT / "iop/connect"
    md = (folder / ("README.zh-CN.md" if zh else "README.md")).read_text(encoding="utf-8")
    heading, *chunks = re.split(r"^## ", md, flags=re.M)
    intro = heading.split("\n\n")[1]
    names = (
        ["工作方式", "选择连接", "安装与更新", "运行实验"]
        if zh
        else ["How it works", "Choose a connection", "Install and update", "Run an experiment"]
    )
    title = "把实验室接入研究系统" if zh else "Connect a research host to the lab"
    labels = (
        (
            ("研究系统", "人、Agent、研究程序"),
            ("IOP Runtime", "调度仪器，保存过程与结果"),
            ("实验平台", "物理仪器、仿真与计算"),
        )
        if zh
        else (
            ("Research host", "People, agents and programs"),
            ("IOP Runtime", "Schedules work and retains results"),
            ("Lab platform", "Instruments, simulation and computation"),
        )
    )
    role = (
        "平台负责人说明接线、样品和现场条件；Agent 把这些条件写成平台配置与实验程序；Runtime 按依赖和资源占用执行，保存每次操作与结果。已有配置可以直接复用。"
        if zh
        else "The operator supplies wiring, sample and site information. The agent turns it into platform settings and an experiment. The runtime schedules operations against those settings and keeps the results. Later sessions reuse the same laboratory."
    )
    caption = (
        "更换宿主或更新插件时，已接收的实验仍由同一台实验室服务执行。"
        if zh
        else "An accepted experiment stays with the same laboratory when its client changes or a plugin is updated."
    )
    diagram = (
        '<figure><div class="flow">'
        + '<span class="arrow" aria-hidden="true">→</span>'.join(
            '<div class="node '
            + ("core" if i == 1 else "")
            + '"><b>'
            + esc(a)
            + "</b><small>"
            + esc(b)
            + "</small></div>"
            for i, (a, b) in enumerate(labels)
        )
        + "</div><figcaption>"
        + caption
        + "</figcaption></figure>"
    )
    ids = ["overview", "connection", "installation", "experiment"]
    sections = [
        f'<section id="overview"><span class="eyebrow">IOP RUNTIME · 0.8.4</span><h1>{title}</h1>{html(intro)}{diagram}<h3>{("首次接入" if zh else "First connection")}</h3><p>{role}</p></section>'
    ]
    for i, chunk in enumerate(chunks, 1):
        first, body = chunk.split("\n", 1)
        sections.append(
            f'<section id="{ids[i]}"><span class="eyebrow">{i + 1:02} / 04</span><h2>{esc(first)}</h2>{html(body)}</section>'
        )
    language = "English" if zh else "中文"
    other = "guide.en.html" if zh else "guide.zh-CN.html"
    nav = "".join(
        f'<a href="#{ids[i]}"><span>{i + 1:02}</span>{esc(n)}</a>' for i, n in enumerate(names)
    )
    page = f"""<!doctype html><html lang="{"zh-CN" if zh else "en"}"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title} · IOP Runtime</title><style>{CSS}</style><header><strong>AI4Instruments / IOP</strong><a href="{other}" hreflang="{"en" if zh else "zh-CN"}">{language}</a></header><main><nav aria-label="{"章节" if zh else "Sections"}">{nav}</nav><article>{"".join(sections)}<div class="controls" hidden><button>{"← 上一节" if zh else "← Previous"}</button><button>{"下一节 →" if zh else "Next →"}</button></div></article></main><footer><a href="{BASE}/releases/latest">{"下载软件" if zh else "Download IOP"}</a> · <a href="{BASE}/tree/main/iop/connect">{"源代码与安装说明" if zh else "Source and instructions"}</a></footer><script>{JS}</script></html>"""
    (folder / ("guide.zh-CN.html" if zh else "guide.en.html")).write_text(page, encoding="utf-8")


if __name__ == "__main__":
    render(False)
    render(True)
