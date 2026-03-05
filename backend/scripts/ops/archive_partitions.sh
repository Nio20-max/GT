#!/usr/bin/env bash
set -euo pipefail

# Archives partition export files into timestamped compressed bundles with checksums.
ts="$(date -u +"%Y%m%dT%H%M%SZ")"
source_dir="${GT_ARCHIVE_SOURCE_DIR:-/mnt/website/GT/exports/live_partitions}"
archive_root="${GT_ARCHIVE_ROOT_DIR:-/mnt/website/GT/exports/archive}"
retention_days="${GT_ARCHIVE_RETENTION_DAYS:-14}"

mkdir -p "${archive_root}"
out_dir="${archive_root}/${ts}"
mkdir -p "${out_dir}"

manifest="${out_dir}/partition-archive-manifest.json"
tmp_manifest="${manifest}.tmp"

if [[ ! -d "${source_dir}" ]]; then
	printf '{"status":"no-source","time":"%s","source":"%s","archived":0}\n' "${ts}" "${source_dir}" >"${manifest}"
	echo "archive source not found; wrote ${manifest}"
	exit 0
fi

archived=0
{
	printf '{"status":"ok","time":"%s","source":"%s","archivedFiles":[' "${ts}" "${source_dir}"
	first=1
	while IFS= read -r -d '' file; do
		rel_path="${file#${source_dir}/}"
		safe_name="${rel_path//\//_}"
		tar_path="${out_dir}/${safe_name}.tar.gz"
		checksum_path="${tar_path}.sha256"

		tar -czf "${tar_path}" -C "${source_dir}" "${rel_path}"
		sha256sum "${tar_path}" | awk '{print $1}' >"${checksum_path}"

		if [[ ${first} -eq 0 ]]; then
			printf ','
		fi
		first=0
		printf '{"source":"%s","archive":"%s","sha256File":"%s"}' "${rel_path}" "$(basename "${tar_path}")" "$(basename "${checksum_path}")"
		archived=$((archived + 1))
	done < <(find "${source_dir}" -type f -print0)
	printf '],"count":%d}\n' "${archived}"
} >"${tmp_manifest}"

mv "${tmp_manifest}" "${manifest}"

find "${archive_root}" -mindepth 1 -maxdepth 1 -type d -mtime +"${retention_days}" -exec rm -rf {} +

echo "archived ${archived} files into ${out_dir}"
