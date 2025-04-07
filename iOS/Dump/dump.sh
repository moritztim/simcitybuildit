#!/usr/bin/env bash
# echo "Read the script before running it" ; exit 1

# Replace the following paths with your own
project_root="$HOME/Projects/simcitybuildit_fork"
source="$HOME/Documents/SimCity.app"
ios_id="05B30DEF-13B1-45C6-84C6-4804E74D91DD"
ios_root="private/var/containers/Bundle/Application/$ios_id/SimCity.app"
target="$project_root/iOS/Dump"
index="$project_root/iOS/files.csv"

replicate() {
	# Remove leading './'
	local entry=${1#./}
	local target_entry="$target/$ios_root/$entry"

	if [ -d "$entry" ]; then
		echo "Creating directory $entry"
		mkdir -p "$target_entry"
		touch "$target_entry/.gitkeep"
		return
	fi

	echo "Replicating $file"

	local source_file="$source/$file"
	local target_file="$target_entry"

	# copy file metadata
	touch --reference "$source_file" "$target_file"
	# gitkeep files only needed in empty directories
	rm "$(dirname "$target_file")/.gitkeep" 2>/dev/null
}


pushd $source
for file in $(find); do
   replicate "$file"
done

python $project_root/iOS/Dump/index.py "$project_root/iOS/files.csv" "$target/$ios_root"
popd
