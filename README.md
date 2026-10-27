# Begone: Blocking List :fr:

This repository contains blocking lists of unwanted numbers for France,
to be used with the [Begone][begone-app] application on iOS.

## Prerequisites

Before you begin, ensure you have installed the [Begone][begone-app]
application on your iPhone. Once the application is installed, launch it
and follow the instructions to activate it as a call blocking application
on iOS.

## Installation

Open [this page](#installation) on your iPhone and follow the instructions
below:

1. Long press on the link of the desired list below and select
   **Download Linked File**.

   <!-- lists:start -->
   - [Spam Numbers](https://raw.githubusercontent.com/Fluyd-Cloud/Begone/refs/heads/main/dist/begone-fr-demarchage.xml) (recommended)
   - [VOIP Numbers](https://raw.githubusercontent.com/Fluyd-Cloud/Begone/refs/heads/main/dist/begone-fr-voip.xml)
     - [OnOff Numbers](https://raw.githubusercontent.com/Fluyd-Cloud/Begone/refs/heads/main/dist/begone-fr-onoff.xml)
     - [Ubicentrex Numbers](https://raw.githubusercontent.com/Fluyd-Cloud/Begone/refs/heads/main/dist/begone-fr-ubicentrex.xml)
     - [BJT Partners Numbers](https://raw.githubusercontent.com/Fluyd-Cloud/Begone/refs/heads/main/dist/begone-fr-bjt.xml)
     - [Kavkom Numbers](https://raw.githubusercontent.com/Fluyd-Cloud/Begone/refs/heads/main/dist/begone-fr-kavcom.xml)
     - [Destiny Numbers](https://raw.githubusercontent.com/Fluyd-Cloud/Begone/refs/heads/main/dist/begone-fr-destiny.xml)
     - [Spartel Numbers](https://raw.githubusercontent.com/Fluyd-Cloud/Begone/refs/heads/main/dist/begone-fr-spartel.xml)
     - [Get & Go Telecom Numbers](https://raw.githubusercontent.com/Fluyd-Cloud/Begone/refs/heads/main/dist/begone-fr-getandgo.xml)
   - [Prepaid Numbers](https://raw.githubusercontent.com/Fluyd-Cloud/Begone/refs/heads/main/dist/begone-fr-prepaid.xml)
     - [Lyca Numbers](https://raw.githubusercontent.com/Fluyd-Cloud/Begone/refs/heads/main/dist/begone-fr-lyca.xml)
   - [Complete List](https://raw.githubusercontent.com/Fluyd-Cloud/Begone/refs/heads/main/dist/begone-fr-full.xml)
   <!-- lists:end -->

2. Open the Begone application and select **Import New Numbers**.

3. Select **Files**.

4. Import the file you just downloaded.

## Contribution

### Setting Up the Development Environment

1. Install [uv](https://docs.astral.sh/uv/), then create the virtual
   environment and install the dependencies.

   ```bash
   make init
   ```

2. Activate the virtual environment.

   ```bash
   source .venv/bin/activate
   ```

### Adding an Operator

1. Find the ARCEP operator code (mnemo) from one of its numbers:

   ```bash
   begone lookup "01 87 68 68 87"
   # GETG  +33187680000 - +33187689999
   ```

2. In `data/numbers.yaml`, add the operator under `operators` with its
   `mnemos` (or explicit `numbers` patterns, `#` being any digit), and a list
   under `lists` for its new tag.

3. Run `make build` to fetch the ARCEP ranges and regenerate the `dist/` lists
   and the download links of this README.

4. Bump the version with `begone bump --structural`.

Anyone can also [report an operator](https://github.com/Fluyd-Cloud/Begone/issues/new?template=operator.yml).

### Checks

Run `make lint test check` before opening a pull request. The CI runs the same
checks on every pull request.

### Updates and Releases

- Every week, the `Refresh lists` workflow regenerates the lists from the
  latest ARCEP data and opens a pull request with a summary of the changes.
- The `begone.version` file holds the version of the lists (first line, bumped
  on structural changes such as a new operator) and the build number (second
  line, bumped on every update).
- When a new version reaches `main`, the `Release` workflow tags it and
  publishes a GitHub release with the lists.

[begone-app]: https://apps.apple.com/fr/app/id1596818195
