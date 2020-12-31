
# Tidal Bot
## Custom Commands

Custom commands are used as a way for server managers to add commands that can be triggered by other users that have a custom response.

The command prefix for custom commands is a twice iterated normal prefix. This means that if your server prefix is `!`, then your custom command prefix is `!!`.

### Set Up

#### Adding a custom command

`!customcommand set <name> <response>`

**name** The name of the custom command you wish to create.

**response** The response of the custom command.

**Note:** This can be used to replace the response of an existing command


#### Deleting a custom command

`!customcommand delete <name>`

**name** The name of the custom command to delete.


#### List all custom commands

`!customcommand list`


#### Search for a command
`!customcommand search <name>`

**name** The name of the custom command to search for.


### Variables
*Variables* are strings of text that are automatically replaced when a command is ran.

**Usage:** `${name}`, where *name* is replaced with one of the variable names below.

#### Basic Variables
Basic variables require no parameters.

| Variable Name | Replacement | Example |
|---------------|-------------|---------|
| author | Author name | MiningMark48 |
| author id | Author id | 138819223932633088 |
| channel | Name of channel message was sent from | #general |
| command_key | Prefix to trigger commands | ! |
| server_name | Server name | Tidal Wave |
| server_id | Server id | 138819614275665920 |

#### Advanced Variables
Advanced variables take in parameters that responds with a dynamic output.

| Variable Name |  Replacement | In Example | Out Example |
|---------------|--------------|------------|-------------|
| rand | Random number between two values | ${rand:1-100} | 42 |
| randlist | Random item from list | ${randlist:yes\|no\|maybe} | yes |


### Examples
| Command Name | Command | Text Example |
|--------------|---------|--------------|
| hello | customcommand set hello Hello, World!   | Hello, World! |
| chan | customcommand set chan You are speaking in ${channel}. | You are speaking in #general. |
| dice | customcommand set dice Dice Roll: ${rand:1-6} | Dice Roll: 3