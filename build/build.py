'''
    生成资源清单 res_info.json

    python build/build.py
'''
from pathlib import Path
from ayaka import ResInfo, ResItem, get_file_hash


def get_ps(path: Path):
    if path.is_dir():
        ps: list[Path] = []
        for p in path.iterdir():
            ps.extend(get_ps(p))
        return ps
    return [path]


if __name__ == "__main__":
    ROOT_PATH = Path(".").parent
    path = ROOT_PATH / "data"/"ayaka_games"
    AUTHOR = "bridgeL"
    REPO = "ayaka_games"
    BRANCH = "master"
    res_info = ResInfo(
        base=f"https://ghproxy.com/https://raw.githubusercontent.com/{AUTHOR}/{REPO}/{BRANCH}/data/ayaka_games",
        items=[
            ResItem(
                path="/".join(p.relative_to(path).parts),
                hash=get_file_hash(p)
            )
            for p in get_ps(path)
            if p.suffix in [".txt", ".json"] and p.stem != "res_info"
        ]
    )

    path = ROOT_PATH / "res_info.json"
    with path.open("w+", encoding="utf8") as f:
        f.write(res_info.json(ensure_ascii=False, indent=4))
