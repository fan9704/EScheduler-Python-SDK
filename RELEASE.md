# Release Workflow

---

透過 GitHub Actions 自動發布 Package 到 PyPI

## 🚀 工作原理

1. cz bump
    - 自動讀取 pyproject.toml 的 version
    - 根據 commit 訊息（Conventional Commits: feat/fix/breaking change）決定是 patch/minor/major bump
    - 更新 pyproject.toml → commit → 打 tag
2. GitHub Action
   - 把新的 commit & tag push 回 main
   - 打包 (python -m build)
   - 上傳到 PyPI (twine upload)

## 運作方式

1. 本地 commit → pre-commit hook 檢查 commit message
2. push 到 main → Action 觸發
3. cz bump → 依 commit 決定新版本號
4. 自動更新 pyproject.toml + CHANGELOG.md
5. commit + tag 新版本
6. 打包 & 上傳到 PyPI
7. 建立 GitHub Release，內容來自 CHANGELOG.md