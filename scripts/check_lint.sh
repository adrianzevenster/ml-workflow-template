if python -m flake8 scripts tests; then
  echo "No lint errors!"
else
  echo "Lint errors detected"
  exit 1
fi