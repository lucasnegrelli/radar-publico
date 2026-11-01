"""Sincroniza dados/ (Parquet) com o dataset privado no Hugging Face.
Uso: python sync_hf.py subir [pasta_local pasta_remota]   |   python sync_hf.py baixar pasta_remota pasta_local
Lê HF_TOKEN do ambiente ou do .env. Repo: HF_REPO (padrão propagang/radar-publico-dados)."""
import os, sys, pathlib
from huggingface_hub import HfApi, snapshot_download

RAIZ = pathlib.Path(__file__).parent.parent
env = RAIZ / ".env"
if "HF_TOKEN" not in os.environ and env.exists():
    for l in env.read_text(encoding="utf-8").splitlines():
        if l.startswith("HF_TOKEN="):
            os.environ["HF_TOKEN"] = l.split("=", 1)[1].strip()
REPO = os.environ.get("HF_REPO", "propagang/radar-publico-dados")
api = HfApi(token=os.environ["HF_TOKEN"])
api.create_repo(REPO, repo_type="dataset", private=True, exist_ok=True)

cmd = sys.argv[1] if len(sys.argv) > 1 else "info"
if cmd == "subir":
    local = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else RAIZ / "dados" / "cnpj")
    remoto = sys.argv[3] if len(sys.argv) > 3 else "cnpj/" + os.environ.get("SNAPSHOT", "atual")
    api.upload_folder(repo_id=REPO, repo_type="dataset", folder_path=str(local), path_in_repo=remoto,
                      allow_patterns=["*.parquet", "*.json", "*.md"], commit_message=f"atualiza {remoto}")
    print("enviado:", local, "->", REPO + "/" + remoto)
elif cmd == "baixar":
    snapshot_download(repo_id=REPO, repo_type="dataset", allow_patterns=[sys.argv[2] + "/*"], local_dir=sys.argv[3])
    print("baixado em", sys.argv[3])
else:
    info = api.repo_info(REPO, repo_type="dataset")
    print("repo:", REPO, "| privado:", info.private)
