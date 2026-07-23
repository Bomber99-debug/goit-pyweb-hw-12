
format:
    @black .

isort:
    @isort .

optimise-imports:
    @autoflake --recursive --in-place --remove-all-unused-imports --ignore-init-module-imports .

pretty: optimise-imports isort format