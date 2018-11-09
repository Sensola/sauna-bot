# sauna-bot

## Running

First, make `config.yaml`. Set HOAS credentials, as well as Telegram token.
Then, just `make run`.

## Developing

Use `make format` to format your code with Black and `make typecheck` to typececk  and `make test` to run tests before committing
(there is also shorthand `make testall`)

We have travis set up for running tests, typechecking and checking style. 
Pushing to master is not allowed, create a pull request.
