# DemoCaP project website

Project page for **DemoCaP: One-Shot Learning from Demonstrations with Code-as-Policy Generation**, by Ege Caglar and Maya Cakmak, University of Washington, Seattle.

Website: https://egecaglar.github.io/democap-corl-late-breaking/

## Preview

Open `index.html` directly, or run:

```bash
python3 -m http.server 8765 --bind 127.0.0.1
```

Visit http://127.0.0.1:8765. The site is static and needs no installation or JavaScript build step.

## Publishing

The `Publish website` GitHub Actions workflow runs on website changes pushed to `master`, or through **Run workflow** in Actions. GitHub Pages must use **GitHub Actions** as its publishing source.

`scripts/build_site.py` creates `_site/` from `index.html`, `.nojekyll`, and the local assets referenced by the page and its CSS. Only `_site/` is uploaded for deployment. Private editing/review folders, Git metadata, documentation, unused assets, and scripts are never part of that bundle.

`text-editor/` and `video-review/` are private local workspaces ignored by Git. They must not be committed or published.

## Editing and result figures

- `index.html`: page copy and video comparisons.
- `static/css/index.css`: styles.
- `static/js/index.js`: paired playback, example tabs, and chart filtering.
- `static/images/method.svg`: method diagram.
- `static/data/results.json`: generalization and direct-demo ablation data, transcribed from the supplied figures.
- `static/data/method-comparison-source.tex`: source table for all 84 method-comparison values and provenance markers.

To regenerate the 17 SVG charts, downloadable PDF collection, and CSV data, install Matplotlib and run:

```bash
python3 scripts/build_results.py
```

The method-comparison and generalization figures report different sample counts and some different success rates; the page displays them separately. The chart generator preserves source values, including regressions. Source PDFs are included alongside the website.

## Attribution

Adapted from [Academic Project Page Template](https://github.com/eliahuhorwitz/Academic-project-page-template), which builds on [Nerfies](https://nerfies.github.io/). Website template license: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
