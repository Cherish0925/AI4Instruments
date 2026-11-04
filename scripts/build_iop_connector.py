"""Build the standalone connector for existing IOP installations (no third-party Python dependencies)."""

from pathlib import Path
import ast
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "src/ai4instruments/iop/connector"


def build(output):
    names = ("__init__.py", "bridge.py", "shell.py")
    module = ast.parse((PACKAGE / "__init__.py").read_text(encoding="utf-8"))
    version = next(
        ast.literal_eval(node.value)
        for node in module.body
        if isinstance(node, ast.Assign)
        and isinstance(node.targets[0], ast.Name)
        and node.targets[0].id == "VERSION"
    )
    output.mkdir(parents=True, exist_ok=True)
    target = output / f"IOP-Connect-{version}.zip"
    root = "IOP-Connect-" + version + "/"
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        for name in names:
            archive.write(PACKAGE / name, root + "connector/" + name)
        archive.write(ROOT / "iop/connect/skills/iop-lab/SKILL.md", root + "connector/SKILL.md")
        for name in ("README.md", "README.zh-CN.md", "guide.en.html", "guide.zh-CN.html"):
            archive.write(ROOT / "iop/connect" / name, root + name)
        for name in ("LICENSE", "LICENSE-docs.md"):
            archive.write(ROOT / name, root + name)
        archive.writestr(
            root + "install.py", 'from connector import main\n\nif __name__ == "__main__":\n    main()\n'
        )
    return target


if __name__ == "__main__":
    print(build(ROOT / "release"))
