if [ "${TRAVIS_EVENT_TYPE}" = "pull_request" ]; then
  for md_file in $(ls -1 README.*.md); do
    cp ${md_file} ${md_file}.pre
  done
fi
