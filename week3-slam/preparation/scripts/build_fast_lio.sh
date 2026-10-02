#!/usr/bin/env bash
# Build the FAST-LIO2 version used in week 3 into a colcon workspace outside the repository.
set -eo pipefail
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
prep_dir="$(cd -- "$script_dir/.." && pwd)"
source "$script_dir/env.sh"

FAST_LIO_REPO=https://github.com/hku-mars/FAST_LIO.git
FAST_LIO_BRANCH=ROS2
FAST_LIO_COMMIT=a4743b095409588842a5b30ddfa27e29d2f99164  # 2025-01-15, "Merge pull request #381"
src="$FASTLIO_WS/src"
fast_lio="$src/FAST_LIO"
patch="$prep_dir/patches/fast_lio_jazzy_cxx17.patch"

mkdir -p "$src"
if [[ ! -d "$fast_lio/.git" ]]; then
    git clone --branch "$FAST_LIO_BRANCH" "$FAST_LIO_REPO" "$fast_lio"
fi
if [[ "$(git -C "$fast_lio" rev-parse HEAD)" != "$FAST_LIO_COMMIT" ]]; then
    git -C "$fast_lio" fetch origin "$FAST_LIO_BRANCH"
    git -C "$fast_lio" checkout --quiet "$FAST_LIO_COMMIT"
fi
git -C "$fast_lio" submodule update --init --recursive

# Upstream forces C++14, but ROS 2 Jazzy's rclcpp headers need C++17.
if git -C "$fast_lio" apply --reverse --check "$patch" 2>/dev/null; then
    printf 'C++17 패치가 이미 적용되어 있습니다.\n'
else
    git -C "$fast_lio" apply "$patch"
    printf 'C++17 패치를 적용했습니다.\n'
fi

# FAST_LIO only needs the Livox message headers; the real driver would also need Livox-SDK2.
rm -rf "$src/livox_ros_driver2"
cp -r "$prep_dir/third_party/livox_ros_driver2" "$src/livox_ros_driver2"

cd "$FASTLIO_WS"
colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release
printf '\n빌드 완료: %s\n새 터미널에서 source scripts/env.sh 후 scripts/check_environment.sh를 실행하세요.\n' "$FASTLIO_WS"
