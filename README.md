A simple action scanner made to find which repositories use a certain action, and extract the contributors.

### Usage

This script uses uv as a package manager.

Run it with `uv run main`, and enter the name of the action you are searching for when prompted.

### Development

This script could be expanded in a variety of ways, the first that come to mind are:

- Extract data from the mandatory "SUPPORT.md" instead of the list of contributors.
- Possibly include an email integration allowing to send a communication to the extracted list.
- Add a dry-run function.

