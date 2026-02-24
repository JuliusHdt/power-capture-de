# TODO

## v0 – Skeleton (today)
- [ ] Repo initialized + first commit
- [ ] Folder structure created (data_raw/, data/, notebooks/, outputs/charts/)
- [ ] Add README.md, TODO.md, .gitignore

## v0.1 – Ingest & Clean
- [ ] Create notebooks/01_ingest_clean.ipynb
- [ ] Load raw files (price, wind, solar, load)
- [ ] Parse timestamps + timezone placeholder
- [ ] Merge to common hourly index
- [ ] Sanity checks (missing %, min/max, duplicates)
- [ ] Save cleaned dataset to data/clean.parquet (or CSV)

## v0.2 – First output
- [ ] Plot 1-week price timeseries
- [ ] Save PNG to outputs/charts/
- [ ] Commit “v0 clean dataset + first plot”
