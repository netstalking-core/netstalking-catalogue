if [ "${TRAVIS_EVENT_TYPE}" = "push" ] && [ "${TRAVIS_BRANCH}" = "master" ]; then

  git config --global user.email "travis@travis-ci.org"
  git config --global user.name "Travis CI"

  git add README.*.md

  git commit --message "Travis build: ${TRAVIS_BUILD_NUMBER}"

  git push https://vechur:${GH_TOKEN}@github.com/netstalking-core/netstalking-catalogue.git HEAD:master

fi
